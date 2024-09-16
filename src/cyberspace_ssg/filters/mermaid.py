"""
Detect use of mermaid. Example usage:

```mermaid
flowchart LR
    Start --> Stop
```
"""

from pathlib import Path

import dominate.tags as dom
import panflute as pf

from ..config import JS_PATH

mermaid_config = """
---
config:
  theme: dark
---
"""


def detect_mermaid(elem: pf.Element, doc: pf.Doc) -> pf.RawBlock | None:
    """Detect the use of mermaid js."""
    if isinstance(elem, pf.CodeBlock) and "mermaid" in elem.classes:
        doc.metadata["mermaid"] = True
        elem.text = mermaid_config + elem.text
        return pf.RawBlock(str(dom.pre(elem.text, cls="mermaid")))
    return None


def finalize(doc: pf.Doc) -> None:
    """Insert mermaid script if necessary"""
    if doc.metadata.get("mermaid"):
        doc.content.append(pf.RawBlock(str(dom.script(src=Path("/") / JS_PATH / "mermaid.esm.min.mjs", type="module"))))


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(detect_mermaid, finalize=finalize, doc=doc)


if __name__ == "__main__":
    main()
