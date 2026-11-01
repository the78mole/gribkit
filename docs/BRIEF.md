# Kickoff brief for the Claude session

The repository is on GitHub (`the78mole/gribkit`, public). Start a session on
https://claude.ai/code and select **both** repositories: `the78mole/gribkit` and
`the78mole/PredictionDB`. Then paste this text:

---

You are working in the new **gribkit** repository, in a cloud session. Read `CLAUDE.md` first, then
`docs/HANDOVER.md` in full and `docs/templates/CONVENTIONS.md`. Carry out the handover in this order
and tick off the acceptance criteria in section 9:

1. Import the history with `scripts/import-history.sh` (install git-filter-repo with
   `uv tool install git-filter-repo`). PR the78mole/PredictionDB#228 is merged, so the default ref
   `main` contains everything. Show me `git log --oneline` and the file list, and merge it with the
   handover commits. The script prints the commands at the end. This repository already has commits,
   so it is a merge with `--allow-unrelated-histories`.
   **Push this merge directly to `main`, not through a PR.** The repository only allows squash merges
   for PRs, and squashing would destroy the imported history. Ask me for the go-ahead before this
   push. If the ruleset `protect main` is already active, the push is refused: ask me to disable it
   for the import, and do not work around it.
2. Settle the open decisions in section 8 with me before building on them.
3. Build the package, docs, license, pre-commit, CI, fuzz, Scorecard and release workflows (Trusted
   Publishing), through PRs from now on. Templates are in `docs/templates/`. Translate the imported
   code to English as well (section 3). The release workflow may reach `main` only after my approval,
   because every commit on `main` publishes from then on.
4. Ask me before the first release goes to PyPI. I will set up the Pending Trusted Publisher on PyPI
   for it. Clean up the handover files before that (section 4).
5. After the first release: open a PR in the78mole/PredictionDB that switches to `gribkit~=0.2` from
   PyPI (section 7).

Talk to me in German; everything in the repository is in English.

Notes on the cloud environment:

- The GitHub proxy rejects `gh pr`, `gh issue` and other GraphQL commands. Use the REST API through
  `gh api`, for example for a PR:
  `gh api repos/the78mole/gribkit/pulls -f title=... -f head=... -f base=main`.
- The proxy only serves the repositories attached to the session. It also rejects pushing tags and
  deleting branches. The release workflow creates release tags in GitHub Actions. For the seed tag
  see section 5; if the REST call is refused too, ask me to create it locally.
- `~/.claude` (Daniel's skills and global rules) does not exist here. What you need from it is in
  `docs/templates/CONVENTIONS.md`.
- The branch ruleset is in `.github/rulesets/main.json`. GitHub does not apply this file by itself;
  Daniel applies it with `gh api`. It has no required status checks yet, because no CI exists. Once
  `ci.yml` runs, add the job names to the file (rule type `required_status_checks`, format in
  `docs/HANDOVER.md`, section 5) and tell Daniel to update the ruleset.
- The repository is set to squash merges only and deletes merged branches. The PR title becomes the
  commit message on `main` and decides the version bump, so it must be a Conventional Commit.

---
