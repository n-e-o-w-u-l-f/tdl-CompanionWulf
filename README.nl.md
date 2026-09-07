# tdl-CompanionWulf

Permanente SQLite-gebaseerde companion, wachtrijbeheerder en begeleide interface voor [tdl](https://github.com/iyear/tdl).

**Versie:** 1.0.0 · [English](README.md) · [Alle vertalingen](README.TRANSLATIONS.md)

## Functies

- blijvende SQLite-wachtrij, events, instellingen en `tdata`-koppelingen
- automatische taaldetectie en `--language`
- interactieve wizard voor chats, topics en media
- bekende of recursieve `tdata`-zoekactie met exclusieve leases
- geïsoleerde Telegram Desktop Portable-bootstrap op Windows
- archief/audio/afbeeldingen/video-profielen en Sidecart-transferopties
- `--tdl-path`, instelbare bestandsnaamlengte, Size/Hash-vergelijking en `--dry-run`

## Installatie

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Snel starten

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Zie [documentatie](docs/getting-started.md), [pariteitsmatrix](PARITY.md) en [migratie](MIGRATION.md).