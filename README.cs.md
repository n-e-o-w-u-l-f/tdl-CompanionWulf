# tdl-CompanionWulf

Trvalý SQLite průvodce, správce fronty a řízená vrstva příkazů pro [tdl](https://github.com/iyear/tdl).

**Verze:** 1.0.0 · [English](README.md) · [Všechny překlady](README.TRANSLATIONS.md)

## Funkce

- trvalá SQLite fronta, události, nastavení a vazby `tdata`
- automatická detekce jazyka a `--language`
- interaktivní průvodce chaty, tématy a médii
- známé i rekurzivní hledání `tdata` s exkluzivními zámky
- izolovaný bootstrap Telegram Desktop Portable ve Windows
- profily archiv/audio/obrázky/video a přenosové volby Sidecart
- `--tdl-path`, nastavitelná délka názvu, porovnání Size/Hash a `--dry-run`

## Instalace

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Rychlý start

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Viz [dokumentace](docs/getting-started.md), [matice parity](PARITY.md) a [migrace](MIGRATION.md).