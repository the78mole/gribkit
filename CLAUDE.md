# CLAUDE.md – gribkit

**gribkit** (GitHub `the78mole/gribkit`, public, PyPI `gribkit`) is a small, typed Python library
for GRIB2 partial downloads: read NCEP `.idx` files, select messages, merge byte ranges, parse
message headers without ecCodes and crop GRIB2 to a region with ecCodes. It was created in
`the78mole/PredictionDB` and moved here with its Git history under the MIT license. How and why
is recorded in [`docs/history/HANDOVER.md`](docs/history/HANDOVER.md).

## Working rules

- **Language:** Talk to the user (Daniel, GitHub `the78mole`) in German. Everything in the
  repository and on PyPI is in **English**: README, docs, docstrings, comments, identifiers, file
  names, commit messages.
- **Tools:** Python with `uv` (no pip/poetry), build backend `hatchling`, Ruff (line length 100,
  rules `E,F,W,I,UP,B,SIM,RUF,DTZ`), mypy `strict`, pytest with Hypothesis, pre-commit with local
  hooks via `uv run --no-sync`. Assess every Ruff finding; ignore deliberate patterns with a
  comment giving the reason, never switch rules off wholesale.
- **Python:** `>=3.12`, tested on 3.12–3.14. **No 3.15** until `eccodeslib` ships matching wheels
  (https://github.com/ecmwf/eccodes/issues/629). Renovate holds the runtime at 3.14.x.
- **CI:** Actions are pinned by SHA (OpenSSF Scorecard), runners by version (`ubuntu-26.04`);
  Renovate keeps both current. Look up current versions before adding an action, never copy them
  from memory.
- **Commits:** Conventional Commits, with `Signed-off-by` (`git commit -s`). PRs are squash-merged,
  so the **PR title** is the commit on `main`.
- **Releases:** Every commit on `main` is a release: `pypi-publish.yml` calculates the version from
  the subject (`feat:` minor, `!` major, else patch), runs CI, publishes to PyPI with Trusted
  Publishing (environment `pypi`) and creates the GitHub Release. Treat a merge to `main` as a
  publication. The publish job must stay in `pypi-publish.yml` (OIDC does not work from a reusable
  workflow). Renovate must never automerge.
- **Public API:** everything in `gribkit.__all__`, plus `gribkit.headers.{HEAD_BYTES, Head, entry,
  idx_line, is_known}` and `gribkit.testing.make_global_message`, which PredictionDB uses.
- **Do not bring along:** No company or customer names from the user's environment; ask when in
  doubt. No code from other PredictionDB packages.
- **Approvals:** Changes to PyPI, the release workflow's triggers and the branch ruleset are
  externally visible. Ask the user first unless they explicitly requested it.

## Quick start

```bash
uv sync
uv run pytest
uv run pre-commit run --all-files
uv sync --group fuzz   # Linux x86_64 only
uv run --no-sync python fuzz/gribkit_fuzz.py idx -max_total_time=60 fuzz/corpus/idx
```
