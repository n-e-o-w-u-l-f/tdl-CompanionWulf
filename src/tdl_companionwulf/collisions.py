from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ExportMedia:
    name: str
    size: int | None
    sha256: str | None = None


@dataclass(frozen=True)
class CollisionSummary:
    checked: int = 0
    same: int = 0
    renamed: int = 0
    unknown: int = 0


_RESERVED = {"CON", "PRN", "AUX", "NUL"}
_RESERVED.update(f"COM{i}" for i in range(1, 10))
_RESERVED.update(f"LPT{i}" for i in range(1, 10))
_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_filename(name: str, *, max_length: int = 180) -> str:
    value = _INVALID.sub("_", str(name or "")).strip().rstrip(". ")
    if not value:
        value = "unnamed"
    path = Path(value)
    suffix = path.suffix
    stem = value[: -len(suffix)] if suffix else value
    if stem.upper() in _RESERVED:
        stem = "_" + stem
        value = stem + suffix
    if len(value) <= max_length:
        return value
    available = max(1, max_length - len(suffix))
    return stem[:available] + suffix


def unique_renamed_path(path: Path | str) -> Path:
    target = Path(path)
    stem, suffix = target.stem, target.suffix
    counter = 1
    while True:
        candidate = target.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _first(mapping: dict[str, Any], names: Iterable[str]) -> Any:
    for name in names:
        value = mapping.get(name)
        if value not in (None, ""):
            return value
    return None


def _size(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _sha256(value: Any) -> str | None:
    if value in (None, ""):
        return None
    digest = str(value).strip().lower()
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        return None
    return digest


def file_sha256(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_export_media(message: Any) -> ExportMedia | None:
    if not isinstance(message, dict):
        return None
    nested = message.get("Media") or message.get("media")
    nested = nested if isinstance(nested, dict) else {}
    name = _first(message, ("file", "file_name", "fileName"))
    if name is None:
        name = _first(nested, ("Name", "name", "FileName", "file_name"))
    if name is None:
        return None
    size = _first(message, ("file_size", "fileSize", "size", "Size"))
    if size is None:
        size = _first(nested, ("Size", "size", "FileSize", "file_size"))
    remote_hash = _first(message, ("sha256", "SHA256", "file_sha256", "fileSha256"))
    if remote_hash is None:
        remote_hash = _first(nested, ("sha256", "SHA256", "FileSHA256", "file_sha256"))
    return ExportMedia(safe_filename(str(name)), _size(size), _sha256(remote_hash))


def _messages(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("messages", "data", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def read_export_media(json_path: Path | str) -> list[ExportMedia]:
    payload = json.loads(Path(json_path).read_text(encoding="utf-8-sig"))
    result: list[ExportMedia] = []
    for message in _messages(payload):
        media = extract_export_media(message)
        if media is not None:
            result.append(media)
    return result


def prepare_existing_files(json_path: Path | str, directory: Path | str) -> CollisionSummary:
    root = Path(directory)
    checked = same = renamed = unknown = 0
    for media in read_export_media(json_path):
        target = root / media.name
        if not target.is_file():
            continue
        checked += 1
        try:
            if media.sha256 is not None:
                matches = file_sha256(target) == media.sha256
            elif media.size is not None:
                matches = target.stat().st_size == media.size
            else:
                unknown += 1
                continue
        except OSError:
            unknown += 1
            continue
        if matches:
            same += 1
            continue
        replacement = unique_renamed_path(target)
        target.rename(replacement)
        renamed += 1
    return CollisionSummary(
        checked=checked,
        same=same,
        renamed=renamed,
        unknown=unknown,
    )
