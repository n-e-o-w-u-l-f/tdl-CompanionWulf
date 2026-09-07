# Configuration

CompanionWulf stores reusable defaults in SQLite.

```text
tdl-companionwulf config set namespace default
tdl-companionwulf config set limit 4
tdl-companionwulf config set threads 10
tdl-companionwulf config set download_dir D:\Telegram
tdl-companionwulf config set language auto
tdl-companionwulf config list
```

Runtime CLI values override persisted defaults.

Common settings include `namespace`, `limit`, `threads`, `delay`, `pool`, `proxy`, `ntp`, `reconnect_timeout`, `storage`, `download_dir` and `language`.

Legacy-compatible runtime controls include `--tdl-path`, `--max-filename-length`, `--comparison size|hash` and `--dry-run` / `--what-if-download`.
