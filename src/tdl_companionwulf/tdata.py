from __future__ import annotations

import os
import string
from pathlib import Path
from typing import Iterable

from .tdata_0_6 import *
from .tdata_0_6 import TdataCandidate, candidate_from_path

_UNIX_SKIP = {"/proc", "/sys", "/dev", "/run"}
_WINDOWS_SKIP = {"$recycle.bin", "system volume information"}


def scan_volume_roots() -> list[Path]:
    if os.name == "nt":
        result: list[Path] = []
        for letter in string.ascii_uppercase:
            root = Path(f"{letter}:/")
            try:
                if root.exists():
                    result.append(root)
            except OSError:
                continue
        return result
    return [Path("/")]


def _scan_key(path: Path) -> str:
    try:
        value = str(path.resolve(strict=False))
    except OSError:
        value = str(path.absolute())
    return os.path.normcase(value)


def _skip_scan_directory(path: Path) -> bool:
    value = str(path)
    if os.name != "nt" and value in _UNIX_SKIP:
        return True
    if path.name.casefold() in _WINDOWS_SKIP:
        return True
    try:
        return path.is_symlink()
    except OSError:
        return True


def find_system_tdata(
    roots: Iterable[Path | str],
    *,
    exclude: Iterable[Path | str] = (),
    max_directories: int | None = None,
) -> list[TdataCandidate]:
    excluded = {_scan_key(Path(path)) for path in exclude}
    seen_dirs: set[str] = set()
    candidates: dict[str, TdataCandidate] = {}
    stack = [Path(root).expanduser() for root in roots]
    visited = 0

    while stack:
        directory = stack.pop()
        key = _scan_key(directory)
        if key in seen_dirs or key in excluded or _skip_scan_directory(directory):
            continue
        seen_dirs.add(key)
        visited += 1
        if max_directories is not None and visited > max_directories:
            break

        if directory.name.casefold() == "tdata":
            candidate = candidate_from_path(directory, "system")
            if candidate is not None:
                candidate_key = _scan_key(candidate.path)
                if candidate_key not in excluded:
                    candidates[candidate_key] = candidate
            continue

        try:
            with os.scandir(directory) as entries:
                children: list[Path] = []
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            child = Path(entry.path)
                            if not _skip_scan_directory(child):
                                children.append(child)
                    except OSError:
                        continue
                stack.extend(reversed(children))
        except (OSError, PermissionError):
            continue

    result = list(candidates.values())
    result.sort(key=lambda item: (not item.has_key_data, -item.modified, str(item.path)))
    return result
