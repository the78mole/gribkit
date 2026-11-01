# Startauftrag für die Claude-Sitzung

Das Repo liegt auf GitHub (`the78mole/gribkit`, zunächst **privat**). Sitzung auf
https://claude.ai/code starten und **beide Repos** auswählen: `the78mole/gribkit` und
`the78mole/PredictionDB`. Dann diesen Text einfügen:

---

Du arbeitest im neuen Repo **gribkit**, in einer Cloud-Sitzung. Lies zuerst `CLAUDE.md`, dann
`docs/UEBERGABE.md` vollständig und `docs/vorlagen/KONVENTIONEN.md`. Setze die Übergabe um, in
dieser Reihenfolge, und hake die Abnahmekriterien in Abschnitt 9 ab:

1. Prüfe, ob PR the78mole/PredictionDB#228 gemergt ist
   (`gh api repos/the78mole/PredictionDB/pulls/228 --jq '.state,.merged'`). Wenn nicht, frag mich,
   ob wir warten oder vom PR-Branch übernehmen.
2. Übernimm die Historie mit `scripts/historie-uebernehmen.sh` (git-filter-repo per
   `uv tool install git-filter-repo`), zeig mir `git log --oneline` und die Dateiliste, und führe
   sie mit dem Übergabe-Commit zusammen. Das Skript nennt am Ende die Befehle. Dieses Repo hat schon
   Commits, also ist es ein Merge mit `--allow-unrelated-histories`.
   **Diesen Merge niemals squashen oder rebasen,** sonst ist die Historie weg. Falls als PR, dann
   nur mit der Merge-Methode `merge`.
3. Kläre mit mir die offenen Entscheidungen aus Abschnitt 8 und die Widersprüche am Ende von
   `docs/vorlagen/KONVENTIONEN.md`, bevor Du darauf aufbaust.
4. Baue Paket, Doku, Lizenz, pre-commit, CI, Fuzz-, Scorecard- und Release-Workflow
   (Trusted Publishing) auf. Vorlagen liegen unter `docs/vorlagen/`. Der Release-Workflow darf
   erst nach meiner Freigabe auf `main` landen, weil er sonst beim Merge schon veröffentlicht.
5. Frag mich, bevor das Repo öffentlich wird und bevor das erste Release auf PyPI geht. Ich lege
   dafür den Pending Trusted Publisher auf PyPI an. Vor dem Öffnen prüfen, dass die Übergabe-Dateien
   aufgeräumt sind (Abschnitt 4). Sie bleiben in der Historie sichtbar.
6. Nach dem ersten Release: PR in the78mole/PredictionDB, der auf `gribkit~=0.2` von PyPI
   umstellt (Abschnitt 7).

Sprich mit mir Deutsch; alles Öffentliche im Repo ist Englisch.

Besonderheiten der Cloud-Umgebung:

- `gh pr`, `gh issue` und andere GraphQL-Befehle lehnt der GitHub-Proxy ab. Nimm die REST-API über
  `gh api`, z. B. für einen PR `gh api repos/the78mole/gribkit/pulls -f title=... -f head=... -f base=main`.
- Der Proxy bedient nur die Repos, die an der Sitzung hängen. Tags lassen sich nicht pushen, auch
  keine Branches löschen. Tags erzeugt der Release-Workflow in GitHub Actions.
- `~/.claude` (Daniels Skills und globale Regeln) gibt es hier nicht; das Nötige steht in
  `docs/vorlagen/KONVENTIONEN.md`.
- Der Branch-Ruleset (`docs/vorlagen/ruleset-main.json`) nennt die Check-Namen von PredictionDB.
  Erst zuletzt einrichten, mit den Job-Namen aus der neuen `ci.yml`.

---
