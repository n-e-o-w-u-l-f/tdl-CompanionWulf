# Queue and downloads

Add work with:

```text
tdl-companionwulf add https://t.me/example/1
tdl-companionwulf queue
tdl-companionwulf status
```

Run one waiting job:

```text
tdl-companionwulf run
```

Preview the next command without changing the queue:

```text
tdl-companionwulf run --dry-run
```

A dry-run does not start `tdl`, increment attempts, change status or add completion/failure events.

Failed jobs can be returned to the waiting state with `requeue <JOB_ID>`.
