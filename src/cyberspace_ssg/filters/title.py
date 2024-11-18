"""
Get document title. Example usage:

# Page Title
"""

from pathlib import Path

import panflute as pf

from .. import git


def find_first_header(elem: pf.Element, doc: pf.Doc) -> pf.Div | None:
    """Set the title to the first header."""
    if (
        isinstance(elem, pf.Header)
        and elem.content
        and isinstance(link := elem.content[0], pf.Link)
        and isinstance(string := link.content[0], pf.Str)
        and "auto-title" not in doc.metadata
    ):
        doc.metadata["auto-title"] = string.text
        if "post-title" in elem.parent.classes:
            text = []
            commits_diffs = git.get_file_commits(Path(doc.get_metadata("path")))
            if len(commits_diffs) >= 1:
                text.append(pf.Str(commits_diffs[0][0].date.strftime("%b %d, %Y")))
            if len(commits_diffs) > 1:
                text.extend([pf.LineBreak, pf.Str(f"Modified {commits_diffs[-1][0].date.strftime("%b %d, %Y")}")])
            return pf.Div(elem, pf.Div(pf.Para(*text), classes=["post-date"]), classes=["side-by-side"])
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(find_first_header, doc=doc)


if __name__ == "__main__":
    main()
