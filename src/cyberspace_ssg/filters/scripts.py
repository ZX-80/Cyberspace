"""
Expand pyscript blocks. Example usage:

```=pyscript
from pyscript import document
document.body.append("Hello from PyScript")
```
"""

import dominate.tags as dom
import dominate.util as dom_util
import panflute as pf
from panflute.elements import RAW_FORMATS

from ..config import JS_PATH

PRIORITY = 10
"""The filters execution priority (lower executes earlier)"""


RAW_FORMATS.add("pyscript")  # Add support for pyscript blocks
RAW_FORMATS.add("javascript")  # Add support for javascript blocks


def expand_script(elem: pf.Element, doc: pf.Doc) -> None:
    """Expand pyscript blocks."""
    if isinstance(elem, pf.RawBlock):
        match elem.format.lower():

            case "javascript":  # Javascript block
                elem.format = "html"
                elem.text = dom.script(
                    dom_util.raw(f"\n{elem.text}"),
                    type="text/javascript",
                ).render()

            case "pyscript":  # PyScript block
                # Get config
                micropython_path = (JS_PATH / "micropython/micropython.mjs").as_posix()
                config = dom_util.raw(
                    f'{{"interpreter": ["{micropython_path}"], "plugins": ["!error"]}}'.replace('"', "&quot;")
                )

                # Clear block
                python_code = elem.text
                elem.format = "html"
                elem.text = ""

                # Only import core once
                if not doc.metadata.get("core_imported"):
                    doc.metadata["core_imported"] = True
                    elem.text += dom.script(src=JS_PATH / "pyscript/core.js", type="module").render()

                # Wrap user script
                elem.text += dom.script(
                    dom_util.raw(f"\n{python_code}"),
                    type="mpy",
                    config=config,
                ).render()


def finalize(doc: pf.Doc) -> None:
    """Clean up metadata."""
    doc.metadata.pop("core_imported", None)


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run actions."""
    return pf.run_filter(expand_script, finalize=finalize, doc=doc)


if __name__ == "__main__":
    main()
