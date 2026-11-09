# gribkit

[![CI](https://github.com/the78mole/gribkit/actions/workflows/ci.yml/badge.svg)](https://github.com/the78mole/gribkit/actions/workflows/ci.yml)
[![Release](https://github.com/the78mole/gribkit/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/the78mole/gribkit/actions/workflows/pypi-publish.yml)
[![PyPI](https://img.shields.io/pypi/v/gribkit?label=gribkit)](https://pypi.org/project/gribkit/)
[![Python versions](https://img.shields.io/pypi/pyversions/gribkit)](https://pypi.org/project/gribkit/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/the78mole/gribkit/badge)](https://scorecard.dev/viewer/?uri=github.com/the78mole/gribkit)
[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

A small, typed Python library for **GRIB2 partial downloads**. Instead of fetching a whole
500 MB forecast file, read its inventory, pick the messages you need, download only their byte
ranges and crop them to your region.

- **Read NCEP `.idx` inventories** (`parse_idx`) as published next to GFS, GEFS and other NCEP
  products, including sub-messages (`12.1`, `12.2`) that share a byte range.
- **Select messages** by `VAR:LEVEL` with an optional regular expression on the forecast field
  (`MessageSpec`, `select`, `missing_specs`).
- **Merge byte ranges** into as few HTTP requests as possible, optionally bridging small gaps
  (`merge_ranges`, `ByteRange.extract`).
- **Parse GRIB2 message headers without ecCodes** (`parse_head`, `find_boundary`) and generate
  `.idx` lines in the style of `wgrib2 -s`, so you can build an inventory for archives that do not
  publish one.
- **Split and validate** a byte stream into complete GRIB2 messages (`iter_messages`).
- **Crop `regular_ll` messages to a bounding box** with ecCodes (`crop`, `crop_message`, `BBox`),
  also across the prime meridian, keeping the packing type and precision of the source.

## Installation

```bash
pip install gribkit
# or
uv add gribkit
```

gribkit supports **Python 3.12 to 3.15**. It depends on `eccodes`, `eccodeslib` and `numpy`.
On Python 3.15, `eccodeslib` 2.50.0.34 or newer is needed, the first release with cp315 wheels.

Only `crop`, `crop_message` and `describe` use ecCodes. Reading `.idx` files, merging ranges and
parsing headers is pure Python.

## Example: a GFS partial download from AWS

Download 2 m temperature and 10 m wind from a GFS 0.25° forecast on the
[NOAA GFS Open Data bucket](https://registry.opendata.aws/noaa-gfs-bdp-pds/) and crop it to Central
Europe:

```python
import urllib.request

from gribkit import BBox, MessageSpec, crop, merge_ranges, parse_idx, select

url = (
    "https://noaa-gfs-bdp-pds.s3.amazonaws.com/"
    "gfs.20261101/00/atmos/gfs.t00z.pgrb2.0p25.f006"
)

with urllib.request.urlopen(url + ".idx") as resp:
    entries = parse_idx(resp.read().decode())

specs = [
    MessageSpec("TMP", "2 m above ground"),
    MessageSpec("UGRD", "10 m above ground"),
    MessageSpec("VGRD", "10 m above ground"),
]
wanted = select(entries, specs)

data = b""
for rng in merge_ranges(wanted, max_gap=64 * 1024):
    req = urllib.request.Request(url, headers={"Range": rng.header})
    with urllib.request.urlopen(req) as resp:
        if resp.status != 206:
            raise RuntimeError(f"expected 206 Partial Content, got {resp.status}")
        data += rng.extract(resp.read())  # checks the length, drops bridged gaps

europe = crop(data, BBox(north=56.0, south=46.0, west=5.0, east=16.0))
```

### One request per range

The S3 endpoints of AWS and Google Cloud answer multi-range requests
(`Range: bytes=a-b,c-d`) with the **whole file** and status `200`. Request each `ByteRange` from
`merge_ranges` separately, and check for `206 Partial Content` and the expected length
(`ByteRange.extract` raises `ValueError` on a length mismatch). Use `max_gap` to trade a few
wasted bytes for fewer requests.

The length of the last message in an `.idx` file is unknown unless you pass the file size
(`parse_idx(text, total_size=...)`); without it, its range is open-ended (`bytes=<offset>-`).

## Development

gribkit uses [uv](https://docs.astral.sh/uv/), Ruff, mypy (strict) and pytest.

```bash
uv sync
uv run pytest
uv run pre-commit install          # once, sets up the Git hook
uv run pre-commit run --all-files
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for commit conventions and the release process.

## Releases

Every commit on `main` is released: the version is calculated from the Conventional Commit
message (`feat:` bumps the minor version, `!` the major version, everything else the patch
version), tagged, published as a [GitHub Release](https://github.com/the78mole/gribkit/releases)
and uploaded to PyPI with Trusted Publishing. The release notes live on GitHub, see
[CHANGELOG.md](CHANGELOG.md).

## Origin

gribkit was written as part of [PredictionDB](https://github.com/the78mole/PredictionDB), where it
loads GFS and GEFS forecasts, and moved to this repository with its Git history to be useful on its
own.

## License

gribkit is licensed under the [MIT License](LICENSE).

The NCEP parameter table `src/gribkit/ncep_parameters.json` (GRIB2 Code Table 4.2 with wgrib2-style
short names) is derived from [grib2io](https://github.com/NOAA-MDL/grib2io) 2.8.2, Copyright (c)
2021 NOAA / National Weather Service, MIT License. See [NOTICE](NOTICE).
