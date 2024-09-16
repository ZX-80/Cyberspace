"""Contains common configurations for the package."""

import logging
from pathlib import Path

SOURCE_PATH = Path("text")
"""The default source path."""

NAV_PATH = Path("pages")
"""The path to document files for the navigation bar."""

WEB_PATH = Path("web")
"""The path to all website related files. Also serves as an output path for html/css generation."""

CSS_PATH = Path("layouts")
"""The path to all CSS files."""

JS_PATH = Path("scripts")
"""The path to any javascript."""

IMAGE_PATH = Path("images")
"""The path to all image files."""

logger = logging.getLogger("Cyberspace SSG")
