"""Allows execution via cli or python -m."""

import argparse
import ast
import logging
from contextlib import suppress
from pathlib import Path
from typing import Any

from . import build, config, serve


def initialize_logging(log_level: int = logging.DEBUG) -> None:
    """Set up log outputs."""

    class ColorFormatter(logging.Formatter):
        """Add color to log levels."""

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

            color_codes = {
                logging.DEBUG: "1;30",
                logging.INFO: "36",
                logging.WARNING: "33",
                logging.ERROR: "1;31",
                logging.CRITICAL: "37;41",
            }

            self.color_format = {
                log_level: self._style._fmt.replace("%(levelname)s", f"\x1b[{color_code}m%(levelname)s\x1b[39;49m")
                for log_level, color_code in color_codes.items()
            }

        def format(self, record) -> str:
            # pylint: disable=protected-access
            self._style._fmt = self.color_format.get(record.levelno, self._style._fmt)
            return super().format(record)

    while config.logger.hasHandlers():  # Remove existing handlers
        config.logger.removeHandler(config.logger.handlers[0])

    config.logger.setLevel(log_level)
    terminal_logger = logging.StreamHandler()
    terminal_logger.setLevel(log_level)
    terminal_logger.setFormatter(
        ColorFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    )
    config.logger.addHandler(terminal_logger)


def process_define(key_val: str) -> tuple[str, Any]:
    """Process new definition."""
    key, has_value, value = key_val.partition("=")
    with suppress(ValueError, SyntaxError):
        value = ast.literal_eval(value)
    return key, value if has_value else True


def main() -> None:
    """Run subcommands."""
    parser = argparse.ArgumentParser(prog="cyberspace")
    parser.set_defaults(func=lambda _args: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-command help")

    # Shared arguments
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("-v", "--verbose", action="store_true", help="Displays debug information")
    base_parser.add_argument("-s", "--silent", action="store_true", help="Only display errors")
    base_parser.add_argument(
        "-D", "--define", type=process_define, default=[], metavar="key[=value]", action="append", help="Set config"
    )

    # create the parser for the "serve" command
    parser_serve = subparsers.add_parser("serve", help="serve http content", parents=[base_parser])
    parser_serve.add_argument("port", type=int, nargs="?", default=None, help="The network port to server on")
    parser_serve.add_argument("directory", type=Path, nargs="?", default=None, help="The path to serve")
    parser_serve.set_defaults(func=lambda args: serve.main(args.port, args.directory))

    # create the parser for the "build" command
    parser_build = subparsers.add_parser("build", help="generate html from source", parents=[base_parser])
    parser_build.add_argument(
        "source",
        type=lambda source: setattr(config, "SOURCE_PATH", Path(source)),
        nargs="?",
        default=None,
        help="The source files path",
    )
    parser_build.add_argument(
        "html",
        type=lambda source: setattr(config, "WEB_PATH", Path(source)),
        nargs="?",
        default=None,
        help="The HTML path / output path",
    )
    parser_build.set_defaults(func=lambda _args: build.main())

    # Initialize config and logging
    args = parser.parse_args()
    for attribute, value in args.define:
        setattr(config, attribute, value)
    initialize_logging(
        10 if hasattr(args, "verbose") and args.verbose else 30 if hasattr(args, "silent") and args.silent else 20
    )

    # Run subcommand
    args.func(args)


if __name__ == "__main__":
    main()
