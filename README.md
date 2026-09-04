# tdl-CompanionWulf

A persistent SQLite-backed companion, queue manager, and command layer for [tdl](https://github.com/iyear/tdl).

**Language:** English · [Deutsch](README.de.md)

## What it does

`tdl-CompanionWulf` keeps download work and defaults outside the transient `tdl` process. It combines the durable queue introduced by CompanionWulf with the useful transfer controls from the former `tdl-sidecart` project.

Current capabilities include:

- persistent SQLite download queue
- persistent key/value settings
- automatic operating-system language detection
- `tdl chat ls` integration, including JSON output and filters
- native `tdl dl` execution with inherited console output
- namespace, concurrency, delay, pool, proxy, NTP and storage options
- takeout, resume, restart, rewrite-extension, descending and group options
- include/exclude extension filters and filename templates
- event history for queued jobs

## Requirements

- Python 3.10 or newer
- `tdl` available in `PATH`
- Windows 10/11, Linux, or another Python-supported platform

## Install

No local Git installation is required:

```powershell
py -3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

On Linux:

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

When installed through **PSTools-InstallerWulf**, CompanionWulf reuses `tdl.exe` from `C:\PS\binaries` instead of shipping another copy.

## Quick start

```text
tdl-companionwulf doctor
tdl-companionwulf add https://t.me/example/1
tdl-companionwulf queue
tdl-companionwulf run
tdl-companionwulf status
```

Queued URLs are deduplicated. Failed jobs can be returned to the waiting state with `requeue <JOB_ID>`.

## Persistent configuration

Defaults can be stored in the CompanionWulf database:

```text
tdl-companionwulf config set namespace default
tdl-companionwulf config set limit 4
tdl-companionwulf config set threads 10
tdl-companionwulf config set download_dir D:\Telegram
tdl-companionwulf config list
```

Supported runtime settings include `namespace`, `limit`, `threads`, `delay`, `pool`, `proxy`, `ntp`, `reconnect_timeout`, `storage`, `download_dir`, and `language`.

## List chats

```text
tdl-companionwulf chats
tdl-companionwulf chats --json
tdl-companionwulf chats --filter "Type contains 'channel'"
```

The command delegates to the installed `tdl` executable and uses the same namespace and connection settings as downloads.

## Sidecart-style transfer options

```text
tdl-companionwulf run --namespace default --limit 4 --threads 10 --delay 2 --takeout --group --rewrite-ext
```

Use `--continue` or `--restart` to resume or restart a transfer; they are intentionally mutually exclusive. `--include` and `--exclude` are also mutually exclusive.

Media profiles from the former Sidecart can be selected directly:

```text
tdl-companionwulf run --media audio
tdl-companionwulf run --media audio,video
tdl-companionwulf run --media archive,images
```

Available profiles are `archive`, `audio`, `images`, and `video`.

## Export chats and topics

Protected chats can be exported to JSON before downloading:

```text
tdl-companionwulf export --chat 123456789 --output export.json
tdl-companionwulf export --chat 123456789 --topic 42 --type last --input 100 --output topic.json
tdl-companionwulf export --chat @channel --all --with-content --output messages.json
```

`--type` accepts `time`, `id`, or `last`; `--input` follows the corresponding `tdl chat export` range format.

## Telegram Desktop authorization

CompanionWulf can inspect and import existing Telegram Desktop sessions without copying credentials into the repository:

```text
tdl-companionwulf auth status --namespace default
tdl-companionwulf auth candidates --namespace default
tdl-companionwulf auth login --namespace default --tdata "C:\\Users\\me\\AppData\\Roaming\\Telegram Desktop\\tdata"
tdl-companionwulf auth auto --namespace default
```

`auth auto` first checks the current namespace, then tries its stored `tdata` association and known Telegram Desktop/iGram locations. Each candidate is protected by an exclusive OS-level lease while it is imported. The successful namespace association is stored in SQLite.

## Interactive wizard

The Sidecart-style guided flow is available as a native cross-platform command:

```text
tdl-companionwulf wizard --dir downloads --media audio,video
```

The wizard checks authorization automatically, loads chats through `tdl chat ls -o json`, accepts selections such as `1,3-5` or `all`, requests topic selections for forum chats, exports each selected chat/topic to JSON, and then downloads the selected media into safe chat/topic subdirectories. Use `--no-auto-auth` to disable the interactive authentication fallback.

## Storage

Windows database location:

```text
%LOCALAPPDATA%\tdl-CompanionWulf\companion.db
```

Linux and other XDG systems use:

```text
$XDG_STATE_HOME/tdl-CompanionWulf/companion.db
```

If `XDG_STATE_HOME` is not set, `~/.local/state` is used. SQLite WAL mode and a busy timeout are enabled for safer concurrent access.

## Language detection

`tdl-CompanionWulf` detects the system locale automatically. The detection layer recognizes German, English, French, Spanish, Italian, Portuguese, Dutch, Polish, Czech, Slovak, Hungarian, Romanian, Turkish, Russian, Ukrainian, Bulgarian, Greek, Swedish, Danish, Norwegian and Finnish locale codes. Text without a dedicated translation falls back to English.

A language can be persisted explicitly:

```text
tdl-companionwulf config set language de
tdl-companionwulf config set language auto
```

## Legacy sidecart

The final `tdl-sidecart` 2.1.1 source is retained under `legacy/tdl-sidecart-v2.1.1/` for migration and regression reference only. The active implementation is the Python package under `src/tdl_companionwulf/`.

See [MIGRATION.md](MIGRATION.md) for details.
