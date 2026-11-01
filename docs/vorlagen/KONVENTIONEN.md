# Daniels Repo-Konventionen (Auszug für die Cloud-Sitzung)

Daniels persönliche Skills (`repo-ci-standards`, `python-project-setup`) liegen nur lokal unter
`~/.claude` und stehen in einer Cloud-Sitzung nicht zur Verfügung. Hier steht das, was für gribkit
davon gilt. Bei Widerspruch gilt: `CLAUDE.md` und `docs/UEBERGABE.md` vor diesem Auszug.

Wo die beiden Quellen sich widersprechen und es nicht offensichtlich ist, steht es unter
„Widersprüche“. Diese Punkte mit Daniel klären.

## Veröffentlichung

- **OIDC und wiederverwendbare Workflows vertragen sich nicht.** Der Publish-Schritt muss direkt
  in der Workflow-Datei stehen, die auf PyPI als Trusted Publisher eingetragen ist, nicht in einer
  per `uses: ./.github/workflows/x.yml` aufgerufenen Datei. Sonst meldet PyPI „does not match
  expected Trusted Publisher“. Mehrere Jobs in einer Datei sind in Ordnung.
- **Das Environment `pypi` muss vor dem ersten Publish-Lauf existieren.** Legt erst der Job es an,
  kann der Lauf dauerhaft auf `queued` hängen, ohne Fehlermeldung und ohne Timeout. Der Job
  taucht dann gar nicht in der Jobliste auf, `pending_deployments` ist leer. Das ist kein
  Trusted-Publisher-Problem. Abhilfe: `gh run cancel <id>`, danach neu auslösen. Anlegen:
  `gh api -X PUT repos/the78mole/gribkit/environments/pypi`
- **Statische Version:** `hatch version <x>` verweigert ein statisches `version = "..."`. Entweder
  die Zeile vor dem Build per Regex setzen (siehe Vorlage) oder dynamisch versionieren.
- **Vorlage:** `docs/vorlagen/pypi-publish.hoermoles-ble.yml` ist erprobt (Version, GitHub-Release,
  Build und Publish in einer Datei). Für gribkit den `-cli`-Teil weglassen und alle Platzhalter
  ersetzen. Action-Versionen darin vor der Übernahme prüfen, sie veralten schnell.
- Vor dem ersten Lauf den Build lokal prüfen: Version setzen, `uv build`, `twine check dist/*`.

## Werkzeuge

- **pre-commit** zusätzlich zu den lokalen Hooks aus der Übergabe mit dem Grundsatz aus
  `pre-commit/pre-commit-hooks` (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`,
  `check-toml`, `check-json`, `check-added-large-files`, `check-merge-conflict`,
  `debug-statements`, `check-ast`) und `python-jsonschema/check-jsonschema`
  (`check-github-workflows`). `rev` jeweils aktuell nachsehen.
- **Beim ersten `pre-commit run --all-files` das Diff ansehen und Daniel zeigen,** bevor es als
  erledigt gilt. Formatierer können datenlastige Dateien aufblähen; solche Dateien ausnehmen
  (`extend-exclude`). `check-added-large-files` und `end-of-file-fixer` auf die Binärdateien in
  `fuzz/korpus/` und `tests/fixtures/` prüfen.
- **Ruff-Funde** einzeln bewerten. Einfach Behebbares beheben, bewusste Muster mit begründendem
  Kommentar ignorieren, nichts pauschal abschalten. Kein `black` neben `ruff format`.
- **Tests und Coverage:** `uv run pytest --cov=gribkit --cov-report=term-missing --cov-report=xml`.
  Richtwert 80 % auf neuem Code, Startwert ehrlich berichten, dann per `--cov-fail-under` absichern.
  `pytest-cov` gehört dafür in die Gruppe `dev`. Coverage in die Job Summary, kein Codecov ohne
  ausdrücklichen Wunsch. Tests laufen in einem eigenen Workflow auf jedem Push und PR, nicht hinter
  der Release-Logik.
- **Vor jedem Workflow** die aktuelle Version jeder Action nachsehen, nie aus dem Gedächtnis oder
  aus alten Workflows kopieren:
  `gh api repos/actions/checkout/releases/latest --jq .tag_name`

## README-Badges

Eine Zeile direkt unter der H1, vor dem ersten Absatz. Zusätzlich zu den Badges aus der Übergabe:

```markdown
[![Release](https://github.com/the78mole/gribkit/actions/workflows/<release-workflow>.yml/badge.svg)](https://github.com/the78mole/gribkit/actions/workflows/<release-workflow>.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com)
[![PyPI](https://img.shields.io/pypi/v/gribkit?label=gribkit)](https://pypi.org/project/gribkit/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
```

Vorbild laut Daniel: https://github.com/the78mole/vnbdigital-client/blob/main/README.md

## Was Daniel selbst macht

Renovate-App aktivieren und den Pending Trusted Publisher auf PyPI anlegen. Beides nicht
automatisieren, sondern ihm die Werte nennen.

## Widersprüche (mit Daniel klären)

| Thema | Übergabe | Daniels Standard | Warum es zählt |
|---|---|---|---|
| Release-Werkzeug | semantic-release, `release.yml` | `paulhatch/semantic-version` mit `bump_each_commit: true`, `pypi-publish.yml` | Mit `bump_each_commit` wird **jeder Commit auf `main` zu einem PyPI-Release**, ein Versehen ist dann eine Veröffentlichung. Der Dateiname muss dem Trusted Publisher entsprechen, also vor dessen Einrichtung festlegen. |
| Action-Pinning | per SHA (Scorecard) | Floating Major (`@v5`) | SHA-Pinning bringt Punkte bei Scorecard, Renovate hält die Hashes aktuell. |
| Renovate | wie PredictionDB, Python auf 3.14.x halten | feste Grundkonfiguration ohne Zusatzregeln | Die Python-Regel ist wegen `eccodeslib` sachlich nötig. |
| Ruff-Zeilenlänge | 100 | 120 | Entschieden: 100 (`CLAUDE.md`). |
