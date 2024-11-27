"""Manage file cache. A shelf is used to simplify use."""

import csv
import json
from dataclasses import dataclass, field
from enum import Enum, member
from functools import cache
from hashlib import blake2b
from pathlib import Path
from typing import Any

from . import config
from .config import logger

CACHE_FILE = Path("build_cache.csv")


@dataclass
class CacheData:
    """The data cached during a build."""

    file_hash: str
    """A hash to detect file modifications."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """The document metadata."""


type CacheDatabase = dict[Path, CacheData]


class InvalidationMode(Enum):
    """
    Methods for generating a file "hash". We need to determine if a file has been modified or not.
    These methods receive a file path, and return some hash string that changes with file modification.
    """

    @member
    @staticmethod
    def always(_file_path: Path) -> str:
        """Always invalidate cache."""
        return ""

    @member
    @staticmethod
    def timestamp(file_path: Path) -> str:
        """Use the modified time and file size."""
        return str((file_path.stat().st_mtime, file_path.stat().st_size))

    @member
    @staticmethod
    def hashing(file_path: Path) -> str:
        """Use an 8 byte hash generated from the file contents."""
        return blake2b(file_path.read_bytes(), digest_size=8).hexdigest()

    def __call__(self, file_path: Path) -> str:
        """Allow the use of method() instead of method.value()."""
        return self.value(file_path)


@cache
def load_cache() -> CacheDatabase:
    """Load cache file once."""
    try:
        with open(CACHE_FILE, mode="r+", newline="", encoding="utf-8") as csv_file:
            return {Path(row[0]): CacheData(row[1], json.loads(row[2])) for row in csv.reader(csv_file)}
    except FileNotFoundError:
        return {}


def sync_cache(database: CacheDatabase) -> None:
    """Write cache back to file."""
    with open(CACHE_FILE, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        for path, cache_data in database.items():
            csv_writer.writerow([path, cache_data.file_hash, json.dumps(cache_data.metadata)])


def cache_miss(file_path: Path) -> bool:
    """Check if a file is cached and valid."""

    # Calculate expected hash
    cache_mode = InvalidationMode[config.INVALIDATION_MODE]
    file_hash = cache_mode(file_path)

    # Check for cache hit
    cache_database = load_cache()
    cache_data = cache_database.get(file_path)
    if cache_data and cache_data.file_hash == file_hash:  # Hit
        logger.info(f"No work for {file_path}")
        return False

    # Miss, update cache
    cache_database[file_path] = CacheData(file_hash)
    sync_cache(cache_database)
    return True
