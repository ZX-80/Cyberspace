"""
Add an aspect ratio to all images.
"""

from pathlib import Path

import panflute as pf
from PIL import Image

from .. import config


def add_aspect(elem: pf.Element, doc: pf.Doc) -> None:
    """Add aspect ratio to all images."""
    if isinstance(elem, pf.Image):
        image_path = Path(elem.url)
        try:
            if image_path.is_relative_to("/"):  # Absolute path
                image_path = config.WEB_PATH / image_path.relative_to("/")
            else:  # Relative path
                doc_path = Path(doc.get_metadata("path")).relative_to(config.SOURCE_PATH).parent
                image_path = config.WEB_PATH / doc_path / image_path
            image_data = Image.open(image_path)
            width, height = image_data.size
            elem.attributes["style"] = f"{elem.attributes.get('style')}; aspect-ratio: {width} / {height};"
        except FileNotFoundError:
            config.logger.warning(f"File not found: {image_path.as_posix()}")


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    """Run document through some filters."""
    return pf.run_filter(add_aspect, doc=doc)


if __name__ == "__main__":
    main()
