# Migration from tdl-companion and tdl-sidecart

`tdl-CompanionWulf` is the successor to the former `tdl-companion` repository and the `tdl-sidecart` 2.1.1 workflow.

## Repository history

The final `tdl-companion` history was merged into this repository as a real Git parent. The source endpoint was removed only after ancestry and metadata were checked. The historical source commit remains referenced by `legacy/tdl-companion-final`.

The Sidecart ZIP itself is not tracked. Its unpacked 2.1.1 source remains under `legacy/tdl-sidecart-v2.1.1/` for regression and historical reference.

## Porting status

Version 1.0.0 completes the functional Sidecart migration. The active implementation now includes:

- persistent queue, events, settings and namespace-to-`tdata` associations
- system language detection and explicit language selection
- chat listing and chat/topic export
- guided chat/topic/media workflow
- Sidecart media extension profiles and transfer options
- existing-file preservation with Size/Hash comparison
- configurable filename policy and explicit `tdl` executable path
- `tdata` known-path discovery and explicit recursive/full-volume scanning
- cross-process `tdata` leases and automatic parallel namespaces
- automatic `tdl login` import and authorization probing
- isolated Windows Telegram Desktop Portable bootstrap
- side-effect-free dry-run behavior

## Architectural replacements

Some Sidecart implementation details were intentionally replaced instead of translated line-for-line:

- PowerShell menu/rendering functions -> portable argparse CLI and wizard
- `NonInteractive` -> the non-interactive queue `run` command
- `NoPause` -> unnecessary; CompanionWulf does not introduce keypress pauses
- PowerShell state files -> SQLite plus OS-level lease files

See [PARITY.md](PARITY.md) for the feature mapping.

New development should target `src/tdl_companionwulf/`; files under `legacy/` are reference-only.
