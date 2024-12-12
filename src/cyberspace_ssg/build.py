"""Build a static website."""

import concurrent.futures
import itertools
import pkgutil
import shutil
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
from string import Template
from typing import Any, Iterator, Self

import dominate
import dominate.tags as dom
import dominate.util as dom_util
import panflute as pf
from feedgen.feed import FeedGenerator
from lxml import etree

from . import cache, config, filters, formats, git
from .config import logger


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
        self.filter_modules = [
            import_module(module_name)
            for _, module_name, _ in pkgutil.iter_modules(filters.__path__, prefix=f"{filters.__name__}.")
        ]
        filter_names = map(lambda module: module.__name__.removeprefix(f"{filters.__name__}."), self.filter_modules)
        logger.debug(f"Filter modules: {", ".join(filter_names)}")

        self.batch_process_files()

    def changelog_name(self, file_path: Path) -> Path:
        """Convert regular path to changelog path."""
        return file_path.with_stem(f"{file_path.stem}-changelog")

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

    def generate_source_changelog(self, relative_file_path: Path) -> tuple[str, dict[str, Any]]:
        """Construct a changelog page."""
        year: int | None = None
        full_path = config.SOURCE_PATH / relative_file_path

        # Templates
        commit_list = ""
        commit_list_template = (
            '- `<label><input type="radio" name="changelog" id="radio{radio_id}" {checked}>`{{=html}} '
            '{{={date}=}}{{title="{date_iso}"}} `<a>{text}</a></label>`{{=html}}\n'
        )
        radio_counter = itertools.count()

        diffs = ""
        diff_template = (
            "::: changelog-diff{diff_id}\n{body}\n\n``` =html\n{html}\n```\n"
            "{{.right-align}}\nCommit: `{git_hash}`\n\n:::\n"
        )
        diff_counter = itertools.count()

        css_selectors = []
        css_selector_template = ".side-by-side:has(#{radio_id}:checked) .{div_id}"

        # Fetch git information for file
        for commit, diff_html in git.get_file_commits(full_path):
            # Commit list year
            if year is None or commit.date.year < year:
                year = commit.date.year
                commit_list += f"## {year}\n\n{{.index-list}}\n"

            # Diff
            diff_id = next(diff_counter)
            diffs += diff_template.format(html=diff_html, diff_id=diff_id, git_hash=commit.hash_id, body=commit.body)

            # Commit list
            radio_id = next(radio_counter)
            commit_list += commit_list_template.format(
                date=commit.date.strftime("%b %d"),
                date_iso=commit.date.isoformat(),
                radio_id=radio_id,
                text=commit.subject,
                checked="" if css_selectors else "checked",
            )
            css_selectors.append(
                css_selector_template.format(radio_id=f"radio{radio_id}", div_id=f"changelog-diff{diff_id}")
            )

        # Create changelog page
        changelog_path = Path(__file__).parent / Path(config.CHANGELOG_TEMPLATE)
        raw_changelog = Template(changelog_path.read_text("utf-8")).substitute(
            selectors=",\n".join(css_selectors), commit_list=commit_list, diffs=diffs
        )
        changelog_file = config.WEB_PATH / self.changelog_name(relative_file_path).with_suffix(
            f"{changelog_path.suffix}.txt"
        )
        changelog_file.parent.mkdir(parents=True, exist_ok=True)
        changelog_file.write_text(raw_changelog, "utf-8")
        input_format = formats.from_extension(Path(config.CHANGELOG_TEMPLATE).suffix)
        changelog_html, changelog_metadata = self.convert_source_to_html(raw_changelog, input_format, changelog_file)
        return changelog_html, changelog_metadata

    def generate_page(self, html: str, metadata: dict[str, Any], file_name: Path, changelog: bool = False) -> str:
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
                        with dom.footer():
                            with dom.p():
                                if changelog:
                                    dom.a(
                                        "Source",
                                        href=self.changelog_name(file_name).with_suffix(f"{file_name.suffix}.txt"),
                                    )
                                    dom_util.text(" | ")
                                    dom.a(
                                        "Latest",
                                        href=file_name.with_suffix(""),
                                    )
                                else:
                                    dom.a(
                                        "Source",
                                        href=file_name.with_suffix(f"{file_name.suffix}.txt"),
                                    )
                                    if not xslt:
                                        dom_util.text(" | ")
                                        dom.a(
                                            "Change log",
                                            href=self.changelog_name(file_name).with_suffix(""),
                                        )
        return page.render(xhtml=xslt)

    def write_file(self, relative_file_path: Path, changelog: bool = False) -> bool:
        """Generate and write file based on file path and type. Return true if the file needs a changelog."""

        # Generate HTML
        if changelog:
            article_html, metadata = self.generate_source_changelog(relative_file_path)
            file_path = config.WEB_PATH / self.changelog_name(relative_file_path).with_suffix(".html")
        else:
            source_path = config.SOURCE_PATH / relative_file_path
            source_text = source_path.read_text("utf-8", errors="ignore")
            input_format = formats.from_extension(relative_file_path.suffix)
            article_html, metadata = self.convert_source_to_html(source_text, input_format, source_path)
            file_path = config.WEB_PATH / relative_file_path
        document_content = self.generate_page(article_html, metadata, Path(relative_file_path.name), changelog)
        match metadata.get("file_type", "html"):
            case "html":
                file_path = file_path.with_suffix(".html")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(document_content, "utf-8")
                return True
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
                return False
            case file_type:
                logger.error(f'Unknown filetype "{file_type}". Cannot write file.')
                return False

        # Write file

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
                generate_changelog = self.write_file(relative_file_path)
                shutil.copyfile(  # Copy raw file over
                    config.SOURCE_PATH / relative_file_path,
                    config.WEB_PATH / relative_file_path.with_suffix(f"{relative_file_path.suffix}.txt"),
                )

            # Generate changelog
            if generate_changelog:
                with timer("Changelog"):
                    self.write_file(relative_file_path, True)
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
            config.futures |= futures

            # Check for exceptions
            processed_files = [future for future in config.futures.values() if future]
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
            fg.link(href=f"https://{(config.WEBSITE_URL / config.ATOM_PATH.relative_to("/")).as_posix()}", rel="self")
            fg.link(href=f"https://{config.WEBSITE_URL.as_posix()}", rel="alternate")
            fg.logo(f"https://{(config.WEBSITE_URL / config.PROFILE_IMAGE.relative_to("/")).as_posix()}")
            fg.id(f"https://{config.WEBSITE_URL.as_posix()}")

            post_list: dict[datetime, list[FeedPost]] = {}
            for path, _post_future in config.futures.items():
                if (
                    path.is_relative_to(config.POST_PATH)
                    and path.with_suffix("") != config.POST_PATH / "index"
                    and (commits := git.load_git_data().get(path.as_posix(), []))
                ):
                    logger.critical(f"{path}")
                    git_date_created = commits[-1][0].date
                    git_date_modified = commits[0][0].date
                    title = cache.load_cache()[path].metadata["title"]
                    post_list.setdefault(git_date_created.year, []).append(
                        FeedPost(git_date_created, git_date_modified, title, path)
                    )
            for year in sorted(post_list, reverse=True):
                for post in sorted(post_list[year]):
                    fe = fg.add_entry()
                    fe.pubDate(post.date_created.isoformat())
                    fe.updated(post.date_modified.isoformat())
                    fe.title(post.title)
                    post_path = config.WEBSITE_URL / post.source_path.relative_to(config.SOURCE_PATH).with_suffix("")
                    fe.link(href=f"https://{post_path.as_posix()}", rel="alternate")
                    fe.id(post_path.as_posix())
                    raw_text = post.source_path.read_text(encoding="utf-8").strip("\n")
                    fe.content(f"<pre>\n{raw_text}\n</pre>", type="html")

            style_header = (
                f'<?xml-stylesheet type="text/xsl" href="{feed_path}" ?>'.encode("utf-8") if feed_path else bytes()
            )
            for short_path, text in ((config.ATOM_PATH, fg.atom_str), (config.RSS_PATH, fg.rss_str)):
                styled_text: bytes = style_header + text(xml_declaration=False)
                path = config.WEB_PATH / short_path.relative_to("/")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(styled_text)

        logger.info(f"Converted {len(processed_files)} files in {time.perf_counter() - total_start_time:.2f} seconds")


def main() -> None:
    """Generate the website."""
    SiteConstructor()


if __name__ == "__main__":
    main()
