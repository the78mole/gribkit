# Handover: moving gribkit out of PredictionDB

As of 2026-11-01, source `the78mole/PredictionDB` on `main`, including the merged PR #228.

## 1. Goal

1. Move gribkit with its Git history from `PredictionDB/packages/gribkit` into this repository,
   `the78mole/gribkit`.
2. License it under **MIT** (PredictionDB itself stays BSL 1.1).
3. Publish it as the standalone package `gribkit` on **PyPI**, using Trusted Publishing from GitHub
   Actions.
4. Then switch PredictionDB to the PyPI package (separate PR there) and remove `packages/gribkit`.

Background: the user wants to offer gribkit as a useful, free tool for others. The other PredictionDB
packages will **not** be published (they depend on the DB schema, Garage and Compose; they ship as a
Docker image).

## 2. What gribkit is

Tools for GRIB2 partial downloads, about 810 lines of code and 410 lines of tests (without PR #228).
Its only dependencies are `eccodes`, `eccodeslib` and `numpy`.

| Module | Content |
|---|---|
| `idx.py` | Read NCEP `.idx` files (`parse_idx`; sub-messages `12.1/12.2` share a range; length of the last message from the file size), selection through `MessageSpec` (`VAR:LEVEL`, optional regex on the forecast field), `select`, `missing_specs`, `merge_ranges` with `max_gap`, `ByteRange.extract` |
| `headers.py` | Parse GRIB2 message headers **without ecCodes** (`parse_head`, `HEAD_BYTES`, `Head`), generate `.idx` lines like `wgrib2 -s` (`entry`, `idx_line`, `is_known`), find message boundaries in raw data (`find_boundary`). This allows building `.idx` files for archives without an inventory (GDEX). Uses `ncep_parameters.json` |
| `grib.py` | `iter_messages` (split a byte stream into messages, check completeness), `crop`/`crop_message` (crop regular_ll to a `BBox`, also across the prime meridian, keeping packing and precision), `describe` |
| `bbox.py` | `BBox` |
| `testing.py` | `make_global_message`: synthetic GRIB2 messages with known values for tests (also used by tests in PredictionDB services, so it is part of the public API) |
| `ncep_parameters.json` | NCEP table 4.2, **taken from grib2io 2.8.2 (MIT, NOAA/NWS)**, see `_source` in the file. Requires attribution in `NOTICE`/README |
| `py.typed` | Type information |

Public API today (`gribkit/__init__.py`): `BBox, ByteRange, GribError, HeaderError, IdxEntry,
IdxParseError, MessageSpec, crop, crop_message, describe, find_boundary, iter_messages, merge_ranges,
missing_specs, parse_head, parse_idx, select`. Consumers also import directly:
`gribkit.headers.{HEAD_BYTES, Head, entry, idx_line, is_known}` and
`gribkit.testing.make_global_message`. These stay importable (add them to `__all__` if useful).

An important domain quirk that belongs in the README: the S3 endpoints of AWS and Google answer
multi-range requests (`Range: bytes=a-b,c-d`) with the whole file (200). The caller therefore
downloads each range from `merge_ranges` individually and checks for 206 and the length.

`ecCodes` also needs the `eccodeslib` wheel, otherwise it fails with "Cannot find the ecCodes
library". `eccodeslib`/`eckitlib` only exist with cp311–cp314 tags, hence Python ≤ 3.14
(https://github.com/ecmwf/eccodes/issues/629).

## 3. What moves here

| Source in PredictionDB | Target here |
|---|---|
| `packages/gribkit/src/gribkit/` | `src/gribkit/` |
| `packages/gribkit/tests/` (incl. `fixtures/`) | `tests/` |
| `packages/gribkit/pyproject.toml` | `pyproject.toml` (rebuild, see below) |
| `packages/gribkit/README.md` | `README.md` (rewrite in English) |
| **from PR #228:** `packages/gribkit/tests/test_robustheit.py` | `tests/test_robustness.py` |
| **from PR #228:** `fuzz/gribkit_fuzz.py`, `fuzz/korpus/{idx,head}/` | `fuzz/gribkit_fuzz.py`, `fuzz/corpus/{idx,head}/` |
| **from PR #228:** `.github/workflows/fuzz.yml` | `.github/workflows/fuzz.yml` (adjust path filters: `src/**`, `fuzz/**`) |
| **from PR #228:** fix in `headers._fcst` (section 4 too short → `HeaderError` instead of `IndexError`) | with `src/` |
| `reqs/40-srs/gribkit.sdoc`, `reqs/50-swa/gribkit.sdoc` | see section 6 (requirements) |

**The imported code is German in places: translate it to English** (docstrings, comments, error
messages, test names, identifiers, file names), in a separate commit after the import. The imported
commit messages stay as they are, because rewriting them would obscure where the history came from.

PR #228 (https://github.com/the78mole/PredictionDB/pull/228, property tests and Atheris fuzzer) was
merged on 2026-11-01, so everything is in the history of `main`.

New dev dependencies from #228: `hypothesis>=6.170` (group `dev`), `atheris>=3.1` (own group `fuzz`,
Linux x86_64 wheels only, mypy ignores the missing types of `atheris`).

## 4. Importing the history

Script: [`scripts/import-history.sh`](../scripts/import-history.sh). Steps:

1. Fresh clone of PredictionDB into a temp directory (never in the user's working clone).
2. `git filter-repo` keeps only the paths from section 3 and renames `packages/gribkit/` to the root.
3. PR references in commit messages like `(#123)` are rewritten to `(the78mole/PredictionDB#123)` so
   they do not point to wrong numbers in the new repository.
4. Merge the result with the handover commits already on GitHub, using
   `--allow-unrelated-histories`, and push the merge directly to `main`. PRs in this repository can
   only be squash-merged, which would destroy the imported history.

Trial run on 2026-11-01 (local, on `main` after #228 was merged): the script completes with 9
commits, only gribkit paths, PR references rewritten, no hits for the company name to avoid in
messages or content.

To verify: `git log --stat` shows only gribkit files, and the tests pass on the first commit after
the rebuild. Clean up the handover files (`CLAUDE.md`, `docs/HANDOVER.md`, `docs/BRIEF.md`,
`docs/templates/`, `scripts/`) once this is done: shorten `CLAUDE.md` for day-to-day work, delete
`HANDOVER.md` and `BRIEF.md` or move them to `docs/history/` (ask the user).

## 5. Building the new repository

### pyproject.toml (direction)

- `name = "gribkit"` (still free on PyPI on 2026-11-01, as is `grib-kit`), first public release
  **0.2.0** (`headers`/GDEX were added since 0.1.0; PredictionDB then pins `gribkit~=0.2`).
- English `description`, `readme = "README.md"`, `license = "MIT"`,
  `license-files = ["LICENSE", "NOTICE"]`, `authors = [{name = "Daniel Glaser"}]` (the licensor in
  PredictionDB is "Daniel (the78mole) Glaser"; ask the user what name to use here).
- `requires-python = ">=3.12"`, classifiers 3.12, 3.13, 3.14, `Typing :: Typed`,
  `Topic :: Scientific/Engineering :: Atmospheric Science`.
- `dependencies = ["eccodes>=2.40", "eccodeslib>=2.40", "numpy>=2.0"]`.
- `[project.urls]` Homepage, Source, Issues, Changelog.
- `[dependency-groups] dev = [hypothesis, mypy, pre-commit, pytest, pytest-cov, ruff]`,
  `fuzz = [atheris]`.
- Take the Ruff/mypy/pytest configuration from the PredictionDB root `pyproject.toml`, reduced to
  gribkit (`known-first-party = ["gribkit"]`, mypy override for `eccodes.*`, `gribapi.*`, `atheris`).
  Keep the pytest marker `network` if tests use it.
- hatchling: `packages = ["src/gribkit"]`; `ncep_parameters.json` and `py.typed` must end up in the
  wheel (verify with `uv build` and `unzip -l`).

### Files

- `LICENSE` (MIT, Copyright 2026 Daniel Glaser or similar), `NOTICE` with attribution for grib2io
  (MIT, NOAA/NWS) for `ncep_parameters.json`.
- `README.md` in English: purpose, installation (`pip install gribkit` / `uv add gribkit`), example
  of a GFS partial download from AWS (`noaa-gfs-bdp-pds`), multi-range note, note on `eccodeslib` and
  Python ≤ 3.14, origin in PredictionDB, badges (PyPI, CI, license, Scorecard).
- `CHANGELOG.md` pointing to the GitHub Releases, which carry the generated notes. The release
  workflow does not commit back to `main`. `CONTRIBUTING.md` (DCO/Signed-off-by; with a free license,
  inbound=outbound is enough, do not take over PredictionDB's CLA-like terms unless the user wants
  them), `SECURITY.md`, `CODE_OF_CONDUCT.md` (like PredictionDB, in English).
- `.github/FUNDING.yml` is already in place.
- `.pre-commit-config.yaml`: local hooks `ruff-check`, `ruff-format`, `mypy` via `uv run --no-sync`
  (template: `docs/templates/pre-commit-config.predictiondb.yaml`, without strictdoc/analyses).
- `renovate.json`: template `docs/templates/renovate.predictiondb.json` (dashboard, minor/patch
  grouped per ecosystem, Python held at 3.14.x because of eccodeslib), **but without `automerge`**,
  see "Release policy" below.
- `.coderabbit.yaml` optional, template `docs/templates/coderabbit.predictiondb.yaml`, reduced to
  what applies to gribkit.

### Workflows (`.github/workflows/`)

- `ci.yml`: matrix Python 3.12/3.13/3.14 × ubuntu (optionally macOS), `uv sync --locked`,
  `uv run pre-commit run --all-files`, `uv run pytest`, `uv build` and check the wheel contents. Pin
  actions by SHA (Scorecard "Pinned-Dependencies"), `permissions: contents: read`.
- `fuzz.yml`: from PR #228, path filter on `src/**`.
- `scorecard.yml`: like PredictionDB (PR #226), template `docs/templates/scorecard.predictiondb.yml`.
- `pypi-publish.yml`: see below. Template `docs/templates/pypi-publish.hoermoles-ble.yml`.
- Optional: Sigstore attestations (`attestations: true` is the default in gh-action-pypi-publish).

### Release policy (decided by the user on 2026-11-01)

**Every commit on `main` produces a semantic-version release:** tag, GitHub Release and PyPI publish.
This is the user's standard setup, `paulhatch/semantic-version` with `bump_each_commit: true`, in a
single file `pypi-publish.yml`.

- The repository allows squash merges only, so each merged PR is one commit and one release, and
  the PR title decides the bump.
- `feat:` bumps minor, a `!` breaking change bumps major, everything else bumps patch. Do not add a
  `paths:` filter to the push trigger as in the template, or not every commit releases.
- Keep `pypi-publish.yml` together with its publish job in one file, in a job behind `ci` checks on
  the same commit where possible, so a broken commit does not reach PyPI.
- **The template's patterns miss scoped commits:** `/^feat:/` does not match `feat(idx): ...`, and
  `/(feat|fix|refactor)!:/` does not match `feat(idx)!: ...`. Widen them to allow an optional scope,
  and verify the result.
- **Seed the version.** The imported history has no tags, so the calculated version would be
  arbitrary. Create the tag `v0.1.0` on the import merge commit before the workflow first runs, with
  `gh api repos/the78mole/gribkit/git/refs -f ref=refs/tags/v0.1.0 -f sha=<sha>`. A `feat:` commit
  then yields 0.2.0. Check the calculated version in a workflow run with `publish_target: none`
  before enabling the push trigger.
- **Renovate must not automerge.** Every automerged dependency update would become a PyPI release,
  and the weekly lockfile maintenance would release every week without any change to the package.
  Lockfile-only updates also change nothing for users.

The user creates a **Pending Trusted Publisher** on PyPI (project `gribkit`, owner `the78mole`,
repository `gribkit`, workflow `pypi-publish.yml`, environment `pypi`). Link:
https://pypi.org/manage/account/publishing/

The GitHub environment `pypi` already exists.

### Security features

As in PredictionDB (PR #226): Dependabot alerts, secret scanning and push protection, a branch ruleset
for `main` (template `docs/templates/ruleset-main.json`, with `squash` as the only merge method and
after the history import), OpenSSF Scorecard badge. On 2026-11-01, secret scanning, push protection
and Dependabot security updates were still off.

## 6. Requirements (StrictDoc)

In PredictionDB, these relate to gribkit: `SYSA-SW-GRIBKIT` (reqs/30-sysa), `SWR-GRIB-001…008`
(reqs/40-srs/gribkit.sdoc), `SWA-GRIB-*` (reqs/50-swa/gribkit.sdoc) and the `@relation(...)` markers
in the gribkit code. The check script `reqs/pruefen.py` in PredictionDB requires every implemented
SWR to be referenced in PredictionDB's code.

Proposal (agree with the user):

- **gribkit repository:** its own lean requirements? For a public library, rather **no**: remove the
  `@relation` markers from the code and move the content of the SWRs into a "Guarantees" section of
  the README or into docstrings.
- **PredictionDB:** `SYSA-SW-GRIBKIT` becomes "external component (PyPI gribkit~=0.2)";
  `reqs/40-srs/gribkit.sdoc` and `reqs/50-swa/gribkit.sdoc` are dropped or become requirements on the
  external component with verification method "inspection" (tests in the gribkit repository).
  `reqs/pruefen.py` must pass afterwards. `SYSR-SEC-009` then refers to the fuzzer in the gribkit
  repository.

## 7. Switching PredictionDB (separate PR in the78mole/PredictionDB, after the first release)

- Delete `packages/gribkit/`; the workspace member disappears automatically
  (`members = ["packages/*",…]`).
- In `services/wx_ingest`, `services/wx_process` and `predict`, remove the source
  `gribkit = { workspace = true }` and declare `gribkit~=0.2` as a dependency. `services/wx_exchange`
  imports gribkit but does not declare it directly (it comes through wx-ingest/wx-process): add
  `gribkit` there too.
- Root `pyproject.toml`: remove `packages/gribkit/src` from `mypy_path` and `gribkit` from
  `known-first-party`.
- Remove `fuzz/`, `.github/workflows/fuzz.yml` and the `fuzz` group (atheris) from PredictionDB (they
  move to the gribkit repository). `hypothesis` stays if other tests use it.
- Requirements as in section 6; point `docs/ARCHITEKTUR.md` (ch. 6/repository structure table, the
  line with `gribkit/`) and `SPECIFICATION.md`/README to the external package.
- `uv lock`, `uv run pre-commit run --all-files` and `uv run pytest` pass; the Docker image
  (`docker/Dockerfile`, `uv sync --frozen --no-dev --all-packages`) builds.
- Consumers that must work against the API: `services/wx_ingest` (gfs.py, config.py, ingest.py,
  testing.py, tests incl. test_header_scan.py), `services/wx_exchange` (idx.py, gefs_vm.py,
  test_gefs.py), `services/wx_process` (decode.py, test_decode.py),
  `predict/src/pdb_predict/weather.py`, analysis scripts
  `docs/analysen/{silber-float16,gfs-v16-jahre,gfs-v15-v16,gfs-folgelauf}/auswertung.py`.
- Renovate in PredictionDB then bumps gribkit like any other dependency. PredictionDB's pin
  `gribkit~=0.2` accepts every patch release, and with a release per commit there will be many.

## 8. Decisions

Decided:

1. **License:** MIT (SPDX `MIT`), decided 2026-11-01. The grib2io attribution (MIT, NOAA/NWS) for
   `ncep_parameters.json` goes in a separate section of `LICENSE` or into `NOTICE`, with copyright
   notice and license text of grib2io.
2. **Language:** English for everything in the repository, decided 2026-11-01. The code is still
   German in places today and must be translated (section 3).
3. **Release policy:** a release on every commit on `main`, decided 2026-11-01 (section 5).
4. **Visibility:** public, decided 2026-11-01.

Still open:

5. **Author name** in `pyproject.toml`/LICENSE.
6. **Requirements in the new repository**, yes or no (section 6).
7. **Timing of the first PyPI release.** The user decided on 2026-11-01 to start the move now.

Legal: gribkit was created entirely within the project (PR #3 of 2026-10-20, no legacy code), and all
commits come from the user or from Claude sessions on their behalf. The user can therefore put gribkit
under a free license without third-party consent. The only external source is `ncep_parameters.json`
from grib2io (MIT) → attribution.

## 9. Acceptance criteria

- [ ] Repository `the78mole/gribkit` with imported history (gribkit paths only, PR references
      rewritten).
- [ ] Free license, NOTICE with grib2io attribution, English README, code translated to English.
- [ ] CI passes on 3.12–3.14, pre-commit passes, wheel contains `ncep_parameters.json` and `py.typed`.
- [ ] Fuzz workflow and property tests from #228 run.
- [ ] Release workflow with Trusted Publishing; `gribkit 0.2.0` on PyPI (after approval).
- [ ] PR in PredictionDB: gribkit from PyPI, `packages/gribkit` and `fuzz/` removed, everything
      passes.
- [ ] Update the project memory in the PredictionDB project (gribkit move: done, repository URL).
