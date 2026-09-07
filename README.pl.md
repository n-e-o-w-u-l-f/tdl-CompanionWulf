# tdl-CompanionWulf

Trwały asystent oparty na SQLite, menedżer kolejki i prowadzona warstwa poleceń dla [tdl](https://github.com/iyear/tdl).

**Wersja:** 1.0.0 · [English](README.md) · [Wszystkie tłumaczenia](README.TRANSLATIONS.md)

## Funkcje

- trwała kolejka SQLite, zdarzenia, ustawienia i powiązania `tdata`
- automatyczne wykrywanie języka i `--language`
- interaktywny kreator czatów, tematów i multimediów
- znane i rekurencyjne wyszukiwanie `tdata` z wyłącznymi blokadami
- izolowany bootstrap Telegram Desktop Portable w Windows
- profile archiwum/audio/obrazy/wideo i opcje transferu Sidecart
- `--tdl-path`, konfigurowalna długość nazwy, porównanie Size/Hash i `--dry-run`

## Instalacja

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Szybki start

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Zobacz [dokumentację](docs/getting-started.md), [macierz zgodności](PARITY.md) i [migrację](MIGRATION.md).