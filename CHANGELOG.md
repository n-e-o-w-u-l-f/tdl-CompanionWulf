# Changelog

All notable changes to `tdl-CompanionWulf` are documented here.

## 0.6.0 - 2026-09-04

### Added

- pre-download protection for existing files in Wizard export jobs
- legacy and current export-media field parsing (`file`, `file_name`, `Media.Name`)
- remote size extraction with conservative unknown-size fallback
- optional SHA-256 extraction and hash-first collision comparison when the export supplies a digest
- Windows-safe media filename normalization and unique `name (n).ext` preservation
- `wizard --no-protect-existing` opt-out
- end-to-end regression coverage proving different-size local files survive a replacement download

### Safety

- files with unknown remote size/hash are never renamed speculatively
- unreadable export metadata falls back to `tdl --skip-same` instead of blocking the download

## 0.5.0 - 2026-09-04

### Added

- cross-platform Telegram Desktop `tdata` candidate model and known-path discovery
- exclusive OS-level `tdata` leases with process metadata
- durable namespace-to-`tdata` associations in SQLite
- `auth status`, `auth candidates`, `auth login`, and `auth auto` commands
- interactive Wizard authorization check and automatic authentication fallback
- process-lifetime lease retention for associated Wizard namespaces
- Telegram Desktop and iGram Desktop known-path compatibility
- login/auth integration tests using an isolated fake `tdl` executable

### Safety

- locked `tdata` candidates are not bypassed through native auto-detection
- background queue execution does not invoke interactive auto-auth implicitly

## 0.4.0 - 2026-09-04

### Added

- interactive cross-platform `wizard` workflow
- typed chat/topic model for `tdl chat ls -o json` output
- range and `all` selection parsing for chats and forum topics
- Windows-safe chat/topic output directory normalization
- protected chat/topic export-to-download orchestration
- fake-`tdl` end-to-end smoke coverage for the wizard flow

## 0.3.0 - 2026-09-04

### Added

- native `tdl chat export` command builder and CLI command
- topic, reply, export-range, filter, raw and content export options
- Sidecart media profiles for archive, audio, image and video extensions
- `run --media` profile selection with deterministic extension merging

## 0.2.0 - 2026-09-04

### Added

- merged history of the former `tdl-companion` repository
- preserved `tdl-sidecart` 2.1.1 source under `legacy/`
- persistent SQLite settings table
- automatic locale normalization for the former Sidecart language set
- reusable `tdl` global and download argument builders
- `chats` command with JSON and filter support
- Sidecart-style transfer options on `run`
- German README translation and migration documentation

### Fixed

- SQLite connections now close after context-manager use
- platform-neutral database path test coverage
- generated Python build artifacts are ignored
