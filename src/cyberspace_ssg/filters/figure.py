"""
Allow captions anywhere.

![Image](link)
^ image caption
"""

import panflute as pf

PRIORITY = 10
"""The filters execution priority (lower executes earlier)"""


def wrap_caption(elem: pf.Element, _doc: pf.Doc) -> pf.Figure | None:
    """Wrap elements in a figure if a caption is present."""
    if (
        isinstance(paragraph := elem.next, pf.Para)
        and elem.next.content
        and isinstance(string := elem.next.content[0], pf.Str)
        and string.text.startswith("^ ")
    ):
        string.text = string.text.removeprefix("^ ")
        del elem.parent.content[elem.index + 1]  # Remove the caption object
        figure = pf.Figure(
            elem,
            caption=pf.Caption(paragraph),
            classes=["center"] + getattr(elem, "classes", []),
            attributes=getattr(elem, "attributes", {}),
        )
        if hasattr(elem, "classes"):
            elem.classes = []
        if hasattr(elem, "attributes"):
            elem.attributes = {}
        return figure
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run document through some filters."""
    return pf.run_filter(wrap_caption, doc=doc)


if __name__ == "__main__":
    main()
