# tdl-CompanionWulf

Ein persistenter SQLite-basierter Begleiter, Queue-Manager, Authentifizierungshelfer und geführter Kommando-Layer für [tdl](https://github.com/iyear/tdl).

**Version:** 1.0.0  
**Sprachen:** [alle README-Übersetzungen](README.TRANSLATIONS.md) · [English](README.md)

## Funktionen

`tdl-CompanionWulf` ist der native Nachfolger des früheren `tdl-sidecart` 2.1.1. Version 1.0.0 schließt die funktionale Migration ab und ersetzt PowerShell-spezifische UI-Hilfen durch eine portable Python-CLI.

Enthalten sind unter anderem:

- persistente SQLite-Queue, Events, Einstellungen und Namespace-zu-`tdata`-Zuordnungen
- automatische Erkennung der Systemsprache plus `--language`
- `tdl chat ls`, geschützter Chat-/Topic-Export und Download-Orchestrierung
- interaktiver Chat-/Topic-/Medien-Assistent
- bekannte `tdata`-Pfade und explizite rekursive Suche
- exklusive Prozess-Leases für `tdata` und automatische Parallel-Namespaces
- isolierter Telegram-Desktop-Portable-Bootstrap unter Windows, wenn keine Sitzung wiederverwendbar ist
- Medienprofile für Archive, Audio, Bilder und Video
- Sidecart-Transferoptionen wie Namespace, Limit, Threads, Delay, Pool, Proxy, NTP, Storage, Takeout, Continue/Restart, Rewrite-Ext, Descending, Group, Include/Exclude und Templates
- expliziter `--tdl-path`, konfigurierbare Dateinamenslänge, Size-/Hash-Vergleich und `--dry-run` / `--what-if-download`
- konservativer Schutz vorhandener kollidierender Dateien

## Voraussetzungen

- Python 3.10 oder neuer
- installiertes `tdl` oder ein expliziter `--tdl-path`
- Windows 10/11, Linux oder eine andere von Python unterstützte Plattform

## Installation

Windows:

```powershell
py -3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

Linux:

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Schnellstart

```text
tdl-companionwulf doctor
tdl-companionwulf add https://t.me/example/1
tdl-companionwulf queue
tdl-companionwulf run --dry-run
tdl-companionwulf run
tdl-companionwulf status
```

## Geführter Sidecart-Ablauf

```text
tdl-companionwulf wizard --dir downloads --media audio,video
```

Der Assistent prüft die Authentifizierung, listet Chats, akzeptiert Auswahlen wie `1,3-5` oder `all`, fragt Forum-Topics ab, exportiert jeden ausgewählten Chat bzw. jedes Topic, schützt kollidierende vorhandene Dateien und lädt die gewählten Medien.

Nützliche Kompatibilitätsoptionen:

```text
tdl-companionwulf wizard --language de --max-filename-length 180
tdl-companionwulf wizard --comparison hash --dry-run
tdl-companionwulf run --tdl-path C:\Tools\tdl.exe --media audio
tdl-companionwulf run --what-if-download
```

`--dry-run` und `--what-if-download` sind Aliase. Beim Queue-Dry-Run wird `tdl` nicht gestartet und Jobstatus, Versuche und Events bleiben unverändert.

## Telegram-Desktop-Authentifizierung

```text
tdl-companionwulf auth status --namespace default
tdl-companionwulf auth candidates --namespace default
tdl-companionwulf auth scan C:\Users\me --max-directories 25000
tdl-companionwulf auth auto --namespace default --scan-root C:\Telegram
tdl-companionwulf auth login --namespace default --tdata C:\Pfad\zu\tdata
```

Unter Windows kann `auth auto` als letzten Fallback das offizielle Telegram-Desktop-Portable-Paket in einem isolierten CompanionWulf-Arbeitsverzeichnis starten. Mit `--no-bootstrap` lässt sich das abschalten.

Eine vollständige rekursive Volumesuche muss ausdrücklich angefordert werden:

```text
tdl-companionwulf auth scan --all-volumes
```

Symlinks werden nicht verfolgt; Pseudo- und Systemverzeichnisse werden soweit sinnvoll übersprungen.

## Speicherung

Windows:

```text
%LOCALAPPDATA%\tdl-CompanionWulf\companion.db
```

Linux/XDG:

```text
$XDG_STATE_HOME/tdl-CompanionWulf/companion.db
```

Ohne `XDG_STATE_HOME` wird `~/.local/state` verwendet. SQLite läuft im WAL-Modus mit Busy-Timeout.

## Dokumentation

- [Erste Schritte](docs/getting-started.md)
- [Konfiguration](docs/configuration.md)
- [Authentifizierung und tdata](docs/authorization.md)
- [Assistent](docs/wizard.md)
- [Queue und Downloads](docs/queue.md)
- [Speicherung und Parallelität](docs/storage.md)
- [Fehlerbehebung](docs/troubleshooting.md)
- [Architektur](ARCHITECTURE.md)
- [Sidecart-Paritätsmatrix](PARITY.md)
- [Migrationsnachweis](MIGRATION.md)

`.gitbook.yaml` und `SUMMARY.md` bereiten das Repository für GitBook Git Sync vor.

## Legacy-Referenz

Der letzte entpackte Sidecart-2.1.1-Quellstand bleibt unter `legacy/tdl-sidecart-v2.1.1/` als Regressions- und Historienreferenz erhalten. Er ist nicht die aktive Runtime-Implementierung.

Telegram-Codes, Passwörter, Sitzungsdaten oder andere Secrets gehören niemals in dieses Repository.
