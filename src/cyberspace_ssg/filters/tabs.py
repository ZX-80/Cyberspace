"""
Support for tabs. Example usage:

::: tabset
### First tab

Sentences.

{.active}
### Second tab

Other sentences.
:::
"""

import itertools

import dominate.tags as dom
import panflute as pf

tab_counter = itertools.count()
active_child: dict[str, str] = {}


def find_tabsets(elem: pf.Element, _doc: pf.Doc) -> None:
    """Uniquely mark tabsets."""
    if isinstance(elem, pf.Div) and "tabset" in elem.classes:
        elem.identifier = f"tabset-{next(tab_counter)}"
        for i, child in enumerate(
            child for child in elem.content if isinstance(child, pf.Div) and "section" in child.classes
        ):
            child.identifier = f"tabdiv-{next(tab_counter)}"
            if i == 0:
                active_child[elem.identifier] = child.identifier
            elif "active" in child.classes:
                active_child[elem.identifier] = child.identifier
                child.classes.remove("active")


def convert_tabsets(elem: pf.Element, _doc: pf.Doc) -> list[pf.Block] | None:
    """Convert a tabset div."""
    if (
        isinstance(elem, pf.Div)
        and "section" in elem.classes
        and isinstance(elem.parent, pf.Div)
        and "tabset" in elem.parent.classes
    ):
        # Get header text and remove element
        tab_title = pf.stringify(elem.content.pop(0))

        # Replace with HTML elements
        elem.classes.remove("section")
        tab_id = next(tab_counter)
        return [
            pf.RawBlock(
                str(
                    dom.input_(
                        type="radio",
                        id=f"tab-{tab_id}",
                        name=f"tabgroup-{elem.parent.identifier}",
                        checked=elem.identifier == active_child[elem.parent.identifier],
                    )
                )
            ),
            pf.RawBlock(text=str(dom.label(tab_title, id=elem.identifier, cls="tab-label", fr=f"tab-{tab_id}"))),
            pf.Div(*elem.content, classes=["tab-content"] + elem.classes),
        ]
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filters([find_tabsets, convert_tabsets], doc=doc)


if __name__ == "__main__":
    main()
