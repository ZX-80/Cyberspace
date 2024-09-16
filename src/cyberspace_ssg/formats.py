"""Handle available file extensions / formats."""

import fnmatch
import functools

import panflute as pf

# See: https://github.com/jgm/pandoc/blob/main/src/Text/Pandoc/Format.hs
formats = {
    ".Rmd": "markdown",
    ".adoc": "asciidoc",
    ".asciidoc": "asciidoc",
    ".bib": "biblatex",
    ".context": "context",
    ".csv": "csv",
    ".ctx": "context",
    ".db": "docbook",
    ".dj": "djot",
    ".doc": "doc",
    ".docx": "docx",
    ".dokuwiki": "dokuwiki",
    ".epub": "epub",
    ".fb2": "fb2",
    ".htm": "html",
    ".html": "html",
    ".icml": "icml",
    ".ipynb": "ipynb",
    ".json": "json",
    ".latex": "latex",
    ".lhs": "markdown",
    ".ltx": "latex",
    ".markdown": "markdown",
    ".markua": "markua",
    ".md": "markdown",
    ".mdown": "markdown",
    ".mdwn": "markdown",
    ".mkd": "markdown",
    ".mkdn": "markdown",
    ".ms": "ms",
    ".muse": "muse",
    ".native": "native",
    ".odt": "odt",
    ".opml": "opml",
    ".org": "org",
    ".pdf": "pdf",
    ".pptx": "pptx",
    ".ris": "ris",
    ".roff": "ms",
    ".rst": "rst",
    ".rtf": "rtf",
    ".s5": "s5",
    ".t2t": "t2t",
    ".tei": "tei",
    ".tex": "latex",
    ".texi": "texinfo",
    ".texinfo": "texinfo",
    ".text": "markdown",
    ".textile": "textile",
    ".tsv": "tsv",
    ".typ": "typst",
    ".txt": "djot",
    ".wiki": "mediawiki",
    ".xhtml": "html",
    ".1*": "man",
    ".2*": "man",
    ".3*": "man",
    ".4*": "man",
    ".5*": "man",
    ".6*": "man",
    ".7*": "man",
    ".8*": "man",
    ".9*": "man",
}


@functools.cache
def supported_formats() -> dict[str, str]:
    """Only support what pandoc supports."""
    pandoc_formats = pf.run_pandoc("", ["--list-input-formats"]).splitlines()
    return {extension: format_name for extension, format_name in formats.items() if format_name in pandoc_formats}


def from_extension(extension: str) -> str:
    """Get the format name of an extension."""
    for extension_pattern, format_name in supported_formats().items():
        if fnmatch.fnmatch(extension, extension_pattern):
            return format_name
    raise RuntimeError(f"Unknown file extension \"{extension}\". Must be one of: {', '.join(supported_formats())}")
