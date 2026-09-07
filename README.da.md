# tdl-CompanionWulf

Vedvarende SQLite-baseret companion, køhåndtering og guidet kommandolag til [tdl](https://github.com/iyear/tdl).

**Version:** 1.0.0 · [English](README.md) · [Alle oversættelser](README.TRANSLATIONS.md)

## Funktioner

- vedvarende SQLite-kø, hændelser, indstillinger og `tdata`-tilknytninger
- automatisk sprogdetektion og `--language`
- interaktiv guide til chats, emner og medier
- kendt eller rekursiv `tdata`-søgning med eksklusive låse
- isoleret Telegram Desktop Portable-bootstrap på Windows
- arkiv/lyd/billeder/video-profiler og Sidecart-indstillinger
- `--tdl-path`, konfigurerbar filnavnelængde, Size/Hash-sammenligning og `--dry-run`

## Installation

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Hurtig start

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Se [dokumentation](docs/getting-started.md), [paritetsmatrix](PARITY.md) og [migration](MIGRATION.md).