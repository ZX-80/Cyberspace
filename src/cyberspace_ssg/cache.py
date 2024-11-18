"""Manage file cache. A shelf is used to simplify use."""

import shelve
from enum import Enum, member
from functools import cache
from hashlib import blake2b
from pathlib import Path

from . import config
from .config import logger

CACHE_NAME = "build_cache"


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
def load_cache() -> dict:
    """Load cache file once."""
    return shelve.open(CACHE_NAME)


def cache_miss(file_path: Path | str) -> bool:
    """Check if a file is cached and valid."""

    # Calculate expected metadata
    cache_mode = InvalidationMode[config.INVALIDATION_MODE]
    file_path = Path(file_path)  # Convert to path
    file_metadata = cache_mode(file_path)

    # Check for cache hit
    cache_database = load_cache()
    cache_metadata = cache_database.get(str(file_path))
    if cache_metadata and cache_metadata == file_metadata:  # Hit
        logger.info(f"No work for {file_path}")
        return False

    # Miss, update cache
    cache_database[str(file_path)] = file_metadata
    cache_database.sync()
    return True
