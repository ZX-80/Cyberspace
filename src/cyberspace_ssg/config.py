"""Contains common configurations for the package."""

import logging
from concurrent.futures import Future
from pathlib import Path

SOURCE_PATH = Path("text")
"""The default source path."""

NAV_PATH = Path("pages")
"""The path to document files for the navigation bar."""

POST_PATH = SOURCE_PATH / NAV_PATH / "posts"
"""The path to find all posts."""

WEB_PATH = Path("web")
"""The path to all website related files. Also serves as an output path for html/css generation."""

STYLE_PATH = Path("layouts")
"""The path to all CSS files."""

FEED_STYLE_PATH = STYLE_PATH / "feed_template.xslt"
"""The path to the feed style template."""

JS_PATH = Path("/scripts")
"""The path to any javascript."""

IMAGE_PATH = Path("/images")
"""The path to all image files."""

PROFILE_IMAGE = IMAGE_PATH / "profile.png"
"""Filename for default profile image."""

CHANGELOG_TEMPLATE = "changelog_template.dj"
"""Filename for the changelog template."""

INVALIDATION_MODE = "hashing"
"""The method for invalidating cache."""

WEBSITE_URL = Path("wasteofcyberspace.net")
"""The URL used by feeds."""

FEED_PATH = Path("/feed")
"""Where to store feed files."""

ATOM_PATH = FEED_PATH / "atom.xml"
"""The path for the Atom feed."""

RSS_PATH = FEED_PATH / "rss.xml"
"""The path for the RSS feed."""

# Some globally shared WORM (write once, read many) variables
logger = logging.getLogger("SSG")
"""Used for console output."""

futures: dict[Path, Future] = {}
"""A mapping of all the files being processed."""
