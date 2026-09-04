from __future__ import annotations

import argparse
import locale
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

APP_NAME = "tdl-CompanionWulf"

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
    candidates = []
    try:
        candidates.append(locale.getlocale()[0])
    except Exception:
        pass
    candidates.extend([os.environ.get("LANG"), os.environ.get("LC_ALL")])
    for value in candidates:
        if value and str(value).lower().startswith("de"):
            return "de"
    return "en"


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
    conn = sqlite3.connect(db_path())
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
    conn.commit()
    return conn


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


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


def run_next(download_dir: Path, limit: int, threads: int) -> int:
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
        command = [
            tdl,
            "dl",
            "--url",
            str(job["url"]),
            "--dir",
            str(download_dir),
            "--skip-same",
            "--limit",
            str(limit),
            "--threads",
            str(threads),
        ]
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tdl-companionwulf")
    parser.add_argument("--version", action="version", version="tdl-CompanionWulf 0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("add", help="Add Telegram URLs to the SQLite queue")
    p.add_argument("urls", nargs="+")
    p.add_argument("--priority", "-p", type=int, default=50)
    sub.add_parser("queue", help="Show queued jobs")
    sub.add_parser("status", help="Show queue status summary")
    p = sub.add_parser("run", help="Run the next queued job with tdl")
    p.add_argument("--dir", type=Path, default=Path.cwd() / "downloads")
    p.add_argument("--limit", type=int, default=2)
    p.add_argument("--threads", type=int, default=4)
    p = sub.add_parser("requeue", help="Requeue one job")
    p.add_argument("job_id", type=int)
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
        return run_next(args.dir, args.limit, args.threads)
    if args.command == "requeue":
        return requeue(args.job_id)
    if args.command == "doctor":
        print(f"language={language()}")
        print(f"database={db_path()}")
        print(f"tdl={find_tdl() or 'NOT FOUND'}")
        return 0 if find_tdl() else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
