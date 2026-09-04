# tdl-CompanionWulf

SQLite-backed companion and queue manager for [tdl](https://github.com/iyear/tdl).

## Requirements

- Windows 10/11 or another Python-supported platform
- Python 3.10+
- `tdl` available in `PATH`

When installed through **PSTools-InstallerWulf**, `tdl.exe` is provided through `C:\PS\binaries` and CompanionWulf reuses that installation instead of bundling a duplicate binary.

## Install

No local Git installation is required:

```powershell
py -3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

The PSTools-InstallerWulf uses the same source-archive strategy inside an isolated virtual environment.

## Commands

```text
tdl-companionwulf doctor
tdl-companionwulf add https://t.me/...
tdl-companionwulf queue
tdl-companionwulf status
tdl-companionwulf run
tdl-companionwulf requeue <JOB_ID>
```

## Storage

On Windows the SQLite database is stored below:

```text
%LOCALAPPDATA%\tdl-CompanionWulf\companion.db
```

The database uses WAL mode and keeps the persistent queue independently of downloaded files.

## Language

The CLI detects the operating-system locale automatically. German is currently provided explicitly; other locales fall back to English.

## Design

CompanionWulf intentionally does not redistribute `tdl.exe`. The executable is discovered through the system `PATH`, with `C:\PS\binaries\tdl.exe` as the Windows fallback used by PSTools-InstallerWulf.
