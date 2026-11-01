# CLAUDE.md – gribkit

Dies ist das eigenständige Repository **gribkit** (GitHub `the78mole/gribkit`, derzeit privat,
PyPI `gribkit`). Es enthält noch keinen Code, sondern die Übergabe aus dem Projekt
PredictionDB. Der vollständige Auftrag steht in [`docs/UEBERGABE.md`](docs/UEBERGABE.md),
der Ablauf in [`docs/AUFTRAG.md`](docs/AUFTRAG.md), Daniels Repo-Konventionen in
[`docs/vorlagen/KONVENTIONEN.md`](docs/vorlagen/KONVENTIONEN.md).
Lies die Übergabe zuerst ganz, bevor Du etwas änderst.

## Kurzfassung

gribkit ist eine kleine Python-Bibliothek für GRIB2-Partial-Downloads (NCEP-`.idx` lesen,
Nachrichten wählen, Byte-Bereiche bündeln, Nachrichtenköpfe ohne ecCodes lesen, GRIB2 per ecCodes
auf einen Ausschnitt zuschneiden). Sie ist in `the78mole/PredictionDB` unter `packages/gribkit`
entstanden und soll mit ihrer Git-Historie in dieses Repo umziehen, unter eine freie Lizenz
gestellt (entschieden: **MIT**) und auf PyPI veröffentlicht werden. Danach bezieht PredictionDB gribkit von PyPI.

## Regeln für die Arbeit

- **Sprache:** Mit dem Nutzer (Daniel, GitHub `the78mole`) auf Deutsch sprechen. Alles, was
  öffentlich im Repo und auf PyPI steht (README, Docstrings, Kommentare, Commit-Messages,
  Changelog), auf **Englisch**, sofern der Nutzer nichts anderes entscheidet (siehe offene
  Entscheidungen in der Übergabe).
- **Werkzeuge:** Python mit `uv` (kein pip/poetry), Build-Backend `hatchling`, Ruff
  (Zeilenlänge 100, Regeln `E,F,W,I,UP,B,SIM,RUF,DTZ`), mypy `strict`, pytest, pre-commit mit
  lokalen Hooks über `uv run --no-sync` (wie in PredictionDB).
- **Python:** `>=3.12`, getestet 3.12–3.14. **Kein 3.15**, solange `eccodeslib` keine passenden
  Wheels hat (Upstream-Issue https://github.com/ecmwf/eccodes/issues/629).
- **Commits:** Conventional Commits (für semantic-release), mit `Signed-off-by` (`git commit -s`).
- **Keine Rückwirkung auf PredictionDB ohne Absprache:** Die Umstellung von PredictionDB auf das
  PyPI-Paket ist ein eigener PR in `the78mole/PredictionDB`, erst nach dem ersten PyPI-Release.
- **Nicht mitnehmen:** Keine Firmen- oder Kundennamen aus dem Umfeld des Nutzers verwenden; im Zweifel
  fragen. Keinen Code aus anderen Paketen von PredictionDB (core, Dienste, ml_train, predict)
  übernehmen.
- **Freigaben:** Das Repo öffentlich schalten, PyPI-Trusted-Publisher einrichten und das erste
  Release veröffentlichen sind nach außen wirksam und schwer umkehrbar. Vorher den Nutzer fragen,
  sofern er es nicht ausdrücklich beauftragt hat.

## Schnelleinstieg (nach der Übernahme)

```bash
uv sync
uv run pytest
uv run pre-commit run --all-files
uv run --group fuzz python fuzz/gribkit_fuzz.py idx -max_total_time=60 fuzz/korpus/idx   # nur Linux x86_64
```
