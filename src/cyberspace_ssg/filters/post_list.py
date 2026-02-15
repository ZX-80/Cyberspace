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

import datetime
import time
from pathlib import Path

import panflute as pf

from .. import cache, config, git
from ..config import logger

PRIORITY = 10
"""The filters execution priority (lower executes earlier)"""


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
                cache_database = {}
                while not cache_database or not all(map(bool, cache_database.values())):
                    cache_database = {
                        path: data
                        for path, data in cache.load_cache().items()
                        if path.is_relative_to(config.POST_PATH) and path != Path(doc.get_metadata("path"))
                    }
                    time.sleep(0.1)

                # Build list
                post_list: dict[datetime.datetime, tuple[datetime.datetime, str, Path]] = {}
                for path in cache_database:
                    if commits := git.load_git_data().get(path.as_posix(), []):
                        git_date = commits[-1][0].date
                        title = cache.load_cache()[path].metadata.get("title", "NO TITLE")
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


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run document through some filters."""
    return pf.run_filter(post_list_macro, doc=doc)


if __name__ == "__main__":
    main()
