#!/usr/bin/env bash
# Übernimmt gribkit mit Git-Historie aus the78mole/PredictionDB.
#
# Voraussetzungen: git, git-filter-repo (z. B. `uv tool install git-filter-repo`).
# Aufruf aus dem Wurzelverzeichnis dieses Repos:
#
#   scripts/historie-uebernehmen.sh            # nimmt origin/main von PredictionDB
#   REF=claude/project-thread-d8ivg0 scripts/historie-uebernehmen.sh   # z. B. PR-Branch von #228
#
# Ergebnis: Verzeichnis ../gribkit-historie mit umgeschriebener Historie (nur gribkit-Pfade,
# packages/gribkit/ -> Wurzel). Dieses Repo wird NICHT verändert; das Zusammenführen geschieht
# danach von Hand (siehe Ende des Skripts), damit man das Ergebnis vorher prüfen kann.
set -euo pipefail

SRC_URL="${SRC_URL:-https://github.com/the78mole/PredictionDB.git}"
REF="${REF:-main}"
WORK="$(mktemp -d)"
OUT="${OUT:-$(cd .. && pwd)/gribkit-historie}"

if [[ -e "$OUT" ]]; then
  echo "Ziel $OUT existiert schon, bitte erst entfernen." >&2
  exit 1
fi

echo "Klone $SRC_URL ($REF) nach $WORK ..."
git clone --no-local --single-branch --branch "$REF" "$SRC_URL" "$WORK/repo"
cd "$WORK/repo"

# Nur gribkit und das, was aus PR #228 dazugehört.
git filter-repo --force \
  --path packages/gribkit/ \
  --path fuzz/ \
  --path .github/workflows/fuzz.yml \
  --path-rename packages/gribkit/: \
  --replace-message <(printf 'regex:\\(#([0-9]+)\\)==>(the78mole/PredictionDB#\\1)\n')

# Kontrolle
echo
echo "Commits: $(git rev-list --count HEAD)"
echo "Dateien:"
git ls-files | sed 's/^/  /'
echo

mv "$WORK/repo" "$OUT"
rm -rf "$WORK"

cat <<EOF
Fertig: $OUT

Prüfen:
  git -C "$OUT" log --stat | less
  (cd "$OUT" && uv run --with pytest --with hypothesis pytest)   # pyproject liegt jetzt an der Wurzel

Zusammenführen mit diesem Repo (der Übergabe-Commit liegt schon vor, nicht squashen):
  git remote add historie "$OUT"
  git fetch historie
  git merge --allow-unrelated-histories --signoff \\
    -m "chore: import gribkit history from PredictionDB" historie/$REF
  git remote remove historie
EOF
