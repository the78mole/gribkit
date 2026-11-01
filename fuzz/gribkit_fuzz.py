"""Atheris fuzzer for the parsers in gribkit.

One target per call, the input is an arbitrary byte stream:

    uv run --group fuzz python fuzz/gribkit_fuzz.py idx  -max_total_time=300 fuzz/corpus/idx
    uv run --group fuzz python fuzz/gribkit_fuzz.py head -max_total_time=300 fuzz/corpus/head

Only the intended errors ``IdxParseError`` and ``HeaderError`` are allowed. Any other exception
aborts the run, and libFuzzer writes the input as ``crash-*`` to the working directory. The
property tests in ``tests/test_robustness.py`` check the same properties more briefly on every
pull request.
"""

from __future__ import annotations

import sys
from itertools import pairwise

import atheris

with atheris.instrument_imports():
    from gribkit import HeaderError, find_boundary, parse_head
    from gribkit.headers import entry, idx_line
    from gribkit.idx import IdxParseError, merge_ranges, parse_idx


def fuzz_idx(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    size = fdp.ConsumeIntInRange(0, 2**40) if fdp.ConsumeBool() else None
    gap = fdp.ConsumeIntInRange(0, 2**30)
    text = fdp.ConsumeUnicodeNoSurrogates(fdp.remaining_bytes())
    try:
        entries = parse_idx(text, size)
    except IdxParseError:
        return
    for e in entries:
        if e.length is not None and e.length <= 0:
            raise AssertionError(f"Length {e.length} for {e}")
    ranges = merge_ranges(entries, max_gap=gap)
    for a, b in pairwise(ranges):
        if a.end is None or a.end >= b.start:
            raise AssertionError(f"Ranges overlap: {a.header} {b.header}")


def fuzz_head(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    complete = fdp.ConsumeBool()
    size_left = fdp.ConsumeIntInRange(0, 2**40)
    raw = fdp.ConsumeBytes(fdp.remaining_bytes())
    try:
        head = parse_head(raw, complete=complete)
    except HeaderError:
        pass
    else:
        idx_line(entry(1, 0, head, "2026010100"))
    pos = find_boundary(raw, size_left)
    if pos is not None and raw[pos - 4 : pos + 4] != b"7777GRIB":
        raise AssertionError(f"Boundary {pos} does not point to 7777GRIB")


TARGETS = {"idx": fuzz_idx, "head": fuzz_head}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in TARGETS:
        sys.exit(f"Missing target: {' | '.join(TARGETS)}")
    target = TARGETS[sys.argv.pop(1)]
    atheris.Setup(sys.argv, target)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
