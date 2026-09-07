# Interactive wizard

The wizard recreates the guided Sidecart workflow using a portable CLI.

```text
tdl-companionwulf wizard --dir downloads --media audio,video
```

It performs these stages:

1. authorization check and optional auto-auth
2. chat listing via `tdl chat ls -o json`
3. chat selection such as `1,3-5` or `all`
4. forum topic selection when applicable
5. JSON export per selected chat/topic
6. existing-file collision precheck
7. selected media download

Useful flags include `--language`, `--comparison`, `--max-filename-length`, `--no-auto-auth`, `--no-bootstrap`, `--no-protect-existing` and `--dry-run`.
