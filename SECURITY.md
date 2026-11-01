# Security Policy

## Supported versions

gribkit is maintained by one person in their spare time. Security fixes are made for the latest
release only.

| Version | Supported |
|---|---|
| latest release on PyPI and `main` | yes |
| older releases | no, please upgrade |

## Reporting a vulnerability

Please **do not open public issues, discussions or pull requests** for security vulnerabilities.

Report them privately through
[Report a vulnerability](https://github.com/the78mole/gribkit/security/advisories/new) (GitHub
private vulnerability reporting). Helpful details:

- the affected version or commit,
- a description of the vulnerability and its impact,
- steps to reproduce, ideally with a minimal input file,
- a suggested fix, if you have one.

## What you can expect

- An acknowledgement within **7 days**.
- A first assessment within **14 days**.
- A fix as quickly as a one-person project allows. The advisory shows the current status.
- The advisory is published after the fix. You are credited if you wish.

There is no bug bounty programme.

## Scope

In scope is the code in this repository: the `gribkit` package, its tests and fuzzers, and the
GitHub Actions workflows. gribkit parses untrusted input (`.idx` files and GRIB2 bytes from the
network); crashes other than the documented exceptions (`IdxParseError`, `HeaderError`,
`GribError`, `ValueError`), hangs or excessive memory use on crafted input are in scope.

Out of scope:

- Already published advisories for dependencies (ecCodes, NumPy). A pointer to the advisory can be
  an ordinary issue.
- The content and availability of external data sources (NOAA, AWS, Google Cloud).
