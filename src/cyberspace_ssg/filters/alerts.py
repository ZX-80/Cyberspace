"""
Replicate alert divs from GitHub. Example usage:

::: note
This is a note
:::
"""

import panflute as pf

supported_alerts = {"note", "important", "warning", "tip", "caution"}


def convert_alert(elem: pf.Element, _doc: pf.Doc) -> pf.Div | None:
    """Wrap alerts in another div."""
    if isinstance(elem, pf.Div) and (note_type := set(elem.classes) & supported_alerts):
        class_name = next(iter(note_type))
        elem.classes.remove(class_name)
        return pf.Div(elem, classes=[class_name])
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(convert_alert, doc=doc)


if __name__ == "__main__":
    main()
