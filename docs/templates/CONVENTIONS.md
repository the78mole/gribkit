# Daniel's repo conventions (excerpt for the cloud session)

Daniel's personal skills (`repo-ci-standards`, `python-project-setup`) exist only locally under
`~/.claude` and are not available in a cloud session. This file holds what applies to gribkit. If
there is a conflict, `CLAUDE.md` and `docs/HANDOVER.md` take precedence over this excerpt.

## Publishing

- **OIDC and reusable workflows do not mix.** The publish step must be directly in the workflow file
  registered as the Trusted Publisher on PyPI, not in a file called through
  `uses: ./.github/workflows/x.yml`. Otherwise PyPI reports "does not match expected Trusted
  Publisher". Several jobs in one file are fine.
- **The `pypi` environment must exist before the first publish run.** If the job creates it, the run
  can hang at `queued` forever, with no error and no timeout. The job does not even appear in the job
  list, and `pending_deployments` is empty. This is not a Trusted Publisher problem. Remedy:
  `gh run cancel <id>`, then trigger again. For gribkit the environment already exists.
- **Static version:** `hatch version <x>` refuses a static `version = "..."`. Either set the line by
  regex before the build (see the template) or use dynamic versioning.
- **Template:** `docs/templates/pypi-publish.hoermoles-ble.yml` is proven (version, GitHub Release,
  build and publish in one file). For gribkit, drop the `-cli` part and replace all placeholders.
  Check the action versions before using it, they go stale quickly. The release policy in
  `docs/HANDOVER.md`, section 5, lists further changes.
- Check the build locally before the first run: set the version, `uv build`, `twine check dist/*`.

## Tools

- **pre-commit:** in addition to the local hooks from the handover, use the baseline from
  `pre-commit/pre-commit-hooks` (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`,
  `check-toml`, `check-json`, `check-added-large-files`, `check-merge-conflict`, `debug-statements`,
  `check-ast`) and `python-jsonschema/check-jsonschema` (`check-github-workflows`). Look up the
  current `rev` of each.
- **Look at the diff of the first `pre-commit run --all-files` and show it to Daniel** before calling
  it done. Formatters can bloat data-heavy files; exclude those (`extend-exclude`). Check
  `check-added-large-files` and `end-of-file-fixer` against the binary files in `fuzz/corpus/` and
  `tests/fixtures/`.
- **Ruff findings:** assess each one. Fix what is easy, ignore deliberate patterns with a comment
  giving the reason, switch nothing off wholesale. No `black` next to `ruff format`.
- **Tests and coverage:** `uv run pytest --cov=gribkit --cov-report=term-missing --cov-report=xml`.
  Target 80 % on new code; report the starting value honestly, then secure it with
  `--cov-fail-under`. Coverage goes to the job summary, no Codecov unless explicitly requested. Tests
  run in their own workflow on every push and PR, not behind the release logic.
- **Before each workflow,** look up the current version of each action, never copy from memory or old
  workflows: `gh api repos/actions/checkout/releases/latest --jq .tag_name`
- **Action pinning:** by SHA as the handover says (Scorecard), overriding Daniel's usual floating
  major tags. Renovate keeps the hashes current.
- **Ruff line length:** 100 (`CLAUDE.md`), overriding Daniel's usual 120.

## README badges

One row directly below the H1, before the first paragraph. In addition to the badges from the
handover:

```markdown
[![Release](https://github.com/the78mole/gribkit/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/the78mole/gribkit/actions/workflows/pypi-publish.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com)
[![PyPI](https://img.shields.io/pypi/v/gribkit?label=gribkit)](https://pypi.org/project/gribkit/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
```

Daniel's preferred example: https://github.com/the78mole/vnbdigital-client/blob/main/README.md

## What Daniel does himself

Enable the Renovate app and create the Pending Trusted Publisher on PyPI. Do not automate either;
give him the values to enter.
