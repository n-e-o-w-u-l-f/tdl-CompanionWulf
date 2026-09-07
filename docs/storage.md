# Storage and concurrency

CompanionWulf stores state in `companion.db` beneath the platform state directory.

Windows:

```text
%LOCALAPPDATA%\tdl-CompanionWulf\companion.db
```

Linux/XDG:

```text
$XDG_STATE_HOME/tdl-CompanionWulf/companion.db
```

Without `XDG_STATE_HOME`, `~/.local/state` is used.

SQLite uses WAL mode and a busy timeout. `tdata` directories are protected by OS-level non-blocking lease files. If the implicit default namespace is already bound to a busy `tdata`, CompanionWulf can generate a parallel namespace rather than sharing the session unsafely.
