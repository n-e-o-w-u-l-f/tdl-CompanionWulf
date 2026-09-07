# tdl-CompanionWulf

Companion persistent bazat pe SQLite, manager de coadă și interfață ghidată pentru [tdl](https://github.com/iyear/tdl).

**Versiune:** 1.0.0 · [English](README.md) · [Toate traducerile](README.TRANSLATIONS.md)

## Funcții

- coadă SQLite persistentă, evenimente, setări și asocieri `tdata`
- detectare automată a limbii și `--language`
- asistent interactiv pentru chat-uri, subiecte și media
- căutare cunoscută sau recursivă `tdata` cu blocări exclusive
- bootstrap izolat Telegram Desktop Portable pe Windows
- profiluri arhivă/audio/imagini/video și opțiuni de transfer Sidecart
- `--tdl-path`, lungime configurabilă a numelui, comparație Size/Hash și `--dry-run`

## Instalare

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Pornire rapidă

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Consultați [documentația](docs/getting-started.md), [matricea de paritate](PARITY.md) și [migrarea](MIGRATION.md).