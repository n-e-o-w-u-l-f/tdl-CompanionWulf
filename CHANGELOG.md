# Changelog

All notable changes to `tdl-CompanionWulf` are documented here.

## 1.0.1 - 2026-09-07

### Fixed

- force UTF-8 decoding for captured `tdl` text/JSON output on Windows instead of inheriting the ANSI code page (for example cp1252)
- prevent `UnicodeDecodeError` reader-thread crashes that could turn Wizard `stdout` into `None` and trigger a secondary JSON `TypeError`
- keep malformed output diagnostic-safe with replacement decoding instead of crashing the process reader

## 1.0.0 - 2026-09-07

### Added

- explicit recursive `tdata` scanning through `auth scan` and `auth auto --scan-root`
- safe full-volume discovery with symlink and pseudo/system-directory guards
- isolated Windows Telegram Desktop Portable bootstrap from the official Telegram source
- `auth bootstrap`, bootstrap timeout and opt-out controls
- explicit `--tdl-path`
- configurable maximum filename length
- Size/Hash existing-file comparison mode
- `--dry-run` / `--what-if-download` without queue side effects
- automatic parallel namespace generation when an implicit namespace is already leased
- restored legacy localized UI catalogs where Sidecart provided translations
- GitBook Git Sync structure and public project documentation
- English plus 20 localized README variants

### Migration

- functional parity with the former `tdl-sidecart` 2.1.1 workflow is complete
- PowerShell console renderers were replaced by the portable argparse CLI/wizard rather than copied verbatim
- `NonInteractive` is represented by the non-interactive `run` path
- `NoPause` is obsolete because CompanionWulf does not add artificial keypress pauses

## 0.6.0 - 2026-09-04

- pre-download preservation of conflicting existing files
- SHA-256-first comparison when the export supplies a digest, otherwise size fallback

## 0.5.0 - 2026-09-04

- Telegram Desktop `tdata` known-path discovery, leases, SQLite associations and auto-auth

## 0.4.0 - 2026-09-04

- interactive cross-platform chat/topic/media wizard

## 0.3.0 - 2026-09-04

- chat/topic export and Sidecart media profiles

## 0.2.0 - 2026-09-04

- merged legacy history, persistent settings, locale normalization and Sidecart transfer options
