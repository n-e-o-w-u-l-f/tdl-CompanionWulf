# tdl-CompanionWulf

Μόνιμος βοηθός SQLite, διαχειριστής ουράς και καθοδηγούμενο επίπεδο εντολών για το [tdl](https://github.com/iyear/tdl).

**Έκδοση:** 1.0.0 · [English](README.md) · [Όλες οι μεταφράσεις](README.TRANSLATIONS.md)

## Δυνατότητες

- μόνιμη ουρά SQLite, συμβάντα, ρυθμίσεις και συσχετίσεις `tdata`
- αυτόματη ανίχνευση γλώσσας και `--language`
- διαδραστικός οδηγός για chats, topics και media
- γνωστή ή αναδρομική αναζήτηση `tdata` με αποκλειστικά locks
- απομονωμένο Telegram Desktop Portable bootstrap στα Windows
- προφίλ archive/audio/images/video και επιλογές Sidecart
- `--tdl-path`, μήκος ονόματος, σύγκριση Size/Hash και `--dry-run`

## Εγκατάσταση

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Γρήγορη έναρξη

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Δείτε [τεκμηρίωση](docs/getting-started.md), [πίνακα ισοδυναμίας](PARITY.md) και [μετανάστευση](MIGRATION.md).