# tdl-CompanionWulf

Compagnon persistant basé sur SQLite, gestionnaire de file d’attente et interface guidée pour [tdl](https://github.com/iyear/tdl).

**Version :** 1.0.0 · [English](README.md) · [Toutes les traductions](README.TRANSLATIONS.md)

## Fonctionnalités

- file d’attente, événements, paramètres et associations `tdata` persistants dans SQLite
- détection automatique de la langue et option `--language`
- assistant interactif pour chats, sujets et médias
- recherche connue ou récursive de `tdata` et verrous exclusifs
- bootstrap Telegram Desktop portable isolé sous Windows
- profils archive/audio/images/vidéo et options de transfert Sidecart
- `--tdl-path`, longueur de nom configurable, comparaison Size/Hash et `--dry-run`

## Installation

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Démarrage rapide

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Voir la [documentation](docs/getting-started.md), la [matrice de parité](PARITY.md) et le [rapport de migration](MIGRATION.md).