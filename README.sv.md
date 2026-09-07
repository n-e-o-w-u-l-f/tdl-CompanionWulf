# tdl-CompanionWulf

Beständig SQLite-baserad följeslagare, köhanterare och guidad kommandolager för [tdl](https://github.com/iyear/tdl).

**Version:** 1.0.0 · [English](README.md) · [Alla översättningar](README.TRANSLATIONS.md)

## Funktioner

- beständig SQLite-kö, händelser, inställningar och `tdata`-kopplingar
- automatisk språkidentifiering och `--language`
- interaktiv guide för chattar, ämnen och media
- känd eller rekursiv `tdata`-sökning med exklusiva lås
- isolerad Telegram Desktop Portable-bootstrap på Windows
- profiler för arkiv/ljud/bilder/video och Sidecart-alternativ
- `--tdl-path`, konfigurerbar filnamnslängd, Size/Hash-jämförelse och `--dry-run`

## Installation

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Snabbstart

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Se [dokumentation](docs/getting-started.md), [paritetsmatris](PARITY.md) och [migration](MIGRATION.md).