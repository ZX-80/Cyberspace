"""
Detect use of mermaid. Example usage:

```mermaid
flowchart LR
    Start --> Stop
```
"""

import shlex
import subprocess

import dominate.tags as dom
import panflute as pf

from ..config import JS_PATH

MERMAID_CONFIG = """
---
config:
  theme: dark
---
"""


def detect_mermaid(elem: pf.Element, doc: pf.Doc) -> pf.RawBlock | None:
    """
    Detect the use of mermaid js. If mermaid-cli is installed, convert
    the code into an svg during the website build. Otherwise load the
    mermaid js scripts and convert when the page is loaded.
    """
    if isinstance(elem, pf.CodeBlock) and "mermaid" in elem.classes:
        try:  # Attempt mermaid-cli conversion
            svg_data = subprocess.run(
                shlex.split("mmdc -i - -o - -t dark -b transparent"),
                input=elem.text,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
            )
            return pf.RawBlock(svg_data.stdout)
        except subprocess.CalledProcessError:
            doc.metadata["mermaid"] = True
            elem.text = f"{MERMAID_CONFIG}{elem.text}"
            return pf.RawBlock(dom.pre(elem.text, cls="mermaid").render())
    return None


def finalize(doc: pf.Doc) -> None:
    """Insert mermaid script if necessary"""
    if doc.metadata.get("mermaid"):
        doc.content.append(pf.RawBlock(str(dom.script(src=JS_PATH / "mermaid.esm.min.mjs", type="module"))))


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(detect_mermaid, finalize=finalize, doc=doc)


if __name__ == "__main__":
    main()
