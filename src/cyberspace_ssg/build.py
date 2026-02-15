"""Build a static website."""

import concurrent.futures
import pkgutil
import shutil
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Any, Iterator, Self

import dominate
import dominate.tags as dom
import dominate.util as dom_util
import panflute as pf
from feedgen.feed import FeedGenerator
from lxml import etree

from . import cache, config, filters, formats, git
from .config import logger
from .json_feed import JSONFeed


@dataclass
class FeedPost:
    """Data about a post."""

    date_created: datetime
    date_modified: datetime
    title: str
    source_path: Path

    def __lt__(self, other: Self) -> bool:
        """Make feeds sortable."""
        return self.date_created < other.date_created


class SiteConstructor:
    """Generate data for use by the site templates."""

    def __new__(cls) -> None:
        """Destroy the instance after initialization."""
        instance = super().__new__(cls)
        instance.__init__()

    def __init__(self) -> None:
        # Locate all CSS files
        self.css_files = [
            css_file.relative_to(config.WEB_PATH) for css_file in (config.WEB_PATH / config.STYLE_PATH).glob("**/*.css")
        ]

        # Locate all top-level source paths
        self.nav_elements = sorted(
            (
                Path("/") / path.with_suffix("").relative_to(config.SOURCE_PATH)
                for path in (config.SOURCE_PATH / config.NAV_PATH).iterdir()
            ),
            key=lambda path: (path.is_file(), path),
        )
        self.nav_elements = {nav_path.stem.title().replace("_", " "): nav_path for nav_path in self.nav_elements}
        logger.debug(f"Nav elements: {", ".join(self.nav_elements)}")

        # Locate all filter modules
        self.filter_modules = sorted(
            [
                import_module(module_name)
                for _, module_name, _ in pkgutil.iter_modules(filters.__path__, prefix=f"{filters.__name__}.")
            ],
            key=lambda module: module.PRIORITY,
        )
        filter_names = map(lambda module: module.__name__.removeprefix(f"{filters.__name__}."), self.filter_modules)
        logger.debug(f"Filter modules: {", ".join(filter_names)}")

        self.batch_process_files()

    def convert_source_to_html(
        self, source_text: str, input_format: str, source_path: Path
    ) -> tuple[str, dict[str, Any]]:
        """Converts source file to pure html."""
        # Get document tree and apply filters
        document_tree = pf.convert_text(source_text, input_format, standalone=True)
        document_tree.metadata["path"] = source_path.as_posix()
        for filter_module in self.filter_modules:
            document_tree = filter_module.main(document_tree)
        del document_tree.metadata["path"]

        # Save metadata
        metadata = {key: document_tree.get_metadata(key) for key in document_tree.metadata}
        cache_database = cache.load_cache()
        if source_path in cache_database:
            cache_database[source_path].metadata = metadata
        cache.sync_cache(cache_database)

        # Return HTML and metadata
        html = pf.convert_text(
            document_tree,
            input_format="panflute",
            output_format="html",
            extra_args=["--no-highlight", "--mathml"],
        )
        return html, metadata

    def generate_page(self, html: str, metadata: dict[str, Any], file_name: Path) -> str:
        """Add document and navbar html."""

        title = metadata.get("title", metadata.get("auto-title", "Page"))
        xslt = metadata.get("file_type") == "xslt"
        page = dominate.document(
            title=f"/{title}/",
            lang="en",
            doctype="" if xslt else "<!DOCTYPE html>",
        )

        # HTML Head
        with page.head:
            dom.meta(charset="utf-8")
            dom.meta(name="viewport", content="width=device-width, initial-scale=1.0")
            dom.link(
                rel="alternate",
                title="Atom Feed",
                type="application/atom+xml",
                href=f"https://{(config.WEBSITE_URL / config.ATOM_PATH.relative_to("/")).as_posix()}",
            )
            dom.link(
                rel="alternate",
                title="RSS Feed",
                type="application/rss+xml",
                href=f"https://{(config.WEBSITE_URL / config.RSS_PATH.relative_to("/")).as_posix()}",
            )
            dom.link(
                rel="alternate",
                title="JSON Feed",
                type="application/feed+json",
                href=f"https://{(config.WEBSITE_URL / config.JSON_PATH.relative_to("/")).as_posix()}",
            )
            for css_file in self.css_files:
                dom.link(rel="stylesheet", type="text/css", href=Path("/") / css_file)

        # HTML Body
        with page.body as body:
            # Generate Navbar
            if xslt:
                body["xmlns:xsl"] = "http://www.w3.org/1999/XSL/Transform"
            dom.div(cls="NavBackground")
            with dom.div():
                with dom.nav():
                    dom.img(cls="ProfileImage", src=config.PROFILE_IMAGE)
                    dom.label("Waste of Cyberspace", cls="  NavTitle")
                    dom.hr()
                    for nav_name, nav_path in self.nav_elements.items():
                        dom.a(nav_name, cls="sidebar", href=nav_path)
                    if metadata.get("toc"):
                        dom.hr()
                        with dom.div(cls="tocLinks"):
                            for href, title in metadata["toc"].items():
                                dom.a(title, cls="sidebar", href=f"#{href}")

            # Generate banner and post
            with dom.div(cls="ArticleParent", style="float:right;"):
                with dom.article():
                    # Insert banner
                    if banner_name := metadata.get("banner"):
                        with dom.div():
                            dom.img(cls="Banner", src=config.IMAGE_PATH / banner_name, alt="Banner")
                    # Insert post
                    with dom.div(cls="Post-parent"):
                        with dom.div(cls="Post"):
                            dom_util.raw(html)
                        with dom.div(cls="Footer"):
                            with dom.footer():
                                with dom.p():
                                    dom.a(
                                        "Source",
                                        href=file_name.with_suffix(f"{file_name.suffix}.txt"),
                                    )
                                    dom_util.text(" | ")
                                    dom.a(
                                        "Top",
                                        href="#top",
                                    )
        return page.render(xhtml=xslt)

    def write_file(self, relative_file_path: Path) -> bool:
        """Generate and write file based on file path and type."""

        # Generate HTML
        source_path = config.SOURCE_PATH / relative_file_path
        source_text = source_path.read_text("utf-8", errors="ignore")
        input_format = formats.from_extension(relative_file_path.suffix)
        article_html, metadata = self.convert_source_to_html(source_text, input_format, source_path)
        file_path = config.WEB_PATH / relative_file_path
        document_content = self.generate_page(article_html, metadata, Path(relative_file_path.name))
        match metadata.get("file_type", "html"):
            case "html":
                file_path = file_path.with_suffix(".html")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(document_content, "utf-8")
            case "xslt":
                file_path = file_path.with_suffix(".xslt")
                tree = etree.parse(config.WEB_PATH / config.FEED_STYLE_PATH)
                new_elem = etree.fromstring(document_content)
                tree.find('{http://www.w3.org/1999/XSL/Transform}template[@match="/"]').append(new_elem)
                parser = etree.XMLParser(remove_blank_text=True)
                new_tree = etree.ElementTree(etree.fromstring(etree.tostring(tree), parser=parser))
                etree.indent(new_tree)
                document_content = etree.tostring(new_tree, encoding="unicode")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(document_content, "utf-8")
            case file_type:
                logger.error(f'Unknown filetype "{file_type}". Cannot write file.')

    def process_file(self, relative_file_path: Path) -> None:
        """Convert a file to a webpage."""
        logger.info(f"Converting {relative_file_path}")

        @contextmanager
        def timer(name: str) -> Iterator[None]:
            """Track runtime in context."""
            start = time.perf_counter()
            yield
            logger.debug(f"{name} time: {time.perf_counter() - start:05.2f} seconds - {relative_file_path}")

        try:
            # Generate article
            with timer("Execution"):
                self.write_file(relative_file_path)
                shutil.copyfile(  # Copy raw file over
                    config.SOURCE_PATH / relative_file_path,
                    config.WEB_PATH / relative_file_path.with_suffix(f"{relative_file_path.suffix}.txt"),
                )
        except RuntimeError as e:
            logger.error(f"  Failed: {e}")

    def batch_process_files(self) -> None:
        """Convert all files in source path."""
        total_start_time = time.perf_counter()
        git.load_git_data()

        # Spawn threads
        futures: dict[Path, concurrent.futures.Future] = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for dirpath, _dirnames, filenames in config.SOURCE_PATH.walk():
                for source_file in filenames:
                    full_path = dirpath / source_file
                    futures[full_path] = (
                        executor.submit(self.process_file, dirpath.relative_to(config.SOURCE_PATH) / source_file)
                        if cache.cache_miss(full_path)
                        else None
                    )

            # Check for exceptions
            processed_files = [future for future in futures.values() if future]
            for future in concurrent.futures.as_completed(processed_files):
                if exception := future.exception():
                    logger.error("".join(traceback.format_exception(exception)))

            # Generate feed
            feed_path = next(
                (
                    (Path("/") / path.relative_to(config.SOURCE_PATH).with_suffix(".xslt")).as_posix()
                    for (path, cache_entry) in cache.load_cache().items()
                    if cache_entry.metadata.get("file_type") == "xslt"
                ),
                Path(),
            )
            fg = FeedGenerator()
            fg.title("/Waste of Cyberspace/")
            fg.subtitle("Posts from the Waste of Cyberspace site.")
            fg.language("en-us")
            if feed_path:
                fg.link(href=f"{feed_path}", rel="related", type="text/xsl")
            fg.link(
                href=f"https://{(config.WEBSITE_URL / config.ATOM_PATH.relative_to("/")).as_posix()}",
                rel="self",
                type="application/atom+xml",
            )
            fg.link(href=f"https://{config.WEBSITE_URL.as_posix()}/", rel="alternate", type="text/html")
            fg.logo(f"https://{(config.WEBSITE_URL / config.PROFILE_IMAGE.relative_to("/")).as_posix()}")
            fg.id(f"https://{config.WEBSITE_URL.as_posix()}/")

            post_list: dict[datetime, list[FeedPost]] = {}
            for path in futures:
                if (
                    path.is_relative_to(config.POST_PATH)
                    and path.with_suffix("") != config.POST_PATH / "index"
                    and (commits := git.load_git_data().get(path.as_posix(), []))
                ):
                    git_date_created = commits[-1][0].date
                    git_date_modified = commits[0][0].date
                    title = cache.load_cache()[path].metadata.get("title", "NO TITLE")
                    post_list.setdefault(git_date_created.year, []).append(
                        FeedPost(git_date_created, git_date_modified, title, path)
                    )
            for year in sorted(post_list, reverse=True):
                for post in sorted(post_list[year]):
                    fe = fg.add_entry()
                    fe.author(
                        {
                            "name": "ZX-80",
                            "email": f"FeedContact@{config.WEBSITE_URL}",
                            "uri": f"https://{config.WEBSITE_URL.as_posix()}/",
                        }
                    )
                    fe.pubDate(post.date_created.isoformat())
                    fe.updated(post.date_modified.isoformat())
                    fe.title(post.title)
                    post_path = config.WEBSITE_URL / post.source_path.relative_to(config.SOURCE_PATH).with_suffix("")
                    fe.link(href=f"https://{post_path.as_posix()}", rel="alternate", type="text/html")
                    fe.id(f"https://{post_path.as_posix()}")
                    raw_text = post.source_path.read_text(encoding="utf-8").strip("\n")
                    fe.content(f"<pre>\n{raw_text}\n</pre>", type="html")

            style_header = (
                f'<?xml-stylesheet type="text/xsl" href="{feed_path}" ?>'.encode("utf-8") if feed_path else bytes()
            )
            for short_path, text in ((config.ATOM_PATH, fg.atom_str), (config.RSS_PATH, fg.rss_str)):
                styled_text: bytes = style_header + text(xml_declaration=False, pretty=True)
                path = config.WEB_PATH / short_path.relative_to("/")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(styled_text)
                fg.link(
                    href=f"https://{(config.WEBSITE_URL / config.RSS_PATH.relative_to("/")).as_posix()}",
                    rel="self",
                    type="application/rss+xml",
                    replace=True,
                )

            # Write JSON feed
            JSONFeed(fg).write(config.WEB_PATH / config.JSON_PATH.relative_to("/"))

        logger.info(f"Converted {len(processed_files)} files in {time.perf_counter() - total_start_time:.2f} seconds")


def main() -> None:
    """Generate the website."""
    SiteConstructor()


if __name__ == "__main__":
    main()
