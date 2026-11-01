#!/usr/bin/env bash
# Imports gribkit with its Git history from the78mole/PredictionDB.
#
# Requirements: git, git-filter-repo (e.g. `uv tool install git-filter-repo`).
# Run from the root of this repository:
#
#   scripts/import-history.sh            # uses origin/main of PredictionDB
#   REF=claude/project-thread-d8ivg0 scripts/import-history.sh   # e.g. the PR branch of #228
#
# Result: directory ../gribkit-history with rewritten history (gribkit paths only,
# packages/gribkit/ -> root). This repository is NOT changed; the merge is done by hand afterwards
# (see the end of this script), so the result can be checked first.
set -euo pipefail

SRC_URL="${SRC_URL:-https://github.com/the78mole/PredictionDB.git}"
REF="${REF:-main}"
WORK="$(mktemp -d)"
OUT="${OUT:-$(cd .. && pwd)/gribkit-history}"

if [[ -e "$OUT" ]]; then
  echo "Target $OUT already exists, please remove it first." >&2
  exit 1
fi

echo "Cloning $SRC_URL ($REF) to $WORK ..."
git clone --no-local --single-branch --branch "$REF" "$SRC_URL" "$WORK/repo"
cd "$WORK/repo"

# Only gribkit and what belongs to it from PR #228.
git filter-repo --force \
  --path packages/gribkit/ \
  --path fuzz/ \
  --path .github/workflows/fuzz.yml \
  --path-rename packages/gribkit/: \
  --replace-message <(printf 'regex:\\(#([0-9]+)\\)==>(the78mole/PredictionDB#\\1)\n')

# Check
echo
echo "Commits: $(git rev-list --count HEAD)"
echo "Files:"
git ls-files | sed 's/^/  /'
echo

mv "$WORK/repo" "$OUT"
rm -rf "$WORK"

cat <<EOF
Done: $OUT

To check:
  git -C "$OUT" log --stat | less
  (cd "$OUT" && uv run --with pytest --with hypothesis pytest)   # pyproject is at the root now

To merge with this repository (the handover commits already exist, do not squash):
  git remote add history "$OUT"
  git fetch history
  git merge --allow-unrelated-histories --signoff \\
    -m "chore: import gribkit history from PredictionDB" history/$REF
  git remote remove history
EOF
