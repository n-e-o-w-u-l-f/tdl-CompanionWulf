# Migration from tdl-companion and tdl-sidecart

`tdl-CompanionWulf` is the successor repository for the previous `tdl-companion` and `tdl-sidecart` work.

## Repository history

The final `tdl-companion` commit was merged into `tdl-CompanionWulf` as a real Git parent. Its final source commit is additionally referenced by the tag:

```text
legacy/tdl-companion-final
```

The former standalone `tdl-companion` GitHub repository was removed after its history and content were verified in the target repository.

## Sidecart source

The former `tdl-sidecart` 2.1.1 archive itself was not retained. Its unpacked source is stored under:

```text
legacy/tdl-sidecart-v2.1.1/
```

Those PowerShell files are reference material, not the active runtime implementation.

## Porting status

Already ported into the active Python package:

- durable queue and event storage
- durable CompanionWulf settings
- operating-system locale detection
- namespace and global transfer settings
- chat listing
- chat/topic JSON export orchestration
- interactive chat/topic selection and export/download wizard
- Telegram Desktop `tdata` known-path discovery
- namespace-to-`tdata` SQLite associations
- exclusive process-level `tdata` lease management
- interactive `auth auto` session import
- URL downloads with Sidecart-style transfer flags
- Sidecart archive/audio/image/video media profiles
- include/exclude extension filters
- safe filename template passed to `tdl`
- pre-download existing-file protection by remote hash/size when available

Still represented only by the legacy reference and scheduled for later native porting:

- recursive full-volume `tdata` search (intentionally not enabled by default)
- automatic isolated Telegram Desktop bootstrap

New development should target `src/tdl_companionwulf/` and add regression tests before removing any remaining legacy dependency or reference.
