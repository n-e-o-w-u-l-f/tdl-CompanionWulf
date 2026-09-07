# tdl-CompanionWulf

A persistent SQLite-backed companion, queue manager, authorization helper, and guided command layer for [tdl](https://github.com/iyear/tdl).

**Version:** 1.0.0  
**Languages:** [all README translations](README.TRANSLATIONS.md) · [Deutsch](README.de.md)

## What it does

`tdl-CompanionWulf` is the native successor to the former `tdl-sidecart` 2.1.1 workflow. Version 1.0.0 completes the functional migration while replacing PowerShell-specific UI helpers with a portable Python CLI.

Main capabilities:

- persistent SQLite queue, events, settings, and namespace-to-`tdata` associations
- automatic operating-system language detection plus `--language`
- `tdl chat ls`, protected chat/topic export, and media download orchestration
- interactive chat/topic/media wizard
- Telegram Desktop `tdata` known-path discovery and explicit recursive scanning
- exclusive process-level `tdata` leases and automatic parallel namespaces
- isolated Windows Telegram Desktop portable bootstrap when no reusable session exists
- archive/audio/image/video media profiles
- Sidecart transfer controls: namespace, limit, threads, delay, pool, proxy, NTP, storage, takeout, continue/restart, rewrite-ext, descending, group, include/exclude, templates
- explicit `--tdl-path`, configurable filename length, Size/Hash collision comparison, and `--dry-run` / `--what-if-download`
- conservative preservation of conflicting existing files

## Requirements

- Python 3.10 or newer
- `tdl` installed or an explicit `--tdl-path`
- Windows 10/11, Linux, or another Python-supported platform

## Install

Windows:

```powershell
py -3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

Linux:

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Quick start

```text
tdl-companionwulf doctor
tdl-companionwulf add https://t.me/example/1
tdl-companionwulf queue
tdl-companionwulf run --dry-run
tdl-companionwulf run
tdl-companionwulf status
```

## Guided Sidecart workflow

```text
tdl-companionwulf wizard --dir downloads --media audio,video
```

The wizard checks authorization, lists chats, accepts selections such as `1,3-5` or `all`, asks for forum topics, exports each selected chat/topic, protects conflicting existing files, and downloads the chosen media.

Useful compatibility controls:

```text
tdl-companionwulf wizard --language de --max-filename-length 180
tdl-companionwulf wizard --comparison hash --dry-run
tdl-companionwulf run --tdl-path /opt/bin/tdl --media audio
tdl-companionwulf run --what-if-download
```

`--dry-run` and `--what-if-download` are aliases. Queue dry-run does not start `tdl` and does not change job status, attempts, or events.

## Telegram Desktop authorization

```text
tdl-companionwulf auth status --namespace default
tdl-companionwulf auth candidates --namespace default
tdl-companionwulf auth scan ~/ --max-directories 25000
tdl-companionwulf auth auto --namespace default --scan-root ~/Telegram
tdl-companionwulf auth login --namespace default --tdata /path/to/tdata
```

On Windows, `auth auto` can fall back to the official Telegram Desktop portable package in an isolated CompanionWulf work directory. Disable this with `--no-bootstrap`.

Full-volume recursive search is explicit only:

```text
tdl-companionwulf auth scan --all-volumes
```

Symlinks are not followed and pseudo/system directories are skipped where appropriate.

## Storage

Windows:

```text
%LOCALAPPDATA%\tdl-CompanionWulf\companion.db
```

Linux/XDG:

```text
$XDG_STATE_HOME/tdl-CompanionWulf/companion.db
```

Without `XDG_STATE_HOME`, `~/.local/state` is used. SQLite WAL mode and a busy timeout are enabled.

## Documentation

- [Getting started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Authorization and tdata](docs/authorization.md)
- [Wizard](docs/wizard.md)
- [Queue and downloads](docs/queue.md)
- [Storage and concurrency](docs/storage.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture](ARCHITECTURE.md)
- [Sidecart parity matrix](PARITY.md)
- [Migration record](MIGRATION.md)

The repository contains `.gitbook.yaml` and `SUMMARY.md` for GitBook Git Sync.

## Legacy reference

The final unpacked Sidecart 2.1.1 source remains under `legacy/tdl-sidecart-v2.1.1/` for regression and historical reference. It is not the active runtime implementation.

No Telegram verification codes, passwords, session material, or secrets belong in this repository.
