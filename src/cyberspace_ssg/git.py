"""Provide basic access to git functions."""

import datetime
import itertools
import shlex
import subprocess
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import dominate.tags as dom
import dominate.util as dom_util

from . import formats
from .config import logger


@dataclass
class Commit:
    """Commit information."""

    def __init__(self, commit_string: str) -> None:
        self.hash_id, date_string, subject_body = commit_string[1:-1].split(",", 2)
        self.date = datetime.datetime.fromisoformat(date_string)
        self.subject, _, self.body = subject_body.partition("\n")


@cache
def load_git_data() -> dict[Path, list[Commit]]:
    """Get all diffs for all commits."""

    # Fetch all commits, separated by NUL, filtering for supported extensions
    extensions = " ".join(map(lambda extension: f'"*{extension}"', formats.supported_formats()))
    all_commits = subprocess.run(
        shlex.split(f"git log --pretty=%x00%H,%aI,%s%n%b -z -p --word-diff=porcelain -- {extensions}"),
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    ).stdout.split(chr(0))[1:]
    logger.debug(f"Found {len(all_commits) // 2} commits")

    # Map paths to a list of diffs
    path_map: dict[Path, list[tuple[Commit, str]]] = {}
    for commit_data_string, all_diffs in itertools.batched(all_commits, 2):
        commit_data = Commit(commit_data_string)  # Create commit object to avoid duplication
        for diff in all_diffs.split("\ndiff")[1:]:
            diff_lines = diff.splitlines()

            # Process header
            old_path = new_path = None
            while not diff_lines[0].startswith("@@ "):  # Find first header
                if diff_lines[0].startswith("--- a/"):  # Get old path name
                    old_path = diff_lines[0].removeprefix("--- a/")
                elif diff_lines[0].startswith("+++ b/"):  # Get new path name
                    new_path = diff_lines[0].removeprefix("+++ b/")
                diff_lines.pop(0)

            # Convert diff to html
            html_result = ""
            with dom.div(cls="highlight") as diff_div:
                with dom.pre(cls="diff"):
                    dom.p(diff_lines[0], cls="diff-header")
                    with dom.p(cls="diff-content"):
                        for line in diff_lines[1:]:
                            match line[:1]:
                                case " ":  # Unmodified
                                    dom_util.text(line[1:])
                                case "+":  # Insertion
                                    dom.ins(line[1:])
                                case "-":  # Deletion
                                    dom.del_(line[1:])
                                case "~":  # Newline
                                    dom_util.text("\n")
            html_result += diff_div.render()
            if new_path:
                path_map.setdefault(new_path, []).append((commit_data, html_result))
            if old_path and old_path != new_path:
                path_map.setdefault(old_path, []).append((commit_data, html_result))
    return path_map


def get_file_commits(file_path: Path) -> list[tuple[Commit, str]]:
    """Get a files commits."""

    return load_git_data().get(file_path.as_posix(), [])
