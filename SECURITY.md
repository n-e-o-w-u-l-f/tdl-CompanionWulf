# Security policy

## Supported version

Security fixes target the current `main` branch and the latest published release.

## Sensitive data

Never commit Telegram `tdata`, session files, verification codes, passwords, API tokens, private chat exports or user databases.

CompanionWulf invokes `tdl` and, on Windows when explicitly allowed, the official Telegram Desktop portable client for interactive authorization. Credential entry belongs to those applications, not to CompanionWulf.

## Reporting

For a security-sensitive issue, avoid posting secrets or exploitable private details in a public issue. Contact the repository owner through GitHub first and provide a minimal reproducible description without credentials.
