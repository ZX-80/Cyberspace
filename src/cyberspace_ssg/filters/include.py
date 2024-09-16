"""
Include documents in another document.

:{#include path="path/to/file"}
"""

from pathlib import Path
from typing import Any

import panflute as pf

from ..config import SOURCE_PATH, logger
from ..formats import from_extension
from .macros import macro_check


def include_action(elem: pf.Element, _doc: pf.Doc) -> Any | list[None] | None:
    """Insert a file where elem is."""
    if (span := macro_check(elem)) and span.identifier.lower() == "include":
        if "path" not in span.attributes:
            logger.error("Include macro has no path attribute.")
            return []

        # Get source text and format
        source_file = SOURCE_PATH / Path(span.attributes["path"])
        if not source_file.is_file():
            logger.error(f"Include macro has invalid path: {source_file}.")
            return []

        source_text = source_file.read_text("utf-8", errors="ignore")
        input_format = from_extension(source_file.suffix)

        # replace with elements
        return pf.convert_text(source_text, input_format=input_format)
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run document through some filters."""
    return pf.run_filter(include_action, doc=doc)


if __name__ == "__main__":
    main()
