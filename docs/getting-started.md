# Getting started

## 1. Install prerequisites

Install Python 3.10+ and `tdl`. If `tdl` is not in `PATH`, pass `--tdl-path` on commands that invoke it.

## 2. Install CompanionWulf

```bash
python3 -m pip install "https://github.com/n-e-o-w-u-l-f/tdl-CompanionWulf/archive/refs/heads/main.zip"
```

## 3. Verify the runtime

```text
tdl-companionwulf --version
tdl-companionwulf doctor
```

## 4. Choose a workflow

Queue workflow:

```text
tdl-companionwulf add https://t.me/example/1
tdl-companionwulf queue
tdl-companionwulf run --dry-run
tdl-companionwulf run
```

Guided Sidecart workflow:

```text
tdl-companionwulf wizard --dir downloads --media audio,video
```

Authorization help is documented in [authorization.md](authorization.md).