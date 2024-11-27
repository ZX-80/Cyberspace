"""
Get document title. Add created/modified dates to post titles. Example usage:

# Page Title
"""

from pathlib import Path

import panflute as pf

from .. import config, git


def find_first_header(elem: pf.Element, doc: pf.Doc) -> pf.Div | None:
    """Set the title to the first header."""
    if (
        isinstance(elem, pf.Header)
        and elem.content
        and isinstance(link := elem.content[0], pf.Link)
        and isinstance(string := link.content[0], pf.Str)
        and "found_title" not in doc.metadata
    ):
        doc.metadata["found_title"] = True
        doc.metadata["title"] = doc.get_metadata("title", string.text)
        if (doc_path := Path(doc.get_metadata("path"))).is_relative_to(config.POST_PATH):
            text = []
            commits_diffs = git.get_file_commits(doc_path)
            if len(commits_diffs) >= 1:
                datetime = commits_diffs[-1][0].date
                formatted_date_short = datetime.strftime("%b %d, %Y")
                formatted_date_long = datetime.isoformat()
                text.append(pf.Span(pf.Str(formatted_date_short), attributes={"title": formatted_date_long}))
            if len(commits_diffs) > 1:
                datetime = commits_diffs[0][0].date
                formatted_date_short = datetime.strftime("%b %d, %Y")
                formatted_date_long = datetime.isoformat()
                text.extend(
                    [
                        pf.LineBreak,
                        pf.Span(
                            pf.Str(f"Modified {formatted_date_short}"),
                            attributes={"title": formatted_date_long},
                        ),
                    ]
                )
            return pf.Div(elem, pf.Div(pf.Para(*text), classes=["post-date"]), classes=["side-by-side"])
    return None


def finalize(doc: pf.Doc) -> None:
    """Clean up metadata."""
    doc.metadata.pop("found_title", None)


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(find_first_header, finalize=finalize, doc=doc)


if __name__ == "__main__":
    main()
