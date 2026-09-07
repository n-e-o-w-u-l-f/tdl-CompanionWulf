# Architecture

`tdl-CompanionWulf` is a standard-library-first Python command layer around `tdl`.

## Components

- `cli.py` — command parsing, SQLite queue/settings, orchestration and authorization flow
- `tdl.py` — deterministic `tdl` command builders
- `wizard.py` — chat/topic models, selection parsing and safe output components
- `media.py` — Sidecart media profiles
- `collisions.py` — exported-media parsing and existing-file preservation
- `tdata.py` — known and recursive `tdata` discovery plus leases
- `telegram_bootstrap.py` — isolated Windows portable client bootstrap
- SQLite — durable queue, events, settings and namespace associations

## Concurrency

SQLite uses WAL mode and a busy timeout. `tdata` directories use OS-level non-blocking locks stored beneath the CompanionWulf state directory. A process retains the lease while it uses an associated namespace.

## Safety model

- recursive scans are explicit and do not follow symlinks
- full-volume scanning is opt-in
- unknown remote file metadata never triggers speculative renames
- Telegram portable bootstrap validates source, archive structure and executable presence
- queue dry-run does not mutate job state

## Legacy boundary

`legacy/tdl-sidecart-v2.1.1/` is not imported by the runtime. It exists solely for historical and regression reference.
