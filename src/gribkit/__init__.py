"""Tools for GRIB2 partial downloads.

The modules (``idx``, ``headers``, ``grib``, ``bbox``, ``testing``) are imported with the
history from PredictionDB; this file only provides the package skeleton until then.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gribkit")
except PackageNotFoundError:  # pragma: no cover - only when run from a source tree
    __version__ = "0.0.0"

__all__ = ["__version__"]
