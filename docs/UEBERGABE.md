# Übergabe: gribkit aus PredictionDB auslagern

Stand: 2026-11-01, Quelle `the78mole/PredictionDB` auf `main` @ `fb4e158`
(plus offener PR #228, siehe unten). Erstellt im Projekt „Strompreisprognose“.

## 1. Ziel

1. gribkit mit seiner Git-Historie aus `PredictionDB/packages/gribkit` in dieses eigene Repo
   `the78mole/gribkit` übernehmen.
2. Unter die **MIT-Lizenz** stellen (PredictionDB selbst bleibt BSL 1.1).
3. Als eigenständiges Paket `gribkit` auf **PyPI** veröffentlichen, per Trusted Publishing aus
   GitHub Actions.
4. PredictionDB danach auf das PyPI-Paket umstellen (eigener PR dort) und `packages/gribkit`
   entfernen.

Hintergrund: Der Nutzer will gribkit als nützliches, freies Werkzeug für andere bereitstellen.
Die übrigen PredictionDB-Pakete werden **nicht** veröffentlicht (hängen an DB-Schema, Garage,
Compose; Verteilweg dort ist das Docker-Image).

## 2. Was gribkit ist

Werkzeuge für GRIB2-Partial-Downloads, rund 810 Zeilen Code und 410 Zeilen Tests
(ohne PR #228), Abhängigkeiten nur `eccodes`, `eccodeslib`, `numpy`.

| Modul | Inhalt |
|---|---|
| `idx.py` | NCEP-`.idx` lesen (`parse_idx`, Unter-Nachrichten `12.1/12.2` teilen einen Bereich, Länge der letzten Nachricht aus Dateigröße), Auswahl über `MessageSpec` (`VAR:LEVEL`, optional Regex aufs Prognosefeld), `select`, `missing_specs`, `merge_ranges` mit `max_gap`, `ByteRange.extract` |
| `headers.py` | Nachrichtenköpfe GRIB2 **ohne ecCodes** lesen (`parse_head`, `HEAD_BYTES`, `Head`), `.idx`-Zeilen wie `wgrib2 -s` erzeugen (`entry`, `idx_line`, `is_known`), Nachrichtengrenzen in Rohdaten finden (`find_boundary`). Damit lassen sich `.idx` für Archive ohne Inventar bauen (GDEX). Nutzt `ncep_parameters.json` |
| `grib.py` | `iter_messages` (Bytestrom in Nachrichten zerlegen, Vollständigkeit prüfen), `crop`/`crop_message` (regular_ll auf `BBox` zuschneiden, auch über den Nullmeridian, Packung und Genauigkeit bleiben), `describe` |
| `bbox.py` | `BBox` |
| `testing.py` | `make_global_message`: synthetische GRIB2-Nachrichten mit bekannten Werten für Tests (wird auch von Tests in PredictionDB-Diensten genutzt, gehört also zur öffentlichen API) |
| `ncep_parameters.json` | NCEP-Tabelle 4.2, **übernommen aus grib2io 2.8.2 (MIT, NOAA/NWS)**, siehe `_source` in der Datei. Attribution in `NOTICE`/README nötig |
| `py.typed` | Typinformationen |

Öffentliche API heute (`gribkit/__init__.py`): `BBox, ByteRange, GribError, HeaderError, IdxEntry,
IdxParseError, MessageSpec, crop, crop_message, describe, find_boundary, iter_messages,
merge_ranges, missing_specs, parse_head, parse_idx, select`. Zusätzlich direkt importiert von
Abnehmern: `gribkit.headers.{HEAD_BYTES, Head, entry, idx_line, is_known}` und
`gribkit.testing.make_global_message`. Diese bleiben importierbar (ggf. zusätzlich in `__all__`).

Wichtige fachliche Eigenheit (gehört in die README): Die S3-Endpunkte von AWS und Google
beantworten Multi-Range-Anfragen (`Range: bytes=a-b,c-d`) mit der ganzen Datei (200). Deshalb lädt
der Aufrufer jeden Bereich aus `merge_ranges` einzeln und prüft 206 und Länge.

`ecCodes` braucht zusätzlich das Wheel `eccodeslib`, sonst „Cannot find the ecCodes library“.
`eccodeslib`/`eckitlib` gibt es nur mit cp311–cp314-Tags, deshalb Python ≤ 3.14
(https://github.com/ecmwf/eccodes/issues/629).

## 3. Was mitwandert

| Quelle in PredictionDB | Ziel hier |
|---|---|
| `packages/gribkit/src/gribkit/` | `src/gribkit/` |
| `packages/gribkit/tests/` (inkl. `fixtures/`) | `tests/` |
| `packages/gribkit/pyproject.toml` | `pyproject.toml` (neu aufbauen, s. u.) |
| `packages/gribkit/README.md` | `README.md` (neu auf Englisch) |
| **aus PR #228:** `packages/gribkit/tests/test_robustheit.py` | `tests/test_robustheit.py` |
| **aus PR #228:** `fuzz/gribkit_fuzz.py`, `fuzz/korpus/{idx,head}/` | `fuzz/` |
| **aus PR #228:** `.github/workflows/fuzz.yml` | `.github/workflows/fuzz.yml` (Pfadfilter anpassen: `src/**`, `fuzz/**`) |
| **aus PR #228:** Fix in `headers._fcst` (Sektion 4 zu kurz → `HeaderError` statt `IndexError`) | mit `src/` |
| `reqs/40-srs/gribkit.sdoc`, `reqs/50-swa/gribkit.sdoc` | siehe Abschnitt 6 (Anforderungen) |

PR #228 (https://github.com/the78mole/PredictionDB/pull/228, „Property-Tests und Atheris-Fuzzer“)
war am 2026-11-01 noch offen. **Erst übernehmen, wenn #228 gemergt ist**, dann ist alles in der
Historie von `main`. Falls er bei Start noch offen ist: Nutzer fragen, ob gewartet oder vom
PR-Branch `claude/project-thread-d8ivg0` übernommen werden soll.

Neue Dev-Abhängigkeiten aus #228: `hypothesis>=6.170` (Gruppe `dev`), `atheris>=3.1` (eigene
Gruppe `fuzz`, nur Linux-x86_64-Wheels, mypy ignoriert fehlende Typen von `atheris`).

## 4. Historie übernehmen

Script: [`scripts/historie-uebernehmen.sh`](../scripts/historie-uebernehmen.sh). Ablauf:

1. Frischer Klon von PredictionDB in ein Temp-Verzeichnis (nie im Arbeitsklon des Nutzers).
2. `git filter-repo` behält nur die Pfade aus Abschnitt 3 und benennt
   `packages/gribkit/` auf die Wurzel um.
3. PR-Verweise in Commit-Messages wie `(#123)` werden zu `(the78mole/PredictionDB#123)`
   umgeschrieben, damit sie im neuen Repo nicht auf falsche Nummern zeigen.
4. Ergebnis per Merge mit `--allow-unrelated-histories` mit dem Übergabe-Commit zusammenführen,
   der schon auf GitHub liegt. Nicht squashen.

Probelauf am 2026-11-01 (lokal, für `main` und den PR-Branch von #228): Skript läuft durch, 8 bzw.
10 Commits, nur gribkit-Pfade, PR-Verweise umgeschrieben, keine Treffer für den zu meidenden Firmennamen in Nachrichten oder
Inhalten. Die Dateiliste enthält noch keine Lizenz, das ist Teil von Abschnitt 5.

Prüfen: `git log --stat` zeigt nur gribkit-Dateien, Tests laufen auf dem ersten Commit nach dem
Umbau. Dateien der Übergabe (`CLAUDE.md`, `docs/UEBERGABE.md`, `docs/AUFTRAG.md`, `scripts/`)
nach der Umsetzung aufräumen: `CLAUDE.md` auf den Dauerbetrieb kürzen, `UEBERGABE.md` und
`AUFTRAG.md` löschen oder nach `docs/history/` verschieben (Nutzer fragen).

## 5. Neues Repo aufbauen

### pyproject.toml (Richtung)

- `name = "gribkit"` (auf PyPI am 2026-11-01 noch frei, ebenso `grib-kit`), `version` per
  semantic-release; erstes öffentliches Release **0.2.0** (seit 0.1.0 kamen `headers`/GDEX dazu,
  PredictionDB pinnt dann `gribkit~=0.2`).
- `description` englisch, `readme = "README.md"`, `license = "MIT"`,
  `license-files = ["LICENSE", "NOTICE"]`, `authors = [{name = "Daniel Glaser"}]`
  (Lizenzgeber in PredictionDB heißt „Daniel (the78mole) Glaser“; Nutzer fragen, wie er hier
  genannt werden will).
- `requires-python = ">=3.12"`, Classifier 3.12, 3.13, 3.14, `Typing :: Typed`,
  `Topic :: Scientific/Engineering :: Atmospheric Science`.
- `dependencies = ["eccodes>=2.40", "eccodeslib>=2.40", "numpy>=2.0"]`.
- `[project.urls]` Homepage, Source, Issues, Changelog.
- `[dependency-groups] dev = [hypothesis, mypy, pre-commit, pytest, pytest-html?, ruff]`,
  `fuzz = [atheris]`.
- Ruff/mypy/pytest-Konfiguration aus der PredictionDB-Wurzel-`pyproject.toml` übernehmen, aber
  auf gribkit reduziert (`known-first-party = ["gribkit"]`, mypy override für `eccodes.*`,
  `gribapi.*`, `atheris`). pytest-Marker `network` übernehmen, falls Tests ihn nutzen.
- hatchling: `packages = ["src/gribkit"]`, `ncep_parameters.json` und `py.typed` müssen im Wheel
  landen (prüfen mit `uv build` und `unzip -l`).

### Dateien

- `LICENSE` (MIT, Copyright 2026 Daniel Glaser o. ä.), `NOTICE` mit Attribution für grib2io (MIT, NOAA/NWS) für
  `ncep_parameters.json`.
- `README.md` englisch: Zweck, Installation (`pip install gribkit` / `uv add gribkit`),
  Beispiel Partial Download GFS von AWS (`noaa-gfs-bdp-pds`), Hinweis Multi-Range, Hinweis
  `eccodeslib` und Python ≤ 3.14, Herkunft aus PredictionDB, Badges (PyPI, CI, Lizenz, Scorecard).
- `CHANGELOG.md` (semantic-release), `CONTRIBUTING.md` (DCO/Signed-off-by; bei freier Lizenz
  reicht inbound=outbound, die CLA-artigen Bedingungen von PredictionDB nicht übernehmen, außer
  der Nutzer will das), `SECURITY.md`, `CODE_OF_CONDUCT.md` (wie PredictionDB, englisch).
- `.github/FUNDING.yml` wie in PredictionDB:
  ```yaml
  github: the78mole
  patreon: the78mole
  ko_fi: the78mole
  buy_me_a_coffee: the78mole
  ```
- `.pre-commit-config.yaml`: lokale Hooks `ruff-check`, `ruff-format`, `mypy` über
  `uv run --no-sync` (Vorlage: PredictionDB `.pre-commit-config.yaml`, ohne strictdoc/analysen).
- `renovate.json` wie PredictionDB (Dashboard, Minor/Patch je Ökosystem gruppiert, Python auf
  3.14.x halten wegen eccodeslib).
- `.coderabbit.yaml` optional wie in PredictionDB (dort Deutsch; hier Englisch?).

### Workflows (`.github/workflows/`)

- `ci.yml`: Matrix Python 3.12/3.13/3.14 × ubuntu (optional macOS), `uv sync --locked`,
  `uv run pre-commit run --all-files`, `uv run pytest`, `uv build` und Wheel-Inhalt prüfen.
  Actions per SHA pinnen (Scorecard „Pinned-Dependencies“), `permissions: contents: read`.
- `fuzz.yml`: aus PR #228, Pfadfilter auf `src/**`.
- `scorecard.yml`: wie PredictionDB (PR #226).
- `release.yml`: semantic-release (Conventional Commits) erzeugt Tag + GitHub-Release, danach
  Job `publish` mit `uv build` und `pypa/gh-action-pypi-publish` per **Trusted Publishing**
  (`permissions: id-token: write`, Environment `pypi`). Vorlage laut Nutzer: sein Repo
  **hoermoles-ble** (lokal unter `~/GIT/…` suchen oder auf GitHub ansehen). Vorher optional
  TestPyPI.
- Optional: Sigstore-Attestations (`attestations: true` ist bei gh-action-pypi-publish Standard).

Der Nutzer muss auf PyPI einen **Pending Trusted Publisher** anlegen (Projekt `gribkit`, Owner
`the78mole`, Repo `gribkit`, Workflow `release.yml`, Environment `pypi`). Link:
https://pypi.org/manage/account/publishing/

### Sicherheitsfunktionen

Wie in PredictionDB (PR #226): Dependabot-Alerts/Secret-Scanning/Push-Protection, Branch-Ruleset
für `main` (Vorlage `/mnt/project-files/security-badges/ruleset-main.json` im Projektordner, hier
als Kopie unter `docs/vorlagen/ruleset-main.json`, falls vorhanden), OpenSSF-Scorecard-Badge.

## 6. Anforderungen (StrictDoc)

In PredictionDB hängen an gribkit: `SYSA-SW-GRIBKIT` (reqs/30-sysa), `SWR-GRIB-001…008`
(reqs/40-srs/gribkit.sdoc), `SWA-GRIB-*` (reqs/50-swa/gribkit.sdoc) und die `@relation(...)`-Marker
im gribkit-Code. Das Prüfskript `reqs/pruefen.py` in PredictionDB verlangt, dass jede umgesetzte
SWR im Code von PredictionDB referenziert wird.

Vorschlag (mit Nutzer abstimmen):

- **gribkit-Repo:** eigene schlanke Anforderungen? Für eine öffentliche Bibliothek eher **nein**:
  `@relation`-Marker aus dem Code entfernen, die Inhalte der SWR als Abschnitt „Guarantees“ in die
  README bzw. Docstrings übernehmen.
- **PredictionDB:** `SYSA-SW-GRIBKIT` wird „externe Komponente (PyPI gribkit~=0.2)“;
  `reqs/40-srs/gribkit.sdoc` und `reqs/50-swa/gribkit.sdoc` entfallen oder werden zu
  Anforderungen an die externe Komponente mit Nachweis „Prüfung“ (Tests im gribkit-Repo).
  `reqs/pruefen.py` muss danach grün sein. `SYSR-SEC-009` verweist dann auf den Fuzzer im
  gribkit-Repo.

## 7. PredictionDB umstellen (eigener PR in the78mole/PredictionDB, nach dem ersten Release)

- `packages/gribkit/` löschen; Workspace-Mitglied entfällt automatisch (`members = ["packages/*",…]`).
- In `services/wx_ingest`, `services/wx_process`, `predict` die Quelle
  `gribkit = { workspace = true }` entfernen und `gribkit~=0.2` als Abhängigkeit setzen.
  `services/wx_exchange` importiert gribkit, deklariert es aber nicht direkt (kommt über
  wx-ingest/wx-process): dort `gribkit` ebenfalls eintragen.
- Wurzel-`pyproject.toml`: `packages/gribkit/src` aus `mypy_path`, `gribkit` aus
  `known-first-party` entfernen.
- `fuzz/`, `.github/workflows/fuzz.yml`, `fuzz`-Gruppe (atheris) aus PredictionDB entfernen
  (wandern ins gribkit-Repo). `hypothesis` bleibt, falls andere Tests es nutzen.
- Anforderungen wie in Abschnitt 6, `docs/ARCHITEKTUR.md` (Kap. 6/Tab. Repo-Struktur, Zeile mit
  `gribkit/`) und `SPECIFICATION.md`/README auf das externe Paket verweisen.
- `uv lock`, `uv run pre-commit run --all-files`, `uv run pytest` grün; Docker-Image
  (`docker/Dockerfile`, `uv sync --frozen --no-dev --all-packages`) baut.
- Abnehmer, die gegen die API laufen müssen: `services/wx_ingest` (gfs.py, config.py, ingest.py,
  testing.py, Tests inkl. test_header_scan.py), `services/wx_exchange` (idx.py, gefs_vm.py,
  test_gefs.py), `services/wx_process` (decode.py, test_decode.py), `predict/src/pdb_predict/weather.py`,
  Analyse-Skripte `docs/analysen/{silber-float16,gfs-v16-jahre,gfs-v15-v16,gfs-folgelauf}/auswertung.py`.
- Renovate in PredictionDB hebt gribkit dann wie jede andere Abhängigkeit.

## 8. Offene Entscheidungen (Nutzer)

1. **Lizenz:** ~~MIT oder Apache-2.0~~ **entschieden 2026-11-01: MIT** (SPDX `MIT`).
   Die grib2io-Attribution (MIT, NOAA/NWS) für `ncep_parameters.json` kommt als eigener
   Abschnitt in `LICENSE` oder als `NOTICE` mit Copyright-Vermerk und Lizenztext von grib2io.
2. **Sprache von Docstrings/Kommentaren:** Empfehlung Englisch (öffentliche Bibliothek); heute
   Deutsch.
3. **Autorenname** in `pyproject.toml`/LICENSE.
4. **Anforderungen im neuen Repo** ja/nein (Abschnitt 6).
5. Zeitpunkt des ersten PyPI-Releases (Memory: „wenn API stabil“; der Nutzer hat am 2026-11-01
   entschieden, die Auslagerung schon jetzt anzugehen).

Rechtliches: gribkit ist vollständig im Projekt entstanden (PR #3 vom 2026-10-20, kein Altcode),
alle Commits stammen vom Nutzer bzw. von Claude-Sitzungen in seinem Auftrag. Er kann gribkit
daher ohne Zustimmung Dritter unter eine freie Lizenz stellen. Einzige Fremdquelle:
`ncep_parameters.json` aus grib2io (MIT) → Attribution.

## 9. Abnahmekriterien

- [ ] Repo `the78mole/gribkit` mit übernommener Historie (nur gribkit-Pfade, PR-Verweise
      umgeschrieben).
- [ ] Freie Lizenz, NOTICE mit grib2io-Attribution, englische README.
- [ ] CI grün auf 3.12–3.14, pre-commit grün, Wheel enthält `ncep_parameters.json` und `py.typed`.
- [ ] Fuzz-Workflow und Property-Tests aus #228 laufen.
- [ ] Release-Workflow mit Trusted Publishing; `gribkit 0.2.0` auf PyPI (nach Freigabe).
- [ ] PR in PredictionDB: gribkit von PyPI, `packages/gribkit` und `fuzz/` entfernt, alles grün.
- [ ] Projekt-Memory in PredictionDB-Projekt aktualisieren (gribkit-auslagerung: erledigt, Repo-URL).
