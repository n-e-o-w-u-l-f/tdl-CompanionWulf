# tdl-CompanionWulf

Persistenter SQLite-basierter Begleiter, Queue-Manager und Kommando-Layer für [tdl](https://github.com/iyear/tdl).

**Sprache:** [English](README.md) · Deutsch

## Funktionen

`tdl-CompanionWulf` hält Download-Aufträge und Einstellungen unabhängig vom jeweils laufenden `tdl`-Prozess dauerhaft fest. Es verbindet die neue CompanionWulf-Datenbank mit den nützlichen Transferoptionen des früheren `tdl-sidecart`.

Aktuell enthalten:

- persistente SQLite-Download-Queue
- persistente Schlüssel/Wert-Einstellungen
- automatische Erkennung der Betriebssystemsprache
- `tdl chat ls` inklusive JSON-Ausgabe und Filter
- native Ausführung von `tdl dl` mit direkter Konsolenausgabe
- Namespace, Parallelität, Delay, Pool, Proxy, NTP und Storage
- Takeout, Fortsetzen, Neustart, Rewrite-Ext, Descending und Group
- Include-/Exclude-Filter und Dateinamens-Templates
- Ereignisprotokoll pro Queue-Auftrag

## Voraussetzungen

- Python 3.10 oder neuer
- `tdl` im `PATH`
- Windows 10/11, Linux oder eine andere von Python unterstützte Plattform

## Installation

Ohne lokale Git-Installation unter Windows:

```powershell
py -3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

Unter Linux:

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

Bei Installation über **PSTools-InstallerWulf** wird `tdl.exe` aus `C:\PS\binaries` verwendet. CompanionWulf liefert keine zweite Kopie von `tdl` mit.

## Schnellstart

```text
tdl-companionwulf doctor
tdl-companionwulf add https://t.me/example/1
tdl-companionwulf queue
tdl-companionwulf run
tdl-companionwulf status
```

Doppelte URLs werden nicht erneut angelegt. Fehlgeschlagene Jobs können mit `requeue <JOB_ID>` wieder in die Warteschlange gesetzt werden.

## Dauerhafte Konfiguration

Standardwerte lassen sich direkt in der CompanionWulf-Datenbank speichern:

```text
tdl-companionwulf config set namespace default
tdl-companionwulf config set limit 4
tdl-companionwulf config set threads 10
tdl-companionwulf config set download_dir D:\Telegram
tdl-companionwulf config list
```

Verwendbare Einstellungen sind unter anderem `namespace`, `limit`, `threads`, `delay`, `pool`, `proxy`, `ntp`, `reconnect_timeout`, `storage`, `download_dir` und `language`.

## Chats anzeigen

```text
tdl-companionwulf chats
tdl-companionwulf chats --json
tdl-companionwulf chats --filter "Type contains 'channel'"
```

## Sidecart-Transferoptionen

```text
tdl-companionwulf run --namespace default --limit 4 --threads 10 --delay 2 --takeout --group --rewrite-ext
```

`--continue` und `--restart` dürfen nicht gleichzeitig verwendet werden. Dasselbe gilt für `--include` und `--exclude`.

Die Medienprofile des früheren Sidecart können direkt ausgewählt werden:

```text
tdl-companionwulf run --media audio
tdl-companionwulf run --media audio,video
tdl-companionwulf run --media archive,images
```

Verfügbare Profile sind `archive`, `audio`, `images` und `video`.

## Chats und Topics exportieren

Geschützte Chats lassen sich vor dem Download als JSON exportieren:

```text
tdl-companionwulf export --chat 123456789 --output export.json
tdl-companionwulf export --chat 123456789 --topic 42 --type last --input 100 --output topic.json
tdl-companionwulf export --chat @channel --all --with-content --output messages.json
```

`--type` unterstützt `time`, `id` und `last`; `--input` verwendet das zugehörige Bereichsformat von `tdl chat export`.

## Interaktiver Assistent

Der geführte Sidecart-Ablauf steht jetzt plattformübergreifend zur Verfügung:

```text
tdl-companionwulf wizard --dir downloads --media audio,video
```

Der Assistent lädt Chats über `tdl chat ls -o json`, akzeptiert Auswahlen wie `1,3-5` oder `all`, fragt bei Forum-Chats die Topics ab, exportiert jeden ausgewählten Chat bzw. jedes Topic als JSON und lädt anschließend die gewählten Medien in sichere Chat-/Topic-Unterverzeichnisse.

## Datenbank

Windows:

```text
%LOCALAPPDATA%\tdl-CompanionWulf\companion.db
```

Linux/XDG:

```text
$XDG_STATE_HOME/tdl-CompanionWulf/companion.db
```

Ohne `XDG_STATE_HOME` wird `~/.local/state` verwendet. SQLite arbeitet mit WAL-Modus und Busy-Timeout.

## Sprache

Die Systemsprache wird automatisch erkannt. Unterstützt werden die Sprachcodes für Deutsch, Englisch, Französisch, Spanisch, Italienisch, Portugiesisch, Niederländisch, Polnisch, Tschechisch, Slowakisch, Ungarisch, Rumänisch, Türkisch, Russisch, Ukrainisch, Bulgarisch, Griechisch, Schwedisch, Dänisch, Norwegisch und Finnisch. Nicht separat übersetzte Texte fallen auf Englisch zurück.

```text
tdl-companionwulf config set language de
tdl-companionwulf config set language auto
```

## Alter Sidecart

Der letzte Quellstand von `tdl-sidecart` 2.1.1 liegt nur noch als Migrations- und Regressionsreferenz unter `legacy/tdl-sidecart-v2.1.1/`. Die aktive Implementierung befindet sich unter `src/tdl_companionwulf/`.

Weitere Einzelheiten stehen in [MIGRATION.md](MIGRATION.md).
