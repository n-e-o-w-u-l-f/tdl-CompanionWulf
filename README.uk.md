# tdl-CompanionWulf

Постійний помічник на SQLite, менеджер черги та керований інтерфейс для [tdl](https://github.com/iyear/tdl).

**Версія:** 1.0.0 · [English](README.md) · [Усі переклади](README.TRANSLATIONS.md)

## Можливості

- постійна черга SQLite, події, налаштування та зв’язки `tdata`
- автоматичне визначення мови та `--language`
- інтерактивний майстер чатів, тем і медіа
- відомий або рекурсивний пошук `tdata` з ексклюзивними блокуваннями
- ізольований Telegram Desktop Portable bootstrap у Windows
- профілі архів/аудіо/зображення/відео та опції Sidecart
- `--tdl-path`, довжина імені файлу, порівняння Size/Hash та `--dry-run`

## Встановлення

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Швидкий старт

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Див. [документацію](docs/getting-started.md), [матрицю паритету](PARITY.md) і [міграцію](MIGRATION.md).