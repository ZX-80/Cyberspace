"""
Get document title. Example usage:

# Page Title
"""

import panflute as pf


def find_first_header(elem: pf.Element, doc: pf.Doc) -> None:
    """Set the title to the first header."""
    if (
        isinstance(elem, pf.Header)
        and elem.content
        and isinstance(string := elem.content[0], pf.Str)
        and "auto-title" not in doc.metadata
    ):
        doc.metadata["auto-title"] = string.text


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(find_first_header, doc=doc)


if __name__ == "__main__":
    main()
