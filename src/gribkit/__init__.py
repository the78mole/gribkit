"""GRIB2-Werkzeuge für Partial Downloads."""

from importlib.metadata import PackageNotFoundError, version

from gribkit.bbox import BBox
from gribkit.grib import GribError, crop, crop_message, describe, iter_messages
from gribkit.headers import HeaderError, find_boundary, parse_head
from gribkit.idx import (
    ByteRange,
    IdxEntry,
    IdxParseError,
    MessageSpec,
    merge_ranges,
    missing_specs,
    parse_idx,
    select,
)

try:
    __version__ = version("gribkit")
except PackageNotFoundError:  # pragma: no cover - only when run from a source tree
    __version__ = "0.0.0"

__all__ = [
    "BBox",
    "ByteRange",
    "GribError",
    "HeaderError",
    "IdxEntry",
    "IdxParseError",
    "MessageSpec",
    "__version__",
    "crop",
    "crop_message",
    "describe",
    "find_boundary",
    "iter_messages",
    "merge_ranges",
    "missing_specs",
    "parse_head",
    "parse_idx",
    "select",
]
