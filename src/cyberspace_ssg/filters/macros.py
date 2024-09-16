"""
Expand custom macros. Macros are of the form :{#name key=value}. Supported macros include:

# Table of Contents

Usage :{#toc}

This macro will be replaced by a small detail with the headers numbered.

# Metadata

Usage :{#metadata title="Title" date="2024-09-07" banner="image.png" type=index}

Provide information on page generation. Supports:

- title: The page title (has priority over the first header)
- date: The page creation date
- banner: The image to use as a banner
"""

from typing import cast

import dominate.tags as dom
import dominate.util as dom_util
import panflute as pf

from ..config import logger

TOC_DEPTH = (2, 2)
"""Start/stop header level to display"""


def remove_wrapper(elem: pf.Element, _doc: pf.Doc) -> None:
    """Strip wrapper attribute. Not sure what it is."""
    if hasattr(elem, "attributes") and "wrapper" in elem.attributes:
        del elem.attributes["wrapper"]


def build_json_toc(elem: pf.Element, doc: pf.Doc) -> None:
    """Build a short table of contents in JSON."""
    if not hasattr(doc, "json_toc"):
        doc.json_toc = {}

    if isinstance(elem, pf.Header) and isinstance(elem.parent, pf.Div) and TOC_DEPTH[0] <= elem.level <= TOC_DEPTH[1]:
        doc.json_toc[elem.parent.identifier] = pf.stringify(elem)


def build_toc(elem: pf.Element, doc: pf.Doc) -> None:
    """Build a full table of contents."""
    if not hasattr(doc, "toc"):
        doc.toc = pf.BulletList()

    if isinstance(elem, pf.Header) and isinstance(elem.parent, pf.Div):
        current_list = doc.toc
        current_index = [len(current_list.content) + 1]
        for _ in range(elem.level - 1):
            if len(current_list.content) == 0:  # Have at least one list item in list
                current_list.content.append(pf.ListItem())

            last_list_item = cast(pf.ListItem, current_list.content[-1])  # Last item is a list
            if len(last_list_item.content) == 0 or not isinstance(last_list_item.content[-1], pf.BulletList):
                last_list_item.content.append(pf.BulletList())

            current_list = cast(pf.BulletList, last_list_item.content[-1])
            current_index[-1] = max(1, current_index[-1] - 1)
            current_index.append(len(current_list.content) + 1)

        current_list.content.append(
            pf.ListItem(
                pf.Plain(pf.Str(f' {".".join(map(str, current_index))} ')),
                pf.RawBlock(str(dom.a(pf.stringify(elem), href=f"#{elem.parent.identifier}"))),
            )
        )


def macro_check(elem: pf.Element) -> pf.Span | None:
    """Check if element is a macro."""
    if (
        isinstance(elem, pf.Para)
        and elem.content
        and isinstance(span := elem.content[0], pf.Span)
        and span.content
        and isinstance(string := span.content[0], pf.Str)
        and string.text == ":"
    ):
        return span
    return None


def macro_action(elem: pf.Element, doc: pf.Doc) -> pf.RawBlock | list[None] | None:
    """Perform some action based on macro name."""
    if span := macro_check(elem):
        match span.identifier.lower():

            case "toc":
                with dom.details(cls="toc", open=True) as details:
                    dom.summary("Table of contents")
                    dom_util.raw(pf.convert_text(doc.toc, input_format="panflute", output_format="html"))
                return pf.RawBlock(str(details))

            case "metadata":
                for attribute, value in span.attributes.items():
                    match attribute.lower():
                        case "title" | "date" | "banner":
                            doc.metadata[attribute] = value
                        case _:
                            logger.warning(f"Unknown metadata attribute: {attribute}={value}")
                return []
    return None


def save_toc(doc: pf.Doc) -> None:
    """Save the short toc to metadata for later use."""
    doc.metadata["toc"] = doc.json_toc


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run document through some filters."""
    return pf.run_filters([remove_wrapper, build_json_toc, build_toc, macro_action], finalize=save_toc, doc=doc)


if __name__ == "__main__":
    main()
