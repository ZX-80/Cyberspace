"""
Detect checkboxes. Pandoc should convert them, but it doesn't. Example usage:

- [ ] not done
- [X] task completed
"""

import panflute as pf

check_value = {"[ ]": False, "[X]": True, "[x]": True}
check_char = ["☐", "☒"]  # ☑


def style_task_list(elem: pf.Element, _doc: pf.Doc) -> pf.Div | None:
    """Mark task lists."""
    if (
        isinstance(elem, pf.BulletList)
        and elem.content
        and isinstance(item := elem.content[0], pf.ListItem)
        and item.content
        and isinstance(plain := item.content[0], pf.Plain)
        and plain.content
        and isinstance(string := plain.content[0], pf.Str)
        and string.text in check_value
    ):
        if isinstance(elem.parent, pf.Div) and len(elem.parent.content) == 1:
            elem.parent.classes.append("task-list")
        else:
            return pf.Div(elem, classes=["task-list"])
    return None


def convert_checkbox(elem: pf.Element, _doc: pf.Doc) -> pf.Plain | None:
    """Convert checkbox text."""
    if (
        isinstance(elem, pf.Plain)
        and isinstance(elem.parent, pf.ListItem)
        and len(elem.content) >= 2
        and isinstance(box := elem.content[0], pf.Str)
        and box.text in check_value
        and isinstance(elem.content[1], pf.Space)
    ):
        if checked := check_value[box.text]:
            return pf.Plain(pf.RawInline(check_char[checked]), pf.Space, pf.Strikeout(*elem.content[2:]))
        return pf.Plain(pf.RawInline(check_char[checked]), pf.Space, *elem.content[2:])
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filters([style_task_list, convert_checkbox], doc=doc)


if __name__ == "__main__":
    main()
