# CLAUDE.md – gribkit

This is the standalone **gribkit** repository (GitHub `the78mole/gribkit`, public, PyPI `gribkit`).
It contains no code yet, only the handover from the PredictionDB project. The full assignment is
in [`docs/HANDOVER.md`](docs/HANDOVER.md), the sequence of steps in [`docs/BRIEF.md`](docs/BRIEF.md)
and Daniel's repo conventions in [`docs/templates/CONVENTIONS.md`](docs/templates/CONVENTIONS.md).
Read the handover in full before changing anything.

## Summary

gribkit is a small Python library for GRIB2 partial downloads (read NCEP `.idx` files, select
messages, merge byte ranges, parse message headers without ecCodes, crop GRIB2 to a region with
ecCodes). It was created in `the78mole/PredictionDB` under `packages/gribkit` and moves to this
repository with its Git history, under the **MIT** license, and gets published on PyPI. After that,
PredictionDB consumes gribkit from PyPI.

## Working rules

- **Language:** Talk to the user (Daniel, GitHub `the78mole`) in German. Everything in the
  repository and on PyPI is in **English**: README, docs, docstrings, comments, identifiers, file
  names, commit messages, changelog.
- **Tools:** Python with `uv` (no pip/poetry), build backend `hatchling`, Ruff (line length 100,
  rules `E,F,W,I,UP,B,SIM,RUF,DTZ`), mypy `strict`, pytest, pre-commit with local hooks via
  `uv run --no-sync` (as in PredictionDB).
- **Python:** `>=3.12`, tested on 3.12–3.14. **No 3.15** until `eccodeslib` ships matching wheels
  (upstream issue https://github.com/ecmwf/eccodes/issues/629).
- **Commits:** Conventional Commits, with `Signed-off-by` (`git commit -s`).
- **Releases:** Every commit on `main` produces a release, including a PyPI publish, once the
  release workflow is in place (see `docs/HANDOVER.md`, section 5). Treat a merge to `main` as a
  publication.
- **No changes to PredictionDB without agreement:** Switching PredictionDB to the PyPI package is a
  separate PR in `the78mole/PredictionDB`, and only after the first PyPI release.
- **Do not bring along:** No company or customer names from the user's environment; ask when in
  doubt. No code from other PredictionDB packages (core, services, ml_train, predict).
- **Approvals:** Setting up the PyPI Trusted Publisher and publishing the first release are
  externally visible and hard to undo. Ask the user first unless they explicitly requested it.

## Quick start (after the import)

```bash
uv sync
uv run pytest
uv run pre-commit run --all-files
uv run --group fuzz python fuzz/gribkit_fuzz.py idx -max_total_time=60 fuzz/corpus/idx   # Linux x86_64 only
```
