"""Property tests with Hypothesis: gribkit with random and corrupted input.

The input (``.idx`` inventories, GRIB headers) comes from external sources such as NOAA or GDEX.
Invalid input may only lead to ``IdxParseError`` or ``HeaderError``, never to other exceptions
or silently wrong ranges. The fuzzer in ``fuzz/`` checks the same functions for longer and with
coverage-guided input.
"""

from __future__ import annotations

import contextlib
from functools import cache
from itertools import pairwise

from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from gribkit import HeaderError, find_boundary, parse_head
from gribkit.headers import HEAD_BYTES, entry, idx_line
from gribkit.idx import IdxEntry, IdxParseError, merge_ranges, parse_idx
from gribkit.testing import make_global_message

# Fields without colons and line breaks, as found in .idx lines
_field = st.text(
    alphabet=st.characters(blacklist_characters=":\r\n\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"),
    max_size=20,
).map(str.strip)


@cache
def _message() -> bytes:
    msg, _, _ = make_global_message(inc=10.0)
    return bytes(msg)


@st.composite
def _entries(draw: st.DrawFn) -> list[IdxEntry]:
    """Valid entries with ascending offsets, as in a real ``.idx`` file."""
    gaps = draw(st.lists(st.integers(1, 10**9), min_size=1, max_size=40))
    offset = draw(st.integers(0, 10**6))
    out = []
    for i, gap in enumerate(gaps, start=1):
        out.append(
            IdxEntry(
                str(i),
                offset,
                gap,
                draw(st.from_regex(r"\A[0-9]{10}\Z")),
                draw(_field.filter(bool)),
                draw(_field),
                draw(_field).rstrip(":"),
            )
        )
        offset += gap
    return out


@given(st.text(max_size=2000), st.one_of(st.none(), st.integers(-(10**12), 10**12)))
@example("1:0:d=2026010100:TMP:2 m above ground:anl:\n2:-5:d=x:A:B:C:", None)
@example("1:10:d=:A:B:C:\n2:10:d=:A:B:C:", 10)
def test_parse_idx_arbitrary_text(text: str, size: int | None) -> None:
    """Arbitrary text yields entries with a positive length or ``IdxParseError``.

    @relation(SWR-GRIB-008, scope=function)
    """
    try:
        entries = parse_idx(text, size)
    except IdxParseError:
        return
    for e in entries:
        assert e.length is None or e.length > 0


@given(_entries())
def test_parse_idx_roundtrip(entries: list[IdxEntry]) -> None:
    """Written ``.idx`` lines read back with the same values.

    @relation(SWR-GRIB-008, scope=function)
    """
    size = (entries[-1].end or 0) + 1
    text = "\n".join(idx_line(e) for e in entries)
    assert parse_idx(text, size) == entries


@given(_entries(), st.data(), st.integers(0, 10**9))
def test_merge_ranges_covers_exactly_the_selection(
    entries: list[IdxEntry], data: st.DataObject, gap_size: int
) -> None:
    """Ranges do not overlap, are sorted and extract exactly the selected messages.

    @relation(SWR-GRIB-008, scope=function)
    """
    selection = data.draw(st.lists(st.sampled_from(entries), unique=True))
    ranges = merge_ranges(selection, max_gap=gap_size)
    for a, b in pairwise(ranges):
        assert a.end is not None and a.end < b.start
    covered = [e for r in ranges for e in r.entries]
    assert sorted(e.offset for e in covered) == sorted({e.offset for e in selection})
    for r in ranges:
        for e in r.entries:
            assert r.start <= e.offset and e.end is not None and r.end is not None
            assert e.end <= r.end
        # Extracting from bytes that encode their position yields exactly the messages
        if r.length is not None and r.length <= 4096:
            data_bytes = bytes((r.start + i) % 251 for i in range(r.length))
            expected = b"".join(
                bytes((e.offset + i) % 251 for i in range(e.length or 0)) for e in r.entries
            )
            assert r.extract(data_bytes) == expected


@given(st.binary(max_size=HEAD_BYTES))
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_parse_head_arbitrary_bytes(data_bytes: bytes) -> None:
    """Arbitrary bytes yield a header or ``HeaderError``.

    @relation(SWR-GRIB-008, scope=function)
    """
    for complete in (False, True):
        with contextlib.suppress(HeaderError):
            parse_head(data_bytes, complete=complete)


@given(st.data())
@settings(max_examples=300, deadline=None)  # building the first message with eccodes is slow
def test_parse_head_corrupted_message(data: st.DataObject) -> None:
    """A real message with corrupted or truncated bytes yields a header or ``HeaderError``.

    @relation(SWR-GRIB-008, scope=function)
    """
    msg = bytearray(_message()[:HEAD_BYTES])
    for _ in range(data.draw(st.integers(1, 8))):
        pos = data.draw(st.integers(0, len(msg) - 1))
        msg[pos] = data.draw(st.integers(0, 255))
    msg = msg[: data.draw(st.integers(0, len(msg)))]
    for complete in (False, True):
        try:
            head = parse_head(bytes(msg), complete=complete)
        except HeaderError:
            continue
        idx_line(entry(1, 0, head, "2026010100"))


def _with_section4(sec4_body: bytes) -> bytes:
    """Real message up to section 3, followed by a section 4 with arbitrary content."""
    msg = _message()
    pos = 16
    while msg[pos + 4] != 4:
        pos += int.from_bytes(msg[pos : pos + 4], "big")
    return msg[:pos] + (len(sec4_body) + 5).to_bytes(4, "big") + b"\x04" + sec4_body


@given(st.binary(min_size=29, max_size=120))
@settings(max_examples=500, deadline=None)
@example(bytes(2) + b"\x00\x08" + bytes(8) + b"\x01" + bytes(16))  # template 4.8, too short
@example(bytes(2) + b"\x00\x0b" + bytes(8) + b"\x01" + bytes(16))  # template 4.11, too short
def test_parse_head_arbitrary_section4(body: bytes) -> None:
    """Arbitrary product definition content (section 4, all templates) yields a header or
    ``HeaderError``.

    @relation(SWR-GRIB-008, scope=function)
    """
    data_bytes = _with_section4(body)
    for complete in (False, True):
        with contextlib.suppress(HeaderError):
            parse_head(data_bytes, complete=complete)


@given(st.binary(max_size=512), st.integers(0, 10**12))
@example(b"7777GRIB" + bytes(8), 10**6)
def test_find_boundary_arbitrary_bytes(chunk: bytes, size_left: int) -> None:
    """A boundary that is found points to ``GRIB`` after ``7777`` and fits into the file.

    @relation(SWR-GRIB-008, scope=function)
    """
    pos = find_boundary(chunk, size_left)
    if pos is not None:
        assert chunk[pos - 4 : pos + 4] == b"7777GRIB"
        assert pos + 16 <= len(chunk) and pos < size_left
