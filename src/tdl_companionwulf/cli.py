from __future__ import annotations

import argparse
import atexit
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .i18n import detect_language
from .media import media_extensions
from .tdl import (
    TdlOptions,
    build_chat_export_command,
    build_chat_list_command,
    build_download_command,
    build_login_command,
)
from .tdata import TdataLease, discover_known_tdata, canonical_tdata_path
from .wizard import build_export_jobs, parse_chats_json, parse_selection, safe_component

APP_NAME = "tdl-CompanionWulf"
_ACTIVE_TDATA_LEASES: list[TdataLease] = []


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()

TEXT = {
    "de": {
        "tdl_missing": "tdl wurde nicht gefunden. Installiere tdl zuerst oder stelle sicher, dass tdl.exe im PATH liegt.",
        "added": "Zur Queue hinzugefügt",
        "duplicate": "Bereits in der Queue",
        "empty": "Queue ist leer.",
        "running": "Starte Job",
        "completed": "Job abgeschlossen",
        "failed": "Job fehlgeschlagen",
        "status": "Status",
    },
    "en": {
        "tdl_missing": "tdl was not found. Install tdl first or ensure tdl.exe is available in PATH.",
        "added": "Added to queue",
        "duplicate": "Already queued",
        "empty": "Queue is empty.",
        "running": "Starting job",
        "completed": "Job completed",
        "failed": "Job failed",
        "status": "Status",
    },
}


def language() -> str:
    return detect_language(get_setting("language") or "auto")


def tr(key: str) -> str:
    lang = language()
    return TEXT.get(lang, TEXT["en"]).get(key, key)


def data_dir() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / APP_NAME
    root = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return root / APP_NAME


def db_path() -> Path:
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True)
    return root / "companion.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(), factory=ClosingConnection)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'waiting',
            priority INTEGER NOT NULL DEFAULT 50,
            attempts INTEGER NOT NULL DEFAULT 0,
            exit_code INTEGER,
            created_at TEXT NOT NULL,
            started_at TEXT,
            finished_at TEXT,
            last_error TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tdata_associations (
            namespace TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def set_setting(key: str, value: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO settings(key,value,updated_at) VALUES(?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (key, value, now()),
        )
        conn.commit()


def get_setting(key: str) -> str | None:
    with connect() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return None if row is None else str(row["value"])


def list_settings() -> list[tuple[str, str]]:
    with connect() as conn:
        rows = conn.execute("SELECT key,value FROM settings ORDER BY key").fetchall()
    return [(str(row["key"]), str(row["value"])) for row in rows]


def unset_setting(key: str) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM settings WHERE key=?", (key,))
        conn.commit()
    return cur.rowcount > 0


def set_namespace_tdata(namespace: str, path: Path | str) -> None:
    canonical = canonical_tdata_path(path)
    with connect() as conn:
        conn.execute(
            "INSERT INTO tdata_associations(namespace,path,updated_at) VALUES(?,?,?) "
            "ON CONFLICT(namespace) DO UPDATE SET path=excluded.path, updated_at=excluded.updated_at",
            (namespace, str(canonical), now()),
        )
        conn.commit()


def get_namespace_tdata(namespace: str) -> Path | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT path FROM tdata_associations WHERE namespace=?", (namespace,)
        ).fetchone()
    if row is None:
        return None
    path = canonical_tdata_path(str(row["path"]))
    return path if path.is_dir() else None


def unset_namespace_tdata(namespace: str) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM tdata_associations WHERE namespace=?", (namespace,))
        conn.commit()
    return cur.rowcount > 0


def release_active_tdata_leases() -> None:
    while _ACTIVE_TDATA_LEASES:
        _ACTIVE_TDATA_LEASES.pop().release()


def hold_namespace_tdata_lease(namespace: str) -> bool:
    associated = get_namespace_tdata(namespace)
    if associated is None:
        return True
    target = os.path.normcase(str(associated))
    for lease in _ACTIVE_TDATA_LEASES:
        if lease.acquired and os.path.normcase(str(lease.tdata_path)) == target:
            return True
    lease = TdataLease(associated, data_dir() / "tdata-locks", namespace=namespace)
    if not lease.acquire():
        return False
    _ACTIVE_TDATA_LEASES.append(lease)
    return True


atexit.register(release_active_tdata_leases)


def event(conn: sqlite3.Connection, job_id: int | None, message: str, level: str = "INFO") -> None:
    conn.execute(
        "INSERT INTO events(job_id,timestamp,level,message) VALUES(?,?,?,?)",
        (job_id, now(), level, message),
    )
    conn.commit()


def find_tdl() -> str | None:
    found = shutil.which("tdl") or shutil.which("tdl.exe")
    if found:
        return found
    if os.name == "nt":
        candidate = Path("C:/PS/binaries/tdl.exe")
        if candidate.is_file():
            return str(candidate)
    return None


def add_url(url: str, priority: int = 50) -> int:
    url = url.strip()
    if not url:
        return 0
    with connect() as conn:
        existing = conn.execute("SELECT id FROM jobs WHERE url=?", (url,)).fetchone()
        if existing:
            print(f"{tr('duplicate')}: #{existing['id']} {url}")
            return int(existing["id"])
        cur = conn.execute(
            "INSERT INTO jobs(url,status,priority,created_at) VALUES(?, 'waiting', ?, ?)",
            (url, priority, now()),
        )
        job_id = int(cur.lastrowid)
        conn.commit()
        event(conn, job_id, f"URL added: {url}")
        print(f"{tr('added')}: #{job_id} {url}")
        return job_id


def queue_rows() -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(
            "SELECT id,status,priority,attempts,url FROM jobs ORDER BY status='waiting' DESC, priority DESC, id ASC"
        ).fetchall()


def show_queue() -> None:
    rows = queue_rows()
    if not rows:
        print(tr("empty"))
        return
    print(f"{'ID':<6}{'STATUS':<14}{'PRI':<6}{'TRY':<6}URL")
    for row in rows:
        print(f"{row['id']:<6}{row['status']:<14}{row['priority']:<6}{row['attempts']:<6}{row['url']}")


def show_status() -> None:
    with connect() as conn:
        rows = conn.execute("SELECT status, COUNT(*) AS count FROM jobs GROUP BY status ORDER BY status").fetchall()
    print(tr("status"))
    if not rows:
        print(tr("empty"))
        return
    for row in rows:
        print(f"{row['status']:<14}{row['count']}")


def next_job(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM jobs WHERE status='waiting' ORDER BY priority DESC, id ASC LIMIT 1"
    ).fetchone()


def run_next(
    download_dir: Path,
    options: TdlOptions,
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    takeout: bool = False,
    continue_download: bool = False,
    restart_download: bool = False,
    rewrite_ext: bool = False,
    desc: bool = False,
    group: bool = False,
    skip_same: bool = True,
    template: str = "{{ filenamify .FileName 180 }}",
    extra_args: list[str] | None = None,
) -> int:
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2
    download_dir.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        job = next_job(conn)
        if job is None:
            print(tr("empty"))
            return 0
        conn.execute(
            "UPDATE jobs SET status='running', attempts=attempts+1, started_at=?, last_error=NULL WHERE id=?",
            (now(), job["id"]),
        )
        conn.commit()
        event(conn, int(job["id"]), "tdl started")
        print(f"{tr('running')} #{job['id']}: {job['url']}")
        command = build_download_command(
            tdl,
            options,
            urls=[str(job["url"])],
            directory=download_dir,
            include=include,
            exclude=exclude,
            takeout=takeout,
            continue_download=continue_download,
            restart_download=restart_download,
            rewrite_ext=rewrite_ext,
            desc=desc,
            group=group,
            skip_same=skip_same,
            template=template,
            extra_args=extra_args,
        )
        result = subprocess.run(command)
        if result.returncode == 0:
            conn.execute(
                "UPDATE jobs SET status='completed', exit_code=0, finished_at=? WHERE id=?",
                (now(), job["id"]),
            )
            conn.commit()
            event(conn, int(job["id"]), "tdl completed")
            print(f"{tr('completed')} #{job['id']}")
            return 0
        error = f"tdl exit code {result.returncode}"
        conn.execute(
            "UPDATE jobs SET status='failed', exit_code=?, finished_at=?, last_error=? WHERE id=?",
            (result.returncode, now(), error, job["id"]),
        )
        conn.commit()
        event(conn, int(job["id"]), error, "ERROR")
        print(f"{tr('failed')} #{job['id']}: {error}", file=sys.stderr)
        return int(result.returncode or 1)


def show_chats(options: TdlOptions, *, json_output: bool = False, filter_expression: str = "") -> int:
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2
    command = build_chat_list_command(
        tdl, options, json_output=json_output, filter_expression=filter_expression
    )
    return int(subprocess.run(command).returncode)


def export_chat(
    options: TdlOptions,
    *,
    chat: str = "",
    topic: int | None = None,
    reply: int | None = None,
    export_type: str = "time",
    inputs: list[int] | None = None,
    output: Path = Path("tdl-export.json"),
    filter_expression: str = "",
    all_messages: bool = False,
    with_content: bool = False,
    raw: bool = False,
) -> int:
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    command = build_chat_export_command(
        tdl,
        options,
        chat=chat,
        topic=topic,
        reply=reply,
        export_type=export_type,
        inputs=inputs,
        output=output,
        filter_expression=filter_expression,
        all_messages=all_messages,
        with_content=with_content,
        raw=raw,
    )
    return int(subprocess.run(command).returncode)


def _split_csv(value: str | None) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def _split_int_csv(value: str | None) -> list[int]:
    return [int(part) for part in _split_csv(value)]


def _setting_int(key: str, default: int) -> int:
    value = get_setting(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def options_from_args(args: argparse.Namespace) -> TdlOptions:
    return TdlOptions(
        namespace=getattr(args, "namespace", None) or get_setting("namespace") or "default",
        limit=getattr(args, "limit", None) or _setting_int("limit", 2),
        threads=getattr(args, "threads", None) or _setting_int("threads", 4),
        delay=getattr(args, "delay", None) if getattr(args, "delay", None) is not None else _setting_int("delay", 0),
        pool=getattr(args, "pool", None) if getattr(args, "pool", None) is not None else _setting_int("pool", 8),
        proxy=getattr(args, "proxy", None) or get_setting("proxy") or "",
        ntp=getattr(args, "ntp", None) or get_setting("ntp") or "",
        reconnect_timeout=getattr(args, "reconnect_timeout", None) or get_setting("reconnect_timeout") or "",
        storage=getattr(args, "storage", None) or get_setting("storage") or "",
        debug=bool(getattr(args, "debug", False)),
        disable_progress_ps=bool(getattr(args, "disable_progress_ps", False)),
    )


def run_wizard(args: argparse.Namespace) -> int:
    if args.continue_download and args.restart_download:
        print("--continue and --restart are mutually exclusive", file=sys.stderr)
        return 2
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2

    options = options_from_args(args)
    if not args.no_auto_auth:
        try:
            authorized, _ = probe_authorization(tdl, options)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if not authorized:
            code = auth_auto(options)
            if code != 0:
                return code

    if not hold_namespace_tdata_lease(options.namespace):
        associated = get_namespace_tdata(options.namespace)
        print(f"tdata is already in use for namespace '{options.namespace}': {associated}", file=sys.stderr)
        return 3

    list_result = subprocess.run(
        build_chat_list_command(
            tdl, options, json_output=True, filter_expression=args.chat_filter
        ),
        capture_output=True,
        text=True,
    )
    if list_result.returncode != 0:
        print(list_result.stderr or list_result.stdout, file=sys.stderr)
        return int(list_result.returncode or 1)
    try:
        chats = sorted(parse_chats_json(list_result.stdout), key=lambda chat: chat.name.casefold())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not chats:
        print("No Telegram chats found.", file=sys.stderr)
        return 1

    print("\nChats")
    for index, chat in enumerate(chats, 1):
        topic_text = f" ({len(chat.topics)} Topics)" if chat.topics else ""
        print(f"{index:>3}. {chat.name} [{chat.type}]{topic_text} ID={chat.id}")
    try:
        selected_chats = parse_selection(
            input("Select chats [1,3-5 or all]: "), len(chats)
        )
    except (EOFError, ValueError) as exc:
        print(f"Invalid chat selection: {exc}", file=sys.stderr)
        return 1
    if not selected_chats:
        print("No chats selected.", file=sys.stderr)
        return 1

    topic_selections: dict[int, list[int]] = {}
    try:
        for chat_index in selected_chats:
            chat = chats[chat_index]
            if not chat.topics:
                continue
            print(f"\nTopics: {chat.name}")
            for index, topic in enumerate(chat.topics, 1):
                print(f"{index:>3}. {topic.title} ID={topic.id}")
            topic_selections[chat.id] = parse_selection(
                input("Select topics [1,3-5 or all]: "), len(chat.topics)
            )
        jobs = build_export_jobs(
            chats,
            selected_chat_indices=selected_chats,
            topic_selections=topic_selections,
        )
    except (EOFError, ValueError) as exc:
        print(f"Invalid topic selection: {exc}", file=sys.stderr)
        return 1

    media_names = _split_csv(args.media)
    if not media_names:
        try:
            media_names = _split_csv(
                input("Media [archive,audio,images,video] (audio): ").strip() or "audio"
            )
        except EOFError:
            media_names = ["audio"]
    try:
        extensions = media_extensions(media_names)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_root = args.dir or Path(
        get_setting("download_dir") or (Path.cwd() / "downloads")
    )
    output_root.mkdir(parents=True, exist_ok=True)
    successes = 0
    errors = 0

    for number, job in enumerate(jobs, 1):
        destination = output_root / safe_component(job.chat_name)
        if job.topic_id is not None:
            destination /= safe_component(job.topic_name)
        destination.mkdir(parents=True, exist_ok=True)
        suffix = str(job.topic_id) if job.topic_id is not None else "chat"
        export_path = destination / f"{job.chat_id}_{suffix}_tdl-export.json"
        label = job.chat_name + (f" / {job.topic_name}" if job.topic_id is not None else "")
        print(f"\n[{number}/{len(jobs)}] Export: {label}")
        export_result = subprocess.run(
            build_chat_export_command(
                tdl,
                options,
                chat=str(job.chat_id),
                topic=job.topic_id,
                output=export_path,
            )
        )
        if export_result.returncode != 0 or not export_path.is_file() or export_path.stat().st_size == 0:
            print(f"Export failed: {label}", file=sys.stderr)
            errors += 1
            continue

        print(f"[{number}/{len(jobs)}] Download: {label}")
        download_result = subprocess.run(
            build_download_command(
                tdl,
                options,
                files=[export_path],
                directory=destination,
                include=extensions,
                takeout=args.takeout,
                continue_download=args.continue_download,
                restart_download=args.restart_download,
                rewrite_ext=args.rewrite_ext,
                desc=args.desc,
                group=args.group,
                skip_same=not args.no_skip_same,
                template=args.template or "{{ filenamify .FileName 180 }}",
                extra_args=args.extra_arg,
            )
        )
        if download_result.returncode == 0:
            successes += 1
        else:
            errors += 1

    print(f"\nWizard complete: {successes} successful, {errors} failed, {len(jobs)} total")
    return 0 if errors == 0 else 1


def probe_authorization(tdl: str, options: TdlOptions) -> tuple[bool, str]:
    result = subprocess.run(
        build_chat_list_command(tdl, options, json_output=True),
        capture_output=True,
        text=True,
    )
    text = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode == 0:
        return True, text
    lowered = text.casefold()
    markers = ("not authorized", "not authenticated", "nicht authentifiziert")
    if any(marker in lowered for marker in markers):
        return False, text
    raise RuntimeError(text or f"tdl exited with code {result.returncode}")


def login_tdata(tdl: str, options: TdlOptions, tdata_path: Path) -> int:
    candidate = canonical_tdata_path(tdata_path)
    lease = TdataLease(candidate, data_dir() / "tdata-locks", namespace=options.namespace)
    if not lease.acquire():
        print(f"tdata is already in use: {candidate}", file=sys.stderr)
        return 3
    try:
        result = subprocess.run(build_login_command(tdl, options, candidate))
        if result.returncode != 0:
            return int(result.returncode or 1)
        authorized, _ = probe_authorization(tdl, options)
        if not authorized:
            return 1
        set_namespace_tdata(options.namespace, candidate)
        return 0
    finally:
        lease.release()


def auth_candidates(namespace: str = "default") -> int:
    associated = get_namespace_tdata(namespace)
    extras = [associated] if associated is not None else []
    candidates = discover_known_tdata(extra_paths=extras)
    if not candidates:
        print("No tdata candidates found.")
        return 1
    for candidate in candidates:
        marker = "key_data" if candidate.has_key_data else "no-key_data"
        association = " associated" if associated == candidate.path else ""
        print(f"{candidate.path} [{marker}{association}]")
    return 0


def auth_status(options: TdlOptions) -> int:
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2
    try:
        authorized, text = probe_authorization(tdl, options)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("authorized" if authorized else "not authorized")
    if not authorized and text:
        print(text, file=sys.stderr)
    return 0 if authorized else 1


def auth_auto(options: TdlOptions) -> int:
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2
    try:
        authorized, _ = probe_authorization(tdl, options)
        if authorized:
            print(f"Namespace '{options.namespace}' is already authorized.")
            return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    associated = get_namespace_tdata(options.namespace)
    extras = [associated] if associated is not None else []
    candidates = discover_known_tdata(extra_paths=extras)
    saw_locked_candidate = False
    for candidate in candidates:
        if not candidate.has_key_data:
            continue
        print(f"Trying tdata: {candidate.path}")
        code = login_tdata(tdl, options, candidate.path)
        if code == 0:
            print(f"Authorized namespace '{options.namespace}' with {candidate.path}")
            return 0
        if code == 3:
            saw_locked_candidate = True
            continue

    if saw_locked_candidate:
        print("A matching tdata candidate is already leased by another CompanionWulf process.", file=sys.stderr)
        return 3

    print("No reusable tdata candidate succeeded; trying tdl native desktop detection.")
    result = subprocess.run(build_login_command(tdl, options))
    if result.returncode != 0:
        return int(result.returncode or 1)
    try:
        authorized, _ = probe_authorization(tdl, options)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0 if authorized else 1


def requeue(job_id: int) -> int:
    with connect() as conn:
        cur = conn.execute(
            "UPDATE jobs SET status='waiting', exit_code=NULL, finished_at=NULL, last_error=NULL WHERE id=?",
            (job_id,),
        )
        conn.commit()
        if cur.rowcount == 0:
            print(f"Job #{job_id} not found", file=sys.stderr)
            return 1
        event(conn, job_id, "job requeued")
    return 0


def _add_tdl_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-n", "--namespace")
    parser.add_argument("-l", "--limit", type=int)
    parser.add_argument("-t", "--threads", type=int)
    parser.add_argument("--delay", type=int)
    parser.add_argument("--pool", type=int)
    parser.add_argument("--proxy")
    parser.add_argument("--ntp")
    parser.add_argument("--reconnect-timeout", dest="reconnect_timeout")
    parser.add_argument("--storage")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--disable-progress-ps", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tdl-companionwulf")
    parser.add_argument("--version", action="version", version="tdl-CompanionWulf 0.5.0")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="Add Telegram URLs to the SQLite queue")
    p.add_argument("urls", nargs="+")
    p.add_argument("--priority", "-p", type=int, default=50)
    sub.add_parser("queue", help="Show queued jobs")
    sub.add_parser("status", help="Show queue status summary")

    p = sub.add_parser("run", help="Run the next queued job with tdl")
    p.add_argument("--dir", type=Path)
    _add_tdl_options(p)
    p.add_argument("-i", "--include")
    p.add_argument("-e", "--exclude")
    p.add_argument("--media", help="Comma-separated profiles: archive,audio,images,video")
    p.add_argument("--takeout", action="store_true")
    p.add_argument("--continue", dest="continue_download", action="store_true")
    p.add_argument("--restart", dest="restart_download", action="store_true")
    p.add_argument("--rewrite-ext", action="store_true")
    p.add_argument("--desc", action="store_true")
    p.add_argument("--group", action="store_true")
    p.add_argument("--template")
    p.add_argument("--no-skip-same", action="store_true")
    p.add_argument("--extra-arg", action="append", default=[])

    p = sub.add_parser("chats", help="List Telegram chats through tdl")
    _add_tdl_options(p)
    p.add_argument("--json", action="store_true")
    p.add_argument("-f", "--filter", default="")

    p = sub.add_parser("export", help="Export messages from a chat or topic to JSON")
    _add_tdl_options(p)
    p.add_argument("-c", "--chat", default="")
    p.add_argument("--topic", type=int)
    p.add_argument("--reply", type=int)
    p.add_argument("-T", "--type", dest="export_type", choices=["time", "id", "last"], default="time")
    p.add_argument("-i", "--input", default="")
    p.add_argument("-o", "--output", type=Path, default=Path("tdl-export.json"))
    p.add_argument("-f", "--filter", default="")
    p.add_argument("--all", dest="all_messages", action="store_true")
    p.add_argument("--with-content", action="store_true")
    p.add_argument("--raw", action="store_true")

    p = sub.add_parser("wizard", help="Interactive chat/topic export and download workflow")
    p.add_argument("--dir", type=Path)
    _add_tdl_options(p)
    p.add_argument("--media", help="Comma-separated profiles: archive,audio,images,video")
    p.add_argument("--chat-filter", default="")
    p.add_argument("--no-auto-auth", action="store_true")
    p.add_argument("--takeout", action="store_true")
    p.add_argument("--continue", dest="continue_download", action="store_true")
    p.add_argument("--restart", dest="restart_download", action="store_true")
    p.add_argument("--rewrite-ext", action="store_true")
    p.add_argument("--desc", action="store_true")
    p.add_argument("--group", action="store_true")
    p.add_argument("--template")
    p.add_argument("--no-skip-same", action="store_true")
    p.add_argument("--extra-arg", action="append", default=[])

    p = sub.add_parser("auth", help="Inspect or import Telegram Desktop authorization")
    auth_sub = p.add_subparsers(dest="auth_command", required=True)
    a = auth_sub.add_parser("status", help="Check whether the namespace is authorized")
    _add_tdl_options(a)
    a = auth_sub.add_parser("candidates", help="List known Telegram Desktop tdata candidates")
    a.add_argument("-n", "--namespace", default="default")
    a = auth_sub.add_parser("login", help="Import one explicit Telegram Desktop tdata directory")
    _add_tdl_options(a)
    a.add_argument("--tdata", type=Path, required=True)
    a = auth_sub.add_parser("auto", help="Try associated and known tdata candidates, then tdl native detection")
    _add_tdl_options(a)

    p = sub.add_parser("requeue", help="Requeue one job")
    p.add_argument("job_id", type=int)

    p = sub.add_parser("config", help="Persist CompanionWulf defaults in SQLite")
    config_sub = p.add_subparsers(dest="config_command", required=True)
    config_sub.add_parser("list")
    c = config_sub.add_parser("get")
    c.add_argument("key")
    c = config_sub.add_parser("set")
    c.add_argument("key")
    c.add_argument("value")
    c = config_sub.add_parser("unset")
    c.add_argument("key")

    sub.add_parser("doctor", help="Check runtime and database paths")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "add":
        for url in args.urls:
            add_url(url, args.priority)
        return 0
    if args.command == "queue":
        show_queue()
        return 0
    if args.command == "status":
        show_status()
        return 0
    if args.command == "run":
        if args.continue_download and args.restart_download:
            print("--continue and --restart are mutually exclusive", file=sys.stderr)
            return 2
        options = options_from_args(args)
        directory = args.dir or Path(get_setting("download_dir") or (Path.cwd() / "downloads"))
        include = _split_csv(args.include)
        if args.media:
            include = list(dict.fromkeys(include + media_extensions(_split_csv(args.media))))
        return run_next(
            directory,
            options,
            include=include,
            exclude=_split_csv(args.exclude),
            takeout=args.takeout,
            continue_download=args.continue_download,
            restart_download=args.restart_download,
            rewrite_ext=args.rewrite_ext,
            desc=args.desc,
            group=args.group,
            skip_same=not args.no_skip_same,
            template=args.template or "{{ filenamify .FileName 180 }}",
            extra_args=args.extra_arg,
        )
    if args.command == "chats":
        return show_chats(options_from_args(args), json_output=args.json, filter_expression=args.filter)
    if args.command == "export":
        return export_chat(
            options_from_args(args),
            chat=args.chat,
            topic=args.topic,
            reply=args.reply,
            export_type=args.export_type,
            inputs=_split_int_csv(args.input),
            output=args.output,
            filter_expression=args.filter,
            all_messages=args.all_messages,
            with_content=args.with_content,
            raw=args.raw,
        )
    if args.command == "wizard":
        return run_wizard(args)
    if args.command == "auth":
        if args.auth_command == "status":
            return auth_status(options_from_args(args))
        if args.auth_command == "candidates":
            return auth_candidates(args.namespace)
        if args.auth_command == "login":
            tdl = find_tdl()
            if not tdl:
                print(tr("tdl_missing"), file=sys.stderr)
                return 2
            return login_tdata(tdl, options_from_args(args), args.tdata)
        if args.auth_command == "auto":
            return auth_auto(options_from_args(args))
    if args.command == "requeue":
        return requeue(args.job_id)
    if args.command == "config":
        if args.config_command == "list":
            for key, value in list_settings():
                print(f"{key}={value}")
            return 0
        if args.config_command == "get":
            value = get_setting(args.key)
            if value is None:
                return 1
            print(value)
            return 0
        if args.config_command == "set":
            set_setting(args.key, args.value)
            return 0
        if args.config_command == "unset":
            return 0 if unset_setting(args.key) else 1
    if args.command == "doctor":
        print(f"language={language()}")
        print(f"database={db_path()}")
        print(f"tdl={find_tdl() or 'NOT FOUND'}")
        return 0 if find_tdl() else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
