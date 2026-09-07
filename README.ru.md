# tdl-CompanionWulf

Постоянный помощник на SQLite, менеджер очереди и управляемый интерфейс для [tdl](https://github.com/iyear/tdl).

**Версия:** 1.0.0 · [English](README.md) · [Все переводы](README.TRANSLATIONS.md)

## Возможности

- постоянная очередь SQLite, события, настройки и связи `tdata`
- автоматическое определение языка и `--language`
- интерактивный мастер чатов, тем и медиа
- поиск известных и рекурсивных `tdata` с эксклюзивными блокировками
- изолированный Telegram Desktop Portable bootstrap в Windows
- профили архив/аудио/изображения/видео и параметры Sidecart
- `--tdl-path`, длина имени файла, сравнение Size/Hash и `--dry-run`

## Установка

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Быстрый старт

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

См. [документацию](docs/getting-started.md), [матрицу соответствия](PARITY.md) и [миграцию](MIGRATION.md).