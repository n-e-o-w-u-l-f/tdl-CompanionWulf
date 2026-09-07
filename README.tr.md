# tdl-CompanionWulf

[tdl](https://github.com/iyear/tdl) için kalıcı SQLite tabanlı yardımcı, kuyruk yöneticisi ve yönlendirmeli komut katmanı.

**Sürüm:** 1.0.0 · [English](README.md) · [Tüm çeviriler](README.TRANSLATIONS.md)

## Özellikler

- kalıcı SQLite kuyruğu, olaylar, ayarlar ve `tdata` eşlemeleri
- otomatik dil algılama ve `--language`
- sohbet, konu ve medya için etkileşimli sihirbaz
- bilinen veya özyinelemeli `tdata` araması ve özel kilitler
- Windows'ta yalıtılmış Telegram Desktop Portable bootstrap
- arşiv/ses/görüntü/video profilleri ve Sidecart aktarım seçenekleri
- `--tdl-path`, yapılandırılabilir dosya adı uzunluğu, Size/Hash karşılaştırması ve `--dry-run`

## Kurulum

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Hızlı başlangıç

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Bkz. [belgeler](docs/getting-started.md), [parite matrisi](PARITY.md) ve [geçiş kaydı](MIGRATION.md).