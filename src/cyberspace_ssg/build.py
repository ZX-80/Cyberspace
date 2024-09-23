"""Build a static website."""

import itertools
import pkgutil
import shutil
import time
from enum import Enum, auto
from importlib import import_module
from pathlib import Path
from string import Template
from typing import Any

import dominate
import dominate.tags as dom
import dominate.util as dom_util
import panflute as pf

from . import filters, formats, git
from .config import CSS_PATH, IMAGE_PATH, NAV_PATH, SOURCE_PATH, WEB_PATH, logger

# CSS styles (tables, etc.)
# TODO: RSS / Atom feed
# TODO: Titles should be links (possibly with anchor icon)
# TODO: external link icon
# TODO: strip metadata (exiftool -all= file)
# TODO: filters priority
# TODO: automatic post generation
# TODO: Series TOC (next, prev)
# TODO: Site download link
# TODO: Git integration
#   date edited, date created
#   cache builds (-f to force all, use git to detect change)
# TODO: Light / dark theme JS?  (requires re-theming)
# TODO: Printing / reader support
# TODO: Mobile phone support (side bar -> burger menu)
# TODO: Highlight current title in sidebar?
# TODO: compile pdoc to appear on website


PROFILE_IMAGE = "profile.png"
"""Filename for default profile image."""

CHANGELOG_TEMPLATE = "changelog_template.dj"
"""Filename for the changelog template."""


class PageType(Enum):
    """The type of page being made."""

    LATEST = auto()
    CHANGE_LOG = auto()


class DocumentConstructor:
    """Builds the website from source/web files."""

    def __init__(self, source_path: Path, web_path: Path, profile_image: str) -> None:
        self.source_path = source_path
        self.web_path = web_path
        self.profile_image = profile_image

        # Locate all CSS files
        self.css_files = [
            css_file.relative_to(self.web_path) for css_file in (self.web_path / CSS_PATH).glob("**/*.css")
        ]

        # Locate all top-level source paths
        nav_elements = sorted(
            (
                Path("/") / path.with_suffix("").relative_to(self.source_path)
                for path in (self.source_path / NAV_PATH).iterdir()
            ),
            key=lambda path: (path.is_file(), path),
        )
        self.nav_elements = {nav_path.stem.title().replace("_", " "): nav_path for nav_path in nav_elements}
        logger.debug(f"Nav elements: {", ".join(self.nav_elements)}")

        # Locate all filter modules
        self.filter_modules = [
            import_module(module_name)
            for _, module_name, _ in pkgutil.iter_modules(filters.__path__, prefix=f"{filters.__name__}.")
        ]
        filter_names = map(lambda module: module.__name__.removeprefix(f"{filters.__name__}."), self.filter_modules)
        logger.debug(f"Filter modules: {", ".join(filter_names)}")

    def convert_source_to_html(self, source_file: Path) -> tuple[str, dict[str, Any]]:
        """Converts source file to pure html."""
        source_text = source_file.read_text("utf-8", errors="ignore")
        input_format = formats.from_extension(source_file.suffix)

        # Get document tree and apply filters
        document_tree = pf.convert_text(source_text, input_format, standalone=True)
        for filter_module in self.filter_modules:
            document_tree = filter_module.main(document_tree)

        # Return HTML and metadata
        html = pf.convert_text(
            document_tree,
            input_format="panflute",
            output_format="html",
            extra_args=["--no-highlight", "--metadata=panflute-verbose:True", "--mathml"],
        )
        return html, {key: document_tree.get_metadata(key) for key in document_tree.metadata}

    def generate_source_changelog(self, source_file: Path) -> tuple[str, dict[str, Any]]:
        """Construct a changelog page."""
        year: int | None = None
        full_path = self.source_path / source_file

        # Templates
        commit_list = ""
        commit_list_template = (
            '- `<label><input type="radio" name="changelog" id="radio{radio_id}" {checked}>`{{=html}} '
            '{{={date}=}}{{title="{date_iso}"}} `<a>{text}</a></label>`{{=html}}\n'
        )
        radio_counter = itertools.count()

        diffs = ""
        diff_template = "::: changelog-diff{diff_id}\n\n*Commit*: `{git_hash}`\n\n``` =html\n{html}\n```\n:::\n"
        diff_counter = itertools.count()

        css_selectors = []
        css_selector_template = ".side-by-side:has(#{radio_id}:checked) .{div_id}"

        # Fetch git information for file
        for git_hash, date, subject in git.get_file_commits(full_path):
            # Commit list year
            if year is None or date.year < year:
                year = date.year
                commit_list += f"## {year}\n\n{{.index-list}}\n"

            # Diff
            diff_id = next(diff_counter)
            diffs += diff_template.format(html=git.diff_html(full_path, git_hash), diff_id=diff_id, git_hash=git_hash)

            # Commit list
            radio_id = next(radio_counter)
            commit_list += commit_list_template.format(
                date=date.strftime("%b %d"),
                date_iso=date.isoformat(),
                radio_id=radio_id,
                text=subject,
                checked="" if css_selectors else "checked",
            )
            css_selectors.append(
                css_selector_template.format(radio_id=f"radio{radio_id}", div_id=f"changelog-diff{diff_id}")
            )

        # Create changelog page
        changelog_path = Path(__file__).parent / Path(CHANGELOG_TEMPLATE)
        raw_changelog = Template(changelog_path.read_text("utf-8")).substitute(
            selectors=",\n".join(css_selectors), commit_list=commit_list, diffs=diffs
        )
        changelog_file = (
            self.web_path
            / "changelog"
            / full_path.with_stem(f"{full_path.stem}-changelog")
            .with_suffix(f"{changelog_path.suffix}.txt")
            .relative_to(self.source_path)
        )
        changelog_file.parent.mkdir(parents=True, exist_ok=True)
        changelog_file.write_text(raw_changelog)
        changelog_html, changelog_metadata = self.convert_source_to_html(changelog_file)
        return changelog_html, changelog_metadata

    def generate_page(
        self, html: str, metadata: dict[str, Any], source_file: Path, page_type: PageType = PageType.LATEST
    ) -> str:
        """Add document and navbar html."""

        title = metadata.get("title", metadata.get("auto-title", "Page"))
        page = dominate.document(title=f"/{title}/", lang="en")

        # HTML Head
        with page.head:
            dom.meta(charset="utf-8")
            for css_file in self.css_files:
                dom.link(rel="stylesheet", type="text/css", href=Path("/") / css_file)

        # HTML Body
        with page.body:
            # Generate Navbar
            dom.div(cls="NavBackground")
            with dom.div():
                with dom.nav():
                    dom.img(cls="ProfileImage", src=Path("/") / IMAGE_PATH / self.profile_image, alt="Profile Image")
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
                            dom.img(cls="Banner", src=Path("/") / IMAGE_PATH / banner_name, alt="Banner")
                    # Insert post
                    with dom.div(cls="Post-parent"):
                        with dom.div(cls="Post"):
                            dom_util.raw(html)
                        with dom.footer():
                            with dom.p():
                                match page_type:
                                    case PageType.LATEST:
                                        dom.a("Source", href=source_file.with_suffix(f"{source_file.suffix}.txt").name)
                                        dom_util.text(" | ")
                                        dom.a("Change log", href="/changelog" / source_file.with_suffix(""))
                                    case PageType.CHANGE_LOG:
                                        dom.a(
                                            "Source",
                                            href=source_file.with_stem(f"{source_file.stem}-changelog")
                                            .with_suffix(f"{source_file.suffix}.txt")
                                            .name,
                                        )
                                        dom_util.text(" | ")
                                        dom.a(
                                            "Latest",
                                            href="/" / source_file.with_suffix("").relative_to("changelog"),
                                        )
        return str(page)

    def write_source_html(self, html: str, source_file: Path) -> None:
        """Write HTML based on source path."""
        # Write HTML
        html_path = self.web_path / source_file.with_suffix(".html")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, "utf-8")

    def generate_website(self) -> None:
        """Convert all files in source path."""
        total_start_time = time.perf_counter()
        files_converted = 0
        for dirpath, _dirnames, filenames in self.source_path.walk():
            for source_file in filenames:
                full_source_file = (dirpath / source_file).relative_to(self.source_path)
                logger.info(f"Converting {source_file}")

                # Generate page
                start_time = time.perf_counter()
                try:
                    article_html, article_metadata = self.convert_source_to_html(self.source_path / full_source_file)
                    document_html = self.generate_page(article_html, article_metadata, full_source_file)
                    self.write_source_html(document_html, full_source_file)
                    shutil.copyfile(  # Copy raw file over
                        self.source_path / full_source_file,
                        self.web_path / full_source_file.with_suffix(f"{full_source_file.suffix}.txt"),
                    )
                except RuntimeError as e:
                    logger.error(f"  Failed: {e}")
                logger.debug(f"Execution time: {time.perf_counter() - start_time:.2f} seconds")

                # Generate changelog
                start_time = time.perf_counter()
                changelog_path = Path("changelog") / full_source_file
                try:
                    changelog_html, changelog_metadata = self.generate_source_changelog(full_source_file)
                    changelog_document = self.generate_page(
                        changelog_html, changelog_metadata, changelog_path, PageType.CHANGE_LOG
                    )
                    self.write_source_html(changelog_document, changelog_path)
                except RuntimeError as e:
                    logger.error(f"  Failed: {e}")
                logger.debug(f"Changelog time: {time.perf_counter() - start_time:.2f} seconds")

                files_converted += 1
        logger.info(f"Converted {files_converted} files in {time.perf_counter() - total_start_time:.2f} seconds")


def main(source_path: Path | None = None, web_path: Path | None = None, profile_image: str | None = None) -> None:
    """Generate the website."""
    if source_path is None:
        source_path = SOURCE_PATH
    if web_path is None:
        web_path = WEB_PATH
    if profile_image is None:
        profile_image = PROFILE_IMAGE
    document_constructor = DocumentConstructor(source_path, web_path, profile_image)
    document_constructor.generate_website()


if __name__ == "__main__":
    main()
