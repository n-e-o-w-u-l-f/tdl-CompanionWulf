from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TdataCandidate:
    path: Path
    source: str
    has_key_data: bool
    modified: float


def stable_hex_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_tdata_path(path: Path | str) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def candidate_from_path(path: Path | str, source: str) -> TdataCandidate | None:
    candidate = canonical_tdata_path(path)
    try:
        if not candidate.is_dir() or candidate.name.lower() != "tdata":
            return None
        modified = candidate.stat().st_mtime
    except OSError:
        return None
    return TdataCandidate(
        path=candidate,
        source=source,
        has_key_data=(candidate / "key_data").is_file(),
        modified=modified,
    )


def _append_if_value(items: list[Path], base: str | Path | None, *parts: str) -> None:
    if base is None or str(base).strip() == "":
        return
    items.append(Path(base).expanduser().joinpath(*parts))


def known_tdata_paths(*, home: Path | None = None, env: dict[str, str] | None = None) -> list[Path]:
    home = (home or Path.home()).expanduser()
    env = os.environ if env is None else env
    paths: list[Path] = []
    _append_if_value(paths, env.get("APPDATA"), "Telegram Desktop", "tdata")
    _append_if_value(paths, env.get("LOCALAPPDATA"), "Telegram Desktop", "tdata")
    _append_if_value(paths, home, "Telegram Desktop", "tdata")
    _append_if_value(paths, home, "tdata")
    _append_if_value(paths, home, "iGram Desktop", "tdata")
    _append_if_value(paths, home, "Desktop", "tdata")
    _append_if_value(paths, home, "Desktop", "iGram Desktop", "tdata")
    _append_if_value(paths, home, "Downloads", "iGram Desktop", "tdata")
    _append_if_value(paths, home, "Documents", "iGram Desktop", "tdata")
    _append_if_value(paths, home, "Desktop", "Telegram Desktop", "tdata")
    _append_if_value(paths, home, "Downloads", "Telegram Desktop", "tdata")
    _append_if_value(paths, home, "Documents", "Telegram Desktop", "tdata")
    _append_if_value(paths, home, ".local", "share", "TelegramDesktop", "tdata")
    _append_if_value(paths, home, ".var", "app", "org.telegram.desktop", "data", "TelegramDesktop", "tdata")
    _append_if_value(paths, home, "Library", "Application Support", "Telegram Desktop", "tdata")
    return paths


def discover_known_tdata(
    *,
    home: Path | None = None,
    env: dict[str, str] | None = None,
    extra_paths: Iterable[Path | str] = (),
) -> list[TdataCandidate]:
    paths = known_tdata_paths(home=home, env=env)
    paths.extend(Path(path) for path in extra_paths)
    seen: set[str] = set()
    result: list[TdataCandidate] = []
    for path in paths:
        candidate = candidate_from_path(path, "known")
        if candidate is None:
            continue
        key = os.path.normcase(str(candidate.path))
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    result.sort(key=lambda item: (not item.has_key_data, -item.modified, str(item.path)))
    return result


class TdataLease:
    def __init__(self, tdata_path: Path | str, lock_root: Path | str, *, namespace: str):
        self.tdata_path = canonical_tdata_path(tdata_path)
        self.lock_root = Path(lock_root)
        self.namespace = namespace
        self._stream = None
        key = os.path.normcase(str(self.tdata_path))
        self.lock_path = self.lock_root / f"{stable_hex_hash(key)}.lock"

    @property
    def acquired(self) -> bool:
        return self._stream is not None

    def acquire(self) -> bool:
        if self._stream is not None:
            return True
        self.lock_root.mkdir(parents=True, exist_ok=True)
        stream = self.lock_path.open("a+b")
        try:
            self._lock_stream(stream)
        except OSError:
            stream.close()
            return False
        metadata = {
            "pid": os.getpid(),
            "namespace": self.namespace,
            "tdata": str(self.tdata_path),
            "startedUtc": datetime.now(timezone.utc).isoformat(),
        }
        if os.name == "nt":
            stream.seek(1)
            stream.truncate(1)
        else:
            stream.seek(0)
            stream.truncate(0)
        stream.write(json.dumps(metadata, separators=(",", ":")).encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
        self._stream = stream
        return True

    def release(self) -> None:
        stream = self._stream
        if stream is None:
            return
        self._stream = None
        try:
            self._unlock_stream(stream)
        finally:
            stream.close()

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"tdata is already leased: {self.tdata_path}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        return False

    @staticmethod
    def _lock_stream(stream) -> None:
        if os.name == "nt":
            import msvcrt
            stream.seek(0, os.SEEK_END)
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    @staticmethod
    def _unlock_stream(stream) -> None:
        if os.name == "nt":
            import msvcrt
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        else:
            import fcntl
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
