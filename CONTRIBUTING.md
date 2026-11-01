# Contributing to gribkit

Thanks for your interest in gribkit! Bug reports, ideas and pull requests are welcome.

## Reporting bugs and asking questions

Open an [issue](https://github.com/the78mole/gribkit/issues). Helpful details: the gribkit and
Python versions, the data source (for example the URL of the `.idx` file or GRIB2 file), what you
expected and what happened. Please report security vulnerabilities privately, see
[SECURITY.md](SECURITY.md).

## Development setup

```bash
git clone https://github.com/the78mole/gribkit.git
cd gribkit
uv sync
uv run pre-commit install
```

Before you open a pull request, run the same checks as CI:

```bash
uv run pre-commit run --all-files   # Ruff (lint and format), mypy strict and file checks
uv run pytest --cov=gribkit         # tests with coverage
uv build                            # wheel and sdist
```

Tests that need internet access are marked with `@pytest.mark.network` and skipped by default
(`uv run pytest -m network` runs them).

## Code style

- Python 3.12 or newer, fully typed (mypy `strict`), Ruff with line length 100.
- Docstrings, comments, identifiers and messages are in English.
- Keep the core free of heavy dependencies: only `crop`, `crop_message` and `describe` may use
  ecCodes.

## Commits and pull requests

- Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`,
  `chore:`, ... with an optional scope such as `fix(idx):`).
- Pull requests are squash-merged, so the **PR title** becomes the commit message on `main`. It
  must be a Conventional Commit, because every commit on `main` is released and the title decides
  the version bump (`feat:` minor, `!` major, everything else patch).
- Sign off every commit (`git commit -s`), see below.

## Developer Certificate of Origin

By adding a `Signed-off-by: Your Name <you@example.com>` line to a commit, you certify the
[Developer Certificate of Origin 1.1](https://developercertificate.org/): in short, that you wrote
the contribution or otherwise have the right to submit it under the project's license.

Contributions are accepted under the same license as the project, the
[MIT License](LICENSE) (inbound = outbound). If your contribution includes third-party material,
name its source and license in the pull request.
