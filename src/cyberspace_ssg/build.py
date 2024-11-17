"""Build a static website."""

import concurrent.futures
import itertools
import pkgutil
import shutil
import time
import traceback
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path
from string import Template
from typing import Any, Iterator

import dominate
import dominate.tags as dom
import dominate.util as dom_util
import panflute as pf

from . import config, filters, formats, git
from .cache import cache_miss
from .config import logger


class SiteConstructor:
    """Generate data for use by the site templates."""

    def __new__(cls) -> None:
        """Destroy the instance after initialization."""
        instance = super().__new__(cls)
        instance.__init__()

    def __init__(self) -> None:
        self.source_path = config.SOURCE_PATH
        self.web_path = config.WEB_PATH
        self.profile_image = config.PROFILE_IMAGE

        # Locate all CSS files
        self.css_files = [
            css_file.relative_to(self.web_path) for css_file in (self.web_path / config.CSS_PATH).glob("**/*.css")
        ]

        # Locate all top-level source paths
        self.nav_elements = sorted(
            (
                Path("/") / path.with_suffix("").relative_to(self.source_path)
                for path in (self.source_path / config.NAV_PATH).iterdir()
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

        # Return HTML and metadata
        html = pf.convert_text(
            document_tree,
            input_format="panflute",
            output_format="html",
            extra_args=["--no-highlight", "--mathml"],
        )
        return html, {key: document_tree.get_metadata(key) for key in document_tree.metadata}

    def generate_source_changelog(self, relative_file_path: Path) -> tuple[str, dict[str, Any]]:
        """Construct a changelog page."""
        year: int | None = None
        full_path = self.source_path / relative_file_path

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
        changelog_file = self.web_path / self.changelog_name(relative_file_path).with_suffix(
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
                    dom.img(cls="ProfileImage", src=config.IMAGE_PATH / self.profile_image)
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
                                    dom_util.text(" | ")
                                    dom.a(
                                        "Change log",
                                        href=self.changelog_name(file_name).with_suffix(""),
                                    )
        return page.render()

    def write_html(self, relative_file_path: Path, changelog: bool = False) -> None:
        """Generate and write HTML based on file path."""

        # Generate HTML
        if changelog:
            article_html, metadata = self.generate_source_changelog(relative_file_path)
            html_path = self.web_path / self.changelog_name(relative_file_path).with_suffix(".html")
        else:
            source_path = self.source_path / relative_file_path
            source_text = source_path.read_text("utf-8", errors="ignore")
            input_format = formats.from_extension(relative_file_path.suffix)
            article_html, metadata = self.convert_source_to_html(source_text, input_format, source_path)
            html_path = self.web_path / relative_file_path.with_suffix(".html")
        document_html = self.generate_page(article_html, metadata, Path(relative_file_path.name), changelog)

        # Write HTML
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(document_html, "utf-8")

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
                self.write_html(relative_file_path)
                shutil.copyfile(  # Copy raw file over
                    self.source_path / relative_file_path,
                    self.web_path / relative_file_path.with_suffix(f"{relative_file_path.suffix}.txt"),
                )

            # Generate changelog
            with timer("Changelog"):
                self.write_html(relative_file_path, True)
        except RuntimeError as e:
            logger.error(f"  Failed: {e}")

    def batch_process_files(self) -> None:
        """Convert all files in source path."""
        total_start_time = time.perf_counter()
        futures = []
        git.load_git_data()

        # Spawn threads
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for dirpath, _dirnames, filenames in self.source_path.walk():
                for source_file in filenames:
                    full_path = dirpath / source_file
                    if cache_miss(full_path):
                        futures.append(
                            executor.submit(self.process_file, dirpath.relative_to(self.source_path) / source_file)
                        )

        # Check for exceptions
        for future in futures:
            if exception := future.exception():
                logger.error("".join(traceback.format_exception(exception)))

        logger.info(f"Converted {len(futures)} files in {time.perf_counter() - total_start_time:.2f} seconds")


def main() -> None:
    """Generate the website."""
    SiteConstructor()


if __name__ == "__main__":
    main()
