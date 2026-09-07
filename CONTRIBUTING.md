# Contributing

Contributions should target the active Python implementation under `src/tdl_companionwulf/`.

## Workflow

1. Create a focused branch.
2. Add or update a regression test before changing behavior where practical.
3. Run `python -m unittest discover -s tests -v`.
4. Run `python -m compileall -q src tests` and check the diff for accidental generated files.
5. Update documentation when CLI behavior changes.
6. Open a pull request describing behavior, tests and compatibility impact.

Do not add Telegram session data, verification codes, passwords, tokens or private exports. Do not reintroduce ZIP-only source snapshots; legacy code is kept unpacked for reviewability.
