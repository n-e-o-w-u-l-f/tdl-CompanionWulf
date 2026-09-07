# tdl-CompanionWulf

Compañero persistente basado en SQLite, gestor de cola y capa guiada para [tdl](https://github.com/iyear/tdl).

**Versión:** 1.0.0 · [English](README.md) · [Todas las traducciones](README.TRANSLATIONS.md)

## Funciones

- cola, eventos, ajustes y asociaciones `tdata` persistentes en SQLite
- detección automática de idioma y opción `--language`
- asistente interactivo para chats, temas y medios
- búsqueda conocida o recursiva de `tdata` con bloqueos exclusivos
- arranque aislado de Telegram Desktop Portable en Windows
- perfiles de archivo/audio/imágenes/vídeo y controles de transferencia Sidecart
- `--tdl-path`, longitud de nombre configurable, comparación Size/Hash y `--dry-run`

## Instalación

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Inicio rápido

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Consulta la [documentación](docs/getting-started.md), la [matriz de paridad](PARITY.md) y el [registro de migración](MIGRATION.md).