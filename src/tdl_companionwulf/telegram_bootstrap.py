from __future__ import annotations

import os
import platform
import subprocess
import time
import urllib.request
import uuid
import zipfile
from pathlib import Path, PurePosixPath
from typing import Callable

OFFICIAL_32 = "https://telegram.org/dl/desktop/win_portable"
OFFICIAL_64 = "https://telegram.org/dl/desktop/win64_portable"
MAX_DOWNLOAD_BYTES = 512 * 1024 * 1024
MIN_DOWNLOAD_BYTES = 1024 * 1024


class BootstrapError(RuntimeError):
    pass


def windows_architecture_bits() -> int:
    return 64 if platform.machine().endswith("64") else 32


def official_portable_url(bits: int | None = None) -> str:
    bits = windows_architecture_bits() if bits is None else bits
    if bits == 64:
        return OFFICIAL_64
    if bits == 32:
        return OFFICIAL_32
    raise ValueError("Windows architecture must be 32 or 64 bits")


def download_official_portable(url: str, target: Path) -> Path:
    if url not in {OFFICIAL_32, OFFICIAL_64}:
        raise BootstrapError("Refusing non-official Telegram Desktop URL")
    request = urllib.request.Request(url, headers={"User-Agent": "tdl-CompanionWulf/1.0"})
    total = 0
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as stream:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                raise BootstrapError("Telegram portable download exceeded safety limit")
            stream.write(chunk)
    if total < MIN_DOWNLOAD_BYTES:
        raise BootstrapError("Telegram portable archive is unexpectedly small")
    with target.open("rb") as stream:
        if stream.read(2) != b"PK":
            raise BootstrapError("Telegram portable download is not a ZIP archive")
    return target


def _safe_member_path(root: Path, member: str) -> Path:
    pure = PurePosixPath(member.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts:
        raise BootstrapError(f"Unsafe archive path: {member}")
    target = root.joinpath(*pure.parts)
    try:
        target.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise BootstrapError(f"Unsafe archive path: {member}") from exc
    return target


def validate_portable_zip(path: Path) -> str:
    if not path.is_file() or path.stat().st_size < MIN_DOWNLOAD_BYTES:
        raise BootstrapError("Telegram portable archive is unexpectedly small")
    with path.open("rb") as stream:
        if stream.read(2) != b"PK":
            raise BootstrapError("Telegram portable archive is not ZIP data")
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise BootstrapError(f"Corrupt ZIP member: {bad}")
            telegram_members: list[str] = []
            for info in archive.infolist():
                _safe_member_path(Path("."), info.filename)
                if PurePosixPath(info.filename.replace("\\", "/")).name.casefold() == "telegram.exe":
                    telegram_members.append(info.filename)
    except zipfile.BadZipFile as exc:
        raise BootstrapError("Invalid Telegram portable ZIP archive") from exc
    if not telegram_members:
        raise BootstrapError("Telegram.exe is missing from the official portable archive")
    return telegram_members[0]


def extract_portable_zip(path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    telegram_member = validate_portable_zip(path)
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            target = _safe_member_path(destination, info.filename)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("wb") as output:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
    telegram = _safe_member_path(destination, telegram_member)
    if not telegram.is_file():
        raise BootstrapError("Telegram.exe was not extracted")
    return telegram


def _default_launcher(executable: Path, workdir: Path):
    return subprocess.Popen(
        [str(executable), "-many", "-workdir", str(workdir)],
        cwd=str(executable.parent),
    )


def bootstrap_telegram_desktop(
    state_root: Path,
    *,
    timeout_seconds: float | None = None,
    downloader: Callable[[str, Path], Path] = download_official_portable,
    launcher: Callable[[Path, Path], object] = _default_launcher,
) -> Path:
    if os.name != "nt":
        raise BootstrapError("Telegram Desktop portable bootstrap is Windows-only")
    client_id = f"client_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    client_root = Path(state_root) / client_id
    profile = client_root / "profile"
    archive = client_root / "telegram-portable.zip"
    client_root.mkdir(parents=True, exist_ok=True)
    profile.mkdir(parents=True, exist_ok=True)

    downloader(official_portable_url(), archive)
    executable = extract_portable_zip(archive, client_root)
    launcher(executable, profile)

    deadline = None if timeout_seconds is None else time.monotonic() + timeout_seconds
    tdata = profile / "tdata"
    while True:
        if (tdata / "key_data").is_file():
            return tdata.resolve()
        if deadline is not None and time.monotonic() >= deadline:
            raise BootstrapError("Timed out waiting for Telegram Desktop sign-in")
        time.sleep(1.0)
