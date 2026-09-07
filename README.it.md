# tdl-CompanionWulf

Companion persistente basato su SQLite, gestore della coda e interfaccia guidata per [tdl](https://github.com/iyear/tdl).

**Versione:** 1.0.0 · [English](README.md) · [Tutte le traduzioni](README.TRANSLATIONS.md)

## Funzioni

- coda, eventi, impostazioni e associazioni `tdata` persistenti in SQLite
- rilevamento automatico della lingua e opzione `--language`
- procedura guidata per chat, argomenti e media
- ricerca nota o ricorsiva di `tdata` con lease esclusivi
- bootstrap isolato di Telegram Desktop Portable su Windows
- profili archivio/audio/immagini/video e controlli di trasferimento Sidecart
- `--tdl-path`, lunghezza nome configurabile, confronto Size/Hash e `--dry-run`

## Installazione

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Avvio rapido

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Vedi [documentazione](docs/getting-started.md), [matrice di parità](PARITY.md) e [migrazione](MIGRATION.md).