# Changelog

All notable changes to `tdl-CompanionWulf` are documented here.

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
