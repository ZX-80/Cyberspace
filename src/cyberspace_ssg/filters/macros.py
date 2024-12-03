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

# Post List

Usage :{#post-list"}

Auto-generated list of all posts.
"""

import concurrent.futures
import datetime
import time
from pathlib import Path
from typing import cast

import dominate.tags as dom
import dominate.util as dom_util
import panflute as pf

from .. import cache, config, git
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
        and isinstance(string := span.content[0], pf.Str)
        and string.text == ":"
    ):
        return span, False
    if isinstance(span := elem, pf.Span) and isinstance(string := elem.content[0], pf.Str) and string.text == ":":
        return span, True
    return None


def post_list_macro(elem: pf.Element, doc: pf.Doc) -> pf.RawBlock | list[None] | None:
    """Insert the post list."""
    if span_inline := macro_check(elem):
        span, inline = span_inline

        match span.identifier.lower():

            case "post-list" if not inline:
                # Log unknown metadata
                for attribute, value in span.attributes.items():
                    logger.warning(f"Unknown metadata attribute: {attribute}={value}")

                # Wait for relevant files to be processed
                while not config.futures:
                    time.sleep(0.1)
                relevant_docs = [
                    (path, post_future)
                    for path, post_future in config.futures.items()
                    if path.is_relative_to(config.POST_PATH) and path != Path(doc.get_metadata("path"))
                ]
                print(relevant_docs)
                concurrent.futures.wait(post_future for _, post_future in relevant_docs if post_future)

                # Build list
                post_list: dict[datetime.datetime, tuple[datetime.datetime, str, Path]] = {}
                for path, _ in relevant_docs:
                    if commits := git.load_git_data().get(path.as_posix(), []):
                        git_date = commits[-1][0].date
                        title = cache.load_cache()[path].metadata["title"]
                        post_list.setdefault(git_date.year, []).append((git_date, title, path))
                lists = []
                list_items = []
                for year in sorted(post_list, reverse=True):
                    for post in sorted(post_list[year], reverse=True):
                        list_items.append(
                            pf.ListItem(
                                pf.Para(
                                    pf.Span(
                                        pf.Str(post[0].strftime("%b %d")),
                                        classes=["highlighted"],
                                        attributes={"title": post[0].isoformat()},
                                    ),
                                    pf.Link(
                                        pf.Str(
                                            post[1],
                                        ),
                                        url=(
                                            Path("/") / post[2].relative_to(config.SOURCE_PATH).with_suffix("")
                                        ).as_posix(),
                                    ),
                                )
                            )
                        )
                    lists.append(
                        pf.Div(
                            pf.Header(pf.Link(pf.Str(str(year)), url=f"#{str(year)}"), level=2), identifier=str(year)
                        )
                    )
                    lists.append(pf.Div(pf.BulletList(*list_items), classes=["index-list"]))
                    list_items = []
                return pf.Div(
                    pf.Div(
                        pf.Header(pf.Link(pf.Str("Date"), url="#Date"), level=1),
                        pf.HorizontalRule,
                        *lists,
                        classes=["date-list"],
                        identifier="Date",
                    ),
                    pf.Div(
                        pf.Header(pf.Link(pf.Str("Series"), url="#Series"), level=1),
                        pf.HorizontalRule,
                        classes=["series-list"],
                        identifier="Series",
                    ),
                    classes=["side-by-side"],
                )
    return None


def macro_action(elem: pf.Element, doc: pf.Doc) -> pf.RawBlock | list[None] | None:
    """Perform some action based on macro name."""
    if span_inline := macro_check(elem):
        span, inline = span_inline

        match span.identifier.lower():

            case "toc" if not inline:
                with dom.details(cls="toc", open=True) as details:
                    dom.summary("Table of contents")
                    dom_util.raw(pf.convert_text(doc.toc, input_format="panflute", output_format="html"))
                return pf.RawBlock(str(details))

            case "metadata" if not inline:
                for attribute, value in span.attributes.items():
                    match attribute.lower():
                        case "title" | "date" | "banner":
                            doc.metadata[attribute] = value
                        case _:
                            logger.warning(f"Unknown metadata attribute: {attribute}={value}")
                return []

    return None


def finalize(doc: pf.Doc) -> None:
    """Save the short toc to metadata for later use."""
    doc.metadata["toc"] = doc.json_toc


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run document through some filters."""
    return pf.run_filters(
        [remove_wrapper, post_list_macro, build_json_toc, build_toc, macro_action], finalize=finalize, doc=doc
    )


if __name__ == "__main__":
    main()
