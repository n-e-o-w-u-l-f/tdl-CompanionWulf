# tdl-CompanionWulf

Tartós SQLite-alapú kísérő, sorkezelő és vezetett parancsréteg a [tdl](https://github.com/iyear/tdl) számára.

**Verzió:** 1.0.0 · [English](README.md) · [Minden fordítás](README.TRANSLATIONS.md)

## Funkciók

- tartós SQLite sor, események, beállítások és `tdata` társítások
- automatikus nyelvfelismerés és `--language`
- interaktív varázsló csevegésekhez, témákhoz és médiához
- ismert és rekurzív `tdata` keresés kizárólagos zárolással
- izolált Telegram Desktop Portable bootstrap Windowson
- archívum/audio/kép/videó profilok és Sidecart átviteli opciók
- `--tdl-path`, állítható fájlnévhossz, Size/Hash összehasonlítás és `--dry-run`

## Telepítés

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Gyors kezdés

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Lásd a [dokumentációt](docs/getting-started.md), a [paritási mátrixot](PARITY.md) és a [migrációt](MIGRATION.md).