from __future__ import annotations

import subprocess as _subprocess
import sys
from typing import Any


class Utf8SubprocessProxy:
    """Delegate to subprocess while forcing UTF-8 for captured text streams.

    tdl emits UTF-8 JSON. On Windows, subprocess text mode otherwise inherits
    the active ANSI code page (commonly cp1252), which can crash reader threads
    before stdout reaches the JSON parser.
    """

    def __getattr__(self, name: str) -> Any:
        return getattr(_subprocess, name)

    def run(self, *popenargs: Any, **kwargs: Any):
        if (
            (kwargs.get("text") or kwargs.get("universal_newlines"))
            and kwargs.get("encoding") is None
        ):
            kwargs["encoding"] = "utf-8"
            kwargs.setdefault("errors", "replace")
        return _subprocess.run(*popenargs, **kwargs)


from . import cli as _cli  # noqa: E402
from . import cli_0_6 as _legacy  # noqa: E402

_PROXY = Utf8SubprocessProxy()
_cli.subprocess = _PROXY
_legacy.subprocess = _PROXY


def main() -> int:
    if sys.argv[1:] == ["--version"]:
        print("tdl-CompanionWulf 1.0.1")
        return 0
    return _cli.main()
