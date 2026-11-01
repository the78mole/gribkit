"""Split GRIB2 messages and crop them to a geographic region.

ecCodes does the decoding and re-encoding. The packing type of the source
(``grid_complex_spatial_differencing`` for GFS) is kept, and so is the
precision through the decimal scale factor.

@relation(SWA-GRIB-GRIB, scope=file)
"""

from __future__ import annotations

import struct
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from gribkit.bbox import BBox

_EPS = 1e-6


class GribError(ValueError):
    """@relation(SWR-GRIB-005, scope=class)"""

    pass


def iter_messages(data: bytes) -> Iterator[bytes]:
    """Split a byte stream into individual GRIB2 messages.

    Checks the ``GRIB`` indicator, edition 2 and the ``7777`` end marker. Bytes
    between messages are not allowed, so truncated downloads are detected.

    @relation(SWR-GRIB-005, scope=function)
    """
    pos = 0
    n = len(data)
    while pos < n:
        if data[pos : pos + 4] != b"GRIB":
            raise GribError(f"No GRIB indicator at byte {pos}")
        if n - pos < 16:
            raise GribError(f"Truncated header at byte {pos}")
        edition = data[pos + 7]
        if edition != 2:
            raise GribError(f"Only GRIB2 is supported, edition {edition} at byte {pos}")
        (length,) = struct.unpack(">Q", data[pos + 8 : pos + 16])
        end = pos + length
        if end > n:
            raise GribError(f"Message at byte {pos} is truncated ({n - pos} of {length} bytes)")
        if data[end - 4 : end] != b"7777":
            raise GribError(f"End marker 7777 missing in message at byte {pos}")
        yield data[pos:end]
        pos = end


@dataclass(frozen=True, slots=True)
class MessageInfo:
    short_name: str
    type_of_level: str
    level: int
    step_range: str
    ni: int
    nj: int


def describe(message: bytes) -> MessageInfo:
    """Read the key metadata of a GRIB2 message with ecCodes."""
    import eccodes as ec

    h = ec.codes_new_from_message(message)
    try:
        return MessageInfo(
            short_name=ec.codes_get(h, "shortName"),
            type_of_level=ec.codes_get(h, "typeOfLevel"),
            level=ec.codes_get(h, "level"),
            step_range=str(ec.codes_get(h, "stepRange")),
            ni=ec.codes_get(h, "Ni"),
            nj=ec.codes_get(h, "Nj"),
        )
    finally:
        ec.codes_release(h)


def _axis(first: float, inc: float, count: int, positive: bool) -> np.ndarray:
    return first + np.arange(count) * (inc if positive else -inc)


def crop_message(message: bytes, bbox: BBox, packing: str | None = None) -> bytes:
    """Crop a ``regular_ll`` message to all grid points inside ``bbox``.

    Longitudes are handled modulo 360, so regions across the prime meridian
    (``west < 0`` on a 0-360° grid) work as well. The output is always scanned
    north to south (like the global GFS files), so the result is uniform
    regardless of the source. ``packing`` optionally sets a different packing
    type (e.g. ``grid_complex_spatial_differencing``).

    @relation(SWR-GRIB-006, SWR-GRIB-007, scope=function)
    """
    import eccodes as ec

    h = ec.codes_new_from_message(message)
    try:
        if ec.codes_get(h, "gridType") != "regular_ll":
            raise GribError(f"Grid type {ec.codes_get(h, 'gridType')!r} is not supported")
        if ec.codes_get(h, "iScansNegatively") or ec.codes_get(h, "jPointsAreConsecutive"):
            raise GribError("Only west-to-east scanning with row-major order is supported")
        ni, nj = ec.codes_get(h, "Ni"), ec.codes_get(h, "Nj")
        di = ec.codes_get(h, "iDirectionIncrementInDegrees")
        dj = ec.codes_get(h, "jDirectionIncrementInDegrees")
        j_pos = bool(ec.codes_get(h, "jScansPositively"))
        lats = _axis(ec.codes_get(h, "latitudeOfFirstGridPointInDegrees"), dj, nj, j_pos)
        lons = _axis(ec.codes_get(h, "longitudeOfFirstGridPointInDegrees"), di, ni, True)

        rows = np.flatnonzero((lats >= bbox.south - _EPS) & (lats <= bbox.north + _EPS))
        rows = rows[np.argsort(-lats[rows], kind="stable")]
        rel = np.mod(lons - bbox.west + _EPS, 360.0) - _EPS
        cols = np.flatnonzero(rel <= bbox.width + _EPS)
        cols = cols[np.argsort(rel[cols], kind="stable")]
        if rows.size == 0 or cols.size == 0:
            raise GribError(f"Region {bbox} contains no grid points")

        values = ec.codes_get_values(h).reshape(nj, ni)
        sub = values[np.ix_(rows, cols)]

        out = ec.codes_clone(h)
        try:
            ec.codes_set(out, "Ni", int(cols.size))
            ec.codes_set(out, "Nj", int(rows.size))
            ec.codes_set(out, "jScansPositively", 0)
            ec.codes_set(out, "latitudeOfFirstGridPointInDegrees", float(lats[rows[0]]))
            ec.codes_set(out, "latitudeOfLastGridPointInDegrees", float(lats[rows[-1]]))
            ec.codes_set(
                out, "longitudeOfFirstGridPointInDegrees", float(np.mod(lons[cols[0]], 360.0))
            )
            ec.codes_set(
                out, "longitudeOfLastGridPointInDegrees", float(np.mod(lons[cols[-1]], 360.0))
            )
            if packing and ec.codes_get(out, "packingType") != packing:
                ec.codes_set(out, "packingType", packing)
            ec.codes_set_values(out, sub.ravel())
            return bytes(ec.codes_get_message(out))
        finally:
            ec.codes_release(out)
    finally:
        ec.codes_release(h)


def crop(data: bytes, bbox: BBox, packing: str | None = None) -> bytes:
    """Crop all messages of a GRIB2 byte stream.

    @relation(SWR-GRIB-006, scope=function)
    """
    return b"".join(crop_message(m, bbox, packing) for m in iter_messages(data))
