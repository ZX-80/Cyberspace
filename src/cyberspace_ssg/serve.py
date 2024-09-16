"""Serve a directory forever. Useful for development."""

import http.server
import signal
import socketserver
import sys
from pathlib import Path
from types import FrameType
from typing import Any, NoReturn

from .config import WEB_PATH, logger

PORT = 8000
"""The port to serve on."""


def signal_handler(_sig: int, _frame: FrameType | None) -> NoReturn:
    """Exit gracefully."""
    logger.info("Shutting down...")
    sys.exit(0)


class ExtensionHandler(http.server.SimpleHTTPRequestHandler):
    """Make html extensions optional."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=self.directory, **kwargs)

    def do_GET(self) -> None:
        """Add html extension if necessary."""
        path = Path(self.path.removeprefix("/"))
        if path.stem and not path.suffix and (self.directory / path.with_suffix(".html")).is_file():
            self.path += ".html"
        logger.debug(f"/{path} -> {self.path}")
        super().do_GET()

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        """Redirect to error page if available."""
        if (WEB_PATH / f"{code}.html").is_file():
            self.error_message_format = (WEB_PATH / f"{code}.html").read_text(encoding="utf-8")
        super().send_error(code, message)


def main(port: int | None = None, directory: Path | None = None) -> None:
    """Serve forever."""
    if directory is None:
        directory = WEB_PATH
    if port is None:
        port = PORT
    signal.signal(signal.SIGINT, signal_handler)
    handler = type("ExtensionHandler", (ExtensionHandler,), {"directory": directory})  # New class with directory info
    with socketserver.TCPServer(("", port), handler) as httpd:
        logger.info(f"Serving HTTP on port {port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
