# Troubleshooting

## tdl not found

Run `tdl-companionwulf doctor`. Install `tdl`, add it to `PATH`, or use `--tdl-path`.

## Namespace is not authorized

Run `auth candidates`, then `auth auto`. Use `auth scan <root>` only when known paths are insufficient.

## tdata already in use

Another CompanionWulf process holds the exclusive lease. Use another namespace/session or let the process finish; do not delete active lock files to bypass the lease.

## Existing file was renamed

The export supplied metadata that did not match the existing file under the selected comparison policy. CompanionWulf preserves the old file as `name (n).ext` before downloading the replacement.

## GitHub Actions did not start

Distinguish workflow/code errors from account-level GitHub scheduling or billing restrictions by inspecting the workflow-run annotation.
