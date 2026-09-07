# tdl-CompanionWulf

Vedvarende SQLite-basert companion, købehandler og veiledet kommandolag for [tdl](https://github.com/iyear/tdl).

**Versjon:** 1.0.0 · [English](README.md) · [Alle oversettelser](README.TRANSLATIONS.md)

## Funksjoner

- vedvarende SQLite-kø, hendelser, innstillinger og `tdata`-koblinger
- automatisk språkdeteksjon og `--language`
- interaktiv veiviser for chatter, emner og media
- kjent eller rekursivt `tdata`-søk med eksklusive låser
- isolert Telegram Desktop Portable-bootstrap på Windows
- arkiv/lyd/bilder/video-profiler og Sidecart-alternativer
- `--tdl-path`, konfigurerbar filnavnlengde, Size/Hash-sammenligning og `--dry-run`

## Installasjon

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Hurtigstart

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Se [dokumentasjon](docs/getting-started.md), [paritetsmatrise](PARITY.md) og [migrasjon](MIGRATION.md).