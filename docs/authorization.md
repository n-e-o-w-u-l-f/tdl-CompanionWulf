# Authorization and tdata

CompanionWulf does not collect Telegram verification codes or passwords.

## Inspect authorization

```text
tdl-companionwulf auth status --namespace default
tdl-companionwulf auth candidates --namespace default
```

## Import a known tdata directory

```text
tdl-companionwulf auth login --namespace default --tdata /path/to/tdata
```

## Recursive discovery

```text
tdl-companionwulf auth scan ~/Telegram --max-directories 25000
tdl-companionwulf auth scan --all-volumes
```

Recursive scanning is explicit, does not follow symlinks and skips pseudo/system locations where applicable.

## Automatic authorization

```text
tdl-companionwulf auth auto --namespace default --scan-root ~/Telegram
```

The flow checks the current namespace, stored associations, known paths, optional scan roots, native `tdl` desktop detection, and on Windows may use the isolated Telegram Desktop portable bootstrap unless `--no-bootstrap` is supplied.
