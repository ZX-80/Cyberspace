"""Functions for managing a JSON feed."""

import json
from pathlib import Path

from feedgen.feed import FeedGenerator

from . import config


class JSONFeed:
    """A JSON feed object."""

    def __init__(self, feed: FeedGenerator) -> None:
        """Convert feed to json."""
        self.feed: dict[str, str] = {}
        self.feed["version"] = "https://jsonfeed.org/version/1.1"
        self.feed["home_page_url"] = f"https://{config.WEBSITE_URL.as_posix()}"
        self.feed["feed_url"] = f"https://{(config.WEBSITE_URL / config.JSON_PATH.relative_to("/")).as_posix()}"
        self.feed["user_comment"] = (
            "This page isn't for human consumption. Please copy-and-paste this pages URL into your news reader if it "
            f"supports JSON feeds. See https://{(config.WEBSITE_URL / 'pages/subscribe').as_posix()} for more details."
        )
        self.feed["description"] = feed.subtitle()
        self.feed["title"] = feed.title()
        self.feed["icon"] = feed.logo()
        self.feed["language"] = feed.language()
        self.feed["items"] = [
            {
                "id": entry.id(),
                "title": entry.title(),
                "content_html": entry.content()["content"],
                "date_published": entry.pubDate().isoformat(),
                "date_modified": entry.updated().isoformat(),
                "url": next(iter(entry.link()), {}).get("href"),
            }
            for entry in feed.entry()
        ]

    def write(self, output_path: Path) -> None:
        """Write feed to file."""
        output_path.write_text(self.raw_json(), encoding="utf-8")

    def raw_json(self) -> str:
        """Get the json feed."""
        return json.dumps(self.feed, indent=4)
