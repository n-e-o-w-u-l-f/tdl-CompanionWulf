# tdl-sidecart 2.1.1 parity matrix

Version 1.0.0 is the functional replacement for the former Sidecart workflow.

| Legacy capability | CompanionWulf 1.0 |
| --- | --- |
| Chat discovery and selection | `chats`, `wizard` |
| Forum topic selection | `wizard` |
| Chat/topic JSON export | `export`, `wizard` |
| Media presets | `--media archive,audio,images,video` |
| Namespace, limit, threads, delay, pool | native CLI/settings |
| Proxy, NTP, storage | native CLI/settings |
| Takeout, continue/restart, rewrite-ext, desc, group | native CLI |
| Include/exclude and filename template | native CLI |
| Explicit tdl executable | `--tdl-path` |
| Max filename length | `--max-filename-length` |
| Existing-file protection | Size/Hash collision precheck |
| WhatIfDownload | `--dry-run` / `--what-if-download` |
| Known Telegram Desktop tdata paths | `auth candidates` / `auth auto` |
| Recursive/system tdata discovery | `auth scan`, `--scan-root`, `--all-volumes` |
| Namespace/tdata association | SQLite |
| tdata reservation | cross-process OS file lease |
| Parallel namespace | automatic `companion_<host>_<pid>` fallback |
| tdl login from tdata | `auth login`, `auth auto` |
| Isolated Telegram Desktop fallback | `auth bootstrap`, Windows auto fallback |
| System language selection | locale detection + `--language` |
| NonInteractive | `run` command |
| NoPause | obsolete; no artificial pause is added |
| PowerShell interactive renderer | portable CLI/wizard |

## Security boundary

CompanionWulf launches `tdl` or Telegram Desktop for interactive authorization. It does not collect Telegram verification codes or passwords itself, and session material must never be committed to Git.
