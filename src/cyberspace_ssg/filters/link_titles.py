"""
Make titles links to themselves.
"""

import panflute as pf


def find_first_header(elem: pf.Element, _doc: pf.Doc) -> None:
    """Make titles links to themselves."""
    if (
        isinstance(elem, pf.Div)
        and "section" in elem.classes
        and elem.content
        and isinstance(header := elem.content[0], pf.Header)
    ):
        header.content = pf.ListContainer(pf.Link(*header.content, url=f"#{elem.identifier}"))


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(find_first_header, doc=doc)


if __name__ == "__main__":
    main()
