# tdl-CompanionWulf

Companheiro persistente baseado em SQLite, gestor de fila e interface guiada para [tdl](https://github.com/iyear/tdl).

**Versão:** 1.0.0 · [English](README.md) · [Todas as traduções](README.TRANSLATIONS.md)

## Recursos

- fila, eventos, definições e associações `tdata` persistentes em SQLite
- deteção automática do idioma e opção `--language`
- assistente interativo para chats, tópicos e multimédia
- pesquisa conhecida ou recursiva de `tdata` com leases exclusivos
- bootstrap isolado do Telegram Desktop Portable no Windows
- perfis arquivo/áudio/imagens/vídeo e controlos Sidecart
- `--tdl-path`, comprimento de nome configurável, comparação Size/Hash e `--dry-run`

## Instalação

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## Início rápido

```text
tdl-companionwulf doctor
tdl-companionwulf wizard --dir downloads --media audio,video
tdl-companionwulf auth auto --namespace default
```

Consulte a [documentação](docs/getting-started.md), a [matriz de paridade](PARITY.md) e a [migração](MIGRATION.md).