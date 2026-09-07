# tdl-CompanionWulf

Trvalý SQLite sprievodca, správca fronty a riadená vrstva príkazov pre [tdl](https://github.com/iyear/tdl).

**Verzia:** 1.0.0 · [English](README.md) · [Všetky preklady](README.TRANSLATIONS.md)

## Funkcie

- trvalá SQLite fronta, udalosti, nastavenia a väzby `tdata`
- automatická detekcia jazyka a `--language`
- interaktívny sprievodca chatmi, témami a médiami
- známe aj rekurzívne vyhľadávanie `tdata` s exkluzívnymi zámkami
- izolovaný bootstrap Telegram Desktop Portable vo Windows
- profily archív/audio/obrázky/video a možnosti prenosu Sidecart
- `--tdl-path`, nastaviteľná dĺžka názvu, porovnanie Size/Hash a `--dry-run`

## Inštalácia

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Rýchly štart

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Pozrite [dokumentáciu](docs/getting-started.md), [maticu parity](PARITY.md) a [migráciu](MIGRATION.md).