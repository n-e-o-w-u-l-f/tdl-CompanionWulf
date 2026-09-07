# tdl-CompanionWulf

Pysyvä SQLite-pohjainen kumppani, jononhallinta ja ohjattu komentokerros [tdl](https://github.com/iyear/tdl)-työkalulle.

**Versio:** 1.0.0 · [English](README.md) · [Kaikki käännökset](README.TRANSLATIONS.md)

## Ominaisuudet

- pysyvä SQLite-jono, tapahtumat, asetukset ja `tdata`-liitokset
- automaattinen kielen tunnistus ja `--language`
- interaktiivinen ohjattu toiminto chateille, aiheille ja medialle
- tunnettu tai rekursiivinen `tdata`-haku eksklusiivisilla lukoilla
- eristetty Telegram Desktop Portable -bootstrap Windowsissa
- arkisto/ääni/kuvat/video-profiilit ja Sidecart-siirtoasetukset
- `--tdl-path`, säädettävä tiedostonimen pituus, Size/Hash-vertailu ja `--dry-run`

## Asennus

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Pika-aloitus

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Katso [dokumentaatio](docs/getting-started.md), [pariteettimatriisi](PARITY.md) ja [migraatio](MIGRATION.md).