"""
Replace symbol with emojis. Example usage:

:golf:
"""

from contextlib import suppress
import unicodedata
import panflute as pf


def replace_symbol(elem: pf.Element, _doc: pf.Doc) -> pf.Str | None:
    """Replace symbol with emoji if possible."""
    if (
        isinstance(elem, pf.Span)
        and "symbol" in elem.classes
        and elem.content
        and isinstance(string := elem.content[0], pf.Str)
    ):
        with suppress(KeyError):
            return pf.Str(unicodedata.lookup(string.text))
    return None


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(replace_symbol, doc=doc)


if __name__ == "__main__":
    main()
