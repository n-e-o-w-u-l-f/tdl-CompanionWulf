# tdl-CompanionWulf

Постоянен SQLite помощник, мениджър на опашка и воден интерфейс за [tdl](https://github.com/iyear/tdl).

**Версия:** 1.0.0 · [English](README.md) · [Всички преводи](README.TRANSLATIONS.md)

## Функции

- постоянна SQLite опашка, събития, настройки и `tdata` връзки
- автоматично разпознаване на език и `--language`
- интерактивен помощник за чатове, теми и медия
- познато или рекурсивно търсене на `tdata` с ексклузивни заключвания
- изолиран Telegram Desktop Portable bootstrap за Windows
- профили архив/аудио/изображения/видео и Sidecart опции
- `--tdl-path`, дължина на име, Size/Hash сравнение и `--dry-run`

## Инсталация

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Бърз старт

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Вижте [документацията](docs/getting-started.md), [матрицата за паритет](PARITY.md) и [миграцията](MIGRATION.md).