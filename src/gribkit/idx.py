"""Parser for NCEP inventory files (``.idx``) and construction of byte ranges.

An ``.idx`` line has the form::

    581:415092545:d=2026102006:TMP:2 m above ground:42 hour fcst:

The length of a message follows from the offset of the next line. For the
last message the length is only known if the file size is passed; otherwise
it stays open (``Range: bytes=<offset>-``).

@relation(SWA-GRIB-IDX, scope=file)
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import pairwise


@dataclass(frozen=True, slots=True)
class IdxEntry:
    """One message from an ``.idx`` file."""

    number: str
    offset: int
    length: int | None
    date: str
    var: str
    level: str
    fcst: str

    @property
    def end(self) -> int | None:
        """Last byte (inclusive), or ``None`` if unknown."""
        return None if self.length is None else self.offset + self.length - 1

    @property
    def key(self) -> str:
        """``VAR:LEVEL:FCST``, as printed by wgrib2."""
        return f"{self.var}:{self.level}:{self.fcst}"


@dataclass(frozen=True, slots=True)
class MessageSpec:
    """Selection of a message by short name and level.

    ``fcst`` is an optional regular expression on the forecast field of the
    ``.idx`` line, e.g. ``"ave"`` for averages. Without ``fcst``, all messages
    with a matching ``VAR:LEVEL`` are selected (for GFS ``TCDC``, for example,
    both the instantaneous value and the interval average).

    @relation(SWR-GRIB-002, scope=class)
    """

    var: str
    level: str
    fcst: str | None = None

    def matches(self, entry: IdxEntry) -> bool:
        if entry.var != self.var or entry.level != self.level:
            return False
        return self.fcst is None or re.search(self.fcst, entry.fcst) is not None

    @property
    def label(self) -> str:
        return f"{self.var}:{self.level}" + (f":{self.fcst}" if self.fcst else "")


@dataclass(frozen=True, slots=True)
class ByteRange:
    """Contiguous byte range (``end`` inclusive, ``None`` = to the end of the file)."""

    start: int
    end: int | None
    entries: tuple[IdxEntry, ...]

    @property
    def header(self) -> str:
        return f"bytes={self.start}-" + ("" if self.end is None else str(self.end))

    @property
    def length(self) -> int | None:
        return None if self.end is None else self.end - self.start + 1

    def extract(self, data: bytes) -> bytes:
        """Cut only the selected messages out of the downloaded bytes
        (merged ranges contain unselected messages in between).

        @relation(SWR-GRIB-003, scope=function)
        """
        if self.length is not None and len(data) != self.length:
            raise ValueError(f"{self.header}: got {len(data)} bytes, expected {self.length}")
        parts = []
        for e in self.entries:
            lo = e.offset - self.start
            parts.append(data[lo:] if e.length is None else data[lo : lo + e.length])
        return b"".join(parts)


class IdxParseError(ValueError):
    """@relation(SWR-GRIB-001, scope=class)"""

    pass


def parse_idx(text: str, total_size: int | None = None) -> list[IdxEntry]:
    """Read an ``.idx`` file. Sub-messages (``12.1``, ``12.2``) share an offset
    and therefore the same byte range.

    @relation(SWR-GRIB-001, SWR-GRIB-008, scope=function)
    """
    rows: list[tuple[str, int, str, str, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")
        if len(parts) < 6:
            raise IdxParseError(f"Line {lineno}: too few fields: {line!r}")
        try:
            offset = int(parts[1])
        except ValueError as exc:
            raise IdxParseError(f"Line {lineno}: offset is not a number: {line!r}") from exc
        number, _, date, var, level = parts[:5]
        fcst = ":".join(parts[5:]).rstrip(":")
        rows.append((number, offset, date.removeprefix("d="), var, level, fcst))

    offsets = sorted({r[1] for r in rows})
    next_offset = dict(pairwise(offsets))
    if total_size is not None and offsets:
        if total_size <= offsets[-1]:
            raise IdxParseError("File size is before the last offset")
        next_offset[offsets[-1]] = total_size

    entries = []
    for number, offset, date, var, level, fcst in rows:
        nxt = next_offset.get(offset)
        entries.append(
            IdxEntry(number, offset, None if nxt is None else nxt - offset, date, var, level, fcst)
        )
    return entries


def select(entries: Iterable[IdxEntry], specs: Sequence[MessageSpec]) -> list[IdxEntry]:
    """All entries that match at least one spec (in file order).

    @relation(SWR-GRIB-002, scope=function)
    """
    return [e for e in entries if any(s.matches(e) for s in specs)]


def missing_specs(entries: Iterable[IdxEntry], specs: Sequence[MessageSpec]) -> list[MessageSpec]:
    """Specs without a match, e.g. accumulated fields in the analysis step f000.

    @relation(SWR-GRIB-002, scope=function)
    """
    entries = list(entries)
    return [s for s in specs if not any(s.matches(e) for e in entries)]


def merge_ranges(entries: Iterable[IdxEntry], max_gap: int = 0) -> list[ByteRange]:
    """Merge the selected messages into as few byte ranges as possible.

    Messages with the same offset (sub-messages) are downloaded only once. If
    two ranges are at most ``max_gap`` bytes apart, they are merged (the gap is
    downloaded and discarded).

    @relation(SWR-GRIB-003, SWR-GRIB-008, scope=function)
    """
    unique: dict[int, IdxEntry] = {}
    for e in sorted(entries, key=lambda e: e.offset):
        unique.setdefault(e.offset, e)

    ranges: list[ByteRange] = []
    for e in unique.values():
        if ranges:
            last = ranges[-1]
            if last.end is not None and e.offset - (last.end + 1) <= max_gap:
                ranges[-1] = ByteRange(last.start, e.end, (*last.entries, e))
                continue
        ranges.append(ByteRange(e.offset, e.end, (e,)))
    return ranges
