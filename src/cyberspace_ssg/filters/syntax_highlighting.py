"""
Highlight code with pygments. Example usage:

```python
print("Hello there")
```

Available block attributes:

{title="Python"} = displays if string is non-empty (default raw: empty, other: language)
{hl_lines="2,6"} = comma separated list of lines to highlight (default empty)
{lineno=1} = The line number to start at. A value of 0 hides line numbers (default raw: 0, other: 1)
"""

import html
import itertools
from contextlib import suppress
from functools import reduce
from pathlib import Path

import panflute as pf
import pygments
import pygments.formatters
import pygments.lexers

from ..config import CSS_PATH, WEB_PATH

STYLE = "gruvbox-dark"
"""The style for syntax highlighting."""

codeblock_counter = itertools.count()

supported_lexers: set[str] = set(
    reduce(lambda supported_lexers, lexer: supported_lexers + lexer[1], pygments.lexers.get_all_lexers(), tuple())
)


def highlight_codeblock(elem: pf.Element, _doc: pf.Doc) -> pf.Div | None:
    """Find and highlight codeblocks if the language is supported."""
    if isinstance(elem, pf.CodeBlock):
        common_lexers = set(map(str.lower, elem.classes)) & supported_lexers
        language = next(iter(common_lexers)) if common_lexers else "text"

        # Line numbers
        lineno = 1
        with suppress(ValueError):
            if not (lineno := int(elem.attributes.get("lineno", "0" if language == "text" else "1"))):
                elem.classes.append("no-linenos")

        # Title
        lexer = pygments.lexers.get_lexer_by_name(language)
        if not (title := elem.attributes.pop("title", "" if language == "text" else html.escape(f"</> {lexer.name}"))):
            elem.classes.append("no-title")
        elem.attributes["data-title"] = title

        # Highlighted lines
        hl_lines = []
        with suppress(ValueError):
            hl_lines = list(map(int, elem.attributes.get("hl_lines", "").split(",")))

        # Generate HTML
        formatter = pygments.formatters.HtmlFormatter(  # pylint: disable=no-member
            style=STYLE,
            filename=title,
            hl_lines=hl_lines,
            linenos="table",
            lineanchors=f"Code-block-{next(codeblock_counter)}",
            anchorlinenos=True,
            linenostart=lineno,
            cssclass=("" if language == "text" else "c ") + "highlight",
        )
        text = pygments.highlight(elem.text, lexer, formatter)
        return pf.Div(pf.RawBlock(text=text), classes=list(set(elem.classes) - {language}), attributes=elem.attributes)
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    # Create CSS file if necessary
    css_full_path = WEB_PATH / CSS_PATH / Path("pygments.css")
    if not css_full_path.exists():
        formatter = pygments.formatters.HtmlFormatter(style=STYLE)  # pylint: disable=no-member
        css_full_path.write_text(formatter.get_style_defs(".highlight"), encoding="utf-8")

    return pf.run_filter(highlight_codeblock, doc=doc)


if __name__ == "__main__":
    main()
