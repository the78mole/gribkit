"""Smoke tests for the package metadata."""

from importlib.resources import files

import gribkit


def test_version_is_set() -> None:
    assert gribkit.__version__
    assert gribkit.__version__ != "0.0.0"


def test_package_is_typed() -> None:
    assert files("gribkit").joinpath("py.typed").is_file()
