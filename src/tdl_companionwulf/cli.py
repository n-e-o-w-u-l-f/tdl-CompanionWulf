from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import socket
import subprocess
import sys
from pathlib import Path

from . import cli_0_6 as _old
from .collisions import prepare_existing_files
from .i18n import detect_language
from .legacy_i18n import legacy_text
from .media import media_extensions
from .tdata import TdataLease, discover_known_tdata, find_system_tdata, scan_volume_roots
from .tdl import TdlOptions, build_chat_export_command, build_chat_list_command, build_download_command, build_login_command
from .telegram_bootstrap import BootstrapError, bootstrap_telegram_desktop
from .wizard import build_export_jobs, parse_chats_json, parse_selection, safe_component

APP_NAME = _old.APP_NAME
ClosingConnection = _old.ClosingConnection
data_dir = _old.data_dir
db_path = _old.db_path
connect = _old.connect
now = _old.now
set_setting = _old.set_setting
get_setting = _old.get_setting
list_settings = _old.list_settings
unset_setting = _old.unset_setting
set_namespace_tdata = _old.set_namespace_tdata
get_namespace_tdata = _old.get_namespace_tdata
unset_namespace_tdata = _old.unset_namespace_tdata
release_active_tdata_leases = _old.release_active_tdata_leases
hold_namespace_tdata_lease = _old.hold_namespace_tdata_lease
event = _old.event
add_url = _old.add_url
queue_rows = _old.queue_rows
show_queue = _old.show_queue
show_status = _old.show_status
next_job = _old.next_job
show_chats = _old.show_chats
export_chat = _old.export_chat
probe_authorization = _old.probe_authorization
login_tdata = _old.login_tdata
auth_candidates = _old.auth_candidates
auth_status = _old.auth_status
requeue = _old.requeue
_split_csv = _old._split_csv
_split_int_csv = _old._split_int_csv
_setting_int = _old._setting_int

_TDL_PATH_OVERRIDE: Path | None = None
_LANGUAGE_OVERRIDE: str | None = None


def set_tdl_path_override(path: Path | str | None) -> None:
    global _TDL_PATH_OVERRIDE
    _TDL_PATH_OVERRIDE = None if path in (None, "") else Path(path)


def _resolve_tdl_candidate(value: Path | str) -> str | None:
    raw = os.path.expandvars(str(value))
    candidate = Path(raw).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    return shutil.which(raw)


def find_tdl() -> str | None:
    if _TDL_PATH_OVERRIDE is not None:
        return _resolve_tdl_candidate(_TDL_PATH_OVERRIDE)
    configured = get_setting("tdl_path")
    if configured:
        return _resolve_tdl_candidate(configured)
    found = shutil.which("tdl") or shutil.which("tdl.exe")
    if found:
        return found
    if os.name == "nt":
        candidate = Path("C:/PS/binaries/tdl.exe")
        if candidate.is_file():
            return str(candidate)
    return None


def set_language_override(value: str | None) -> None:
    global _LANGUAGE_OVERRIDE
    _LANGUAGE_OVERRIDE = value.strip() if value and value.strip() else None


def language() -> str:
    return detect_language(_LANGUAGE_OVERRIDE or get_setting("language") or "auto")


def ui_text(key: str) -> str:
    return legacy_text(language(), key)


def tr(key: str) -> str:
    lang = language()
    return _old.TEXT.get(lang, _old.TEXT["en"]).get(key, key)


def _bounded_int(name: str, minimum: int, maximum: int):
    def parse(value: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc
        if not minimum <= parsed <= maximum:
            raise argparse.ArgumentTypeError(f"{name} must be between {minimum} and {maximum}")
        return parsed
    return parse


def _filename_length(value: str) -> int:
    return _bounded_int("filename length", 32, 255)(value)


def filename_length_from_args(args: argparse.Namespace) -> int:
    value = getattr(args, "max_filename_length", None)
    if value is not None:
        return int(value)
    configured = _setting_int("max_filename_length", 180)
    return configured if 32 <= configured <= 255 else 180


def download_template_from_args(args: argparse.Namespace) -> str:
    explicit = getattr(args, "template", None)
    return explicit or "{{ filenamify .FileName %d }}" % filename_length_from_args(args)


def existing_file_comparison_from_args(args: argparse.Namespace) -> str:
    value = getattr(args, "existing_file_comparison", None) or get_setting("existing_file_comparison") or "size"
    return value if value in {"size", "hash"} else "size"


def new_parallel_namespace() -> str:
    machine_hash = hashlib.sha256((socket.gethostname() or "machine").encode("utf-8")).hexdigest()[:10]
    return f"companion_{machine_hash}_{os.getpid()}"[:64]


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


def auth_scan(roots: list[Path] | None = None, *, all_volumes: bool = False, max_directories: int | None = None) -> int:
    roots = list(roots or [])
    if all_volumes:
        roots.extend(scan_volume_roots())
    if not roots:
        print("Provide at least one scan root or use --all-volumes.", file=sys.stderr)
        return 2
    candidates = find_system_tdata(roots, max_directories=max_directories)
    if not candidates:
        print("No tdata candidates found.")
        return 1
    for candidate in candidates:
        marker = "key_data" if candidate.has_key_data else "no-key_data"
        print(f"{candidate.path} [{marker} {candidate.source}]")
    return 0


def auth_bootstrap(options: TdlOptions, *, timeout_seconds: float | None = None) -> int:
    if os.name != "nt":
        print("Telegram portable bootstrap is available only on Windows.", file=sys.stderr)
        return 2
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2
    try:
        candidate = bootstrap_telegram_desktop(data_dir() / "telegram-clients", timeout_seconds=timeout_seconds)
    except BootstrapError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Telegram Desktop tdata ready: {candidate}")
    return login_tdata(tdl, options, candidate)


def auth_auto(options: TdlOptions, *, scan_roots: list[Path] | None = None, scan_all_volumes: bool = False, scan_max_directories: int | None = None, allow_bootstrap: bool = True, bootstrap_timeout: float | None = None) -> int:
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
    candidates = discover_known_tdata(extra_paths=[associated] if associated else [])
    roots = list(scan_roots or [])
    if scan_all_volumes:
        roots.extend(scan_volume_roots())
    if roots:
        candidates.extend(find_system_tdata(roots, max_directories=scan_max_directories))

    saw_locked = False
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate.has_key_data:
            continue
        key = os.path.normcase(str(candidate.path))
        if key in seen:
            continue
        seen.add(key)
        print(f"Trying tdata: {candidate.path}")
        code = login_tdata(tdl, options, candidate.path)
        if code == 0:
            print(f"Authorized namespace '{options.namespace}' with {candidate.path}")
            return 0
        if code == 3:
            saw_locked = True
    if saw_locked:
        print("A matching tdata candidate is already leased by another CompanionWulf process.", file=sys.stderr)
        return 3

    print("No reusable tdata candidate succeeded; trying tdl native desktop detection.")
    result = subprocess.run(build_login_command(tdl, options))
    if result.returncode == 0:
        try:
            authorized, _ = probe_authorization(tdl, options)
            if authorized:
                return 0
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    if allow_bootstrap and os.name == "nt":
        print("Native desktop detection did not authorize; starting isolated Telegram Desktop.")
        return auth_bootstrap(options, timeout_seconds=bootstrap_timeout)
    return int(result.returncode or 1)


def run_next(download_dir: Path, options: TdlOptions, *, include=None, exclude=None, takeout=False, continue_download=False, restart_download=False, rewrite_ext=False, desc=False, group=False, skip_same=True, template="{{ filenamify .FileName 180 }}", extra_args=None, dry_run=False) -> int:
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr)
        return 2
    download_dir.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        job = next_job(conn)
        if job is None:
            print(tr("empty")); return 0
        command = build_download_command(tdl, options, urls=[str(job["url"])], directory=download_dir, include=include, exclude=exclude, takeout=takeout, continue_download=continue_download, restart_download=restart_download, rewrite_ext=rewrite_ext, desc=desc, group=group, skip_same=skip_same, template=template, extra_args=extra_args)
        if dry_run:
            print("WHAT-IF: " + shlex.join(command)); return 0
        conn.execute("UPDATE jobs SET status='running', attempts=attempts+1, started_at=?, last_error=NULL WHERE id=?", (now(), job["id"]))
        conn.commit(); event(conn, int(job["id"]), "tdl started")
        print(f"{tr('running')} #{job['id']}: {job['url']}")
        result = subprocess.run(command)
        if result.returncode == 0:
            conn.execute("UPDATE jobs SET status='completed', exit_code=0, finished_at=? WHERE id=?", (now(), job["id"]))
            conn.commit(); event(conn, int(job["id"]), "tdl completed")
            print(f"{tr('completed')} #{job['id']}"); return 0
        error = f"tdl exit code {result.returncode}"
        conn.execute("UPDATE jobs SET status='failed', exit_code=?, finished_at=?, last_error=? WHERE id=?", (result.returncode, now(), error, job["id"]))
        conn.commit(); event(conn, int(job["id"]), error, "ERROR")
        print(f"{tr('failed')} #{job['id']}: {error}", file=sys.stderr)
        return int(result.returncode or 1)


def run_wizard(args: argparse.Namespace) -> int:
    if args.continue_download and args.restart_download:
        print("--continue and --restart are mutually exclusive", file=sys.stderr); return 2
    tdl = find_tdl()
    if not tdl:
        print(tr("tdl_missing"), file=sys.stderr); return 2
    options = options_from_args(args)
    if not args.no_auto_auth:
        try:
            authorized, _ = probe_authorization(tdl, options)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr); return 2
        if not authorized:
            code = auth_auto(options, scan_roots=args.scan_root, scan_all_volumes=args.scan_all_volumes, scan_max_directories=args.scan_max_directories, allow_bootstrap=not args.no_bootstrap, bootstrap_timeout=args.bootstrap_timeout)
            if code != 0: return code
    if not hold_namespace_tdata_lease(options.namespace):
        associated = get_namespace_tdata(options.namespace)
        if getattr(args, "namespace", None) or args.no_auto_auth:
            print(f"tdata is already in use for namespace '{options.namespace}': {associated}", file=sys.stderr); return 3
        options.namespace = new_parallel_namespace()
        print(f"Using parallel namespace: {options.namespace}")
        code = auth_auto(options, scan_roots=args.scan_root, scan_all_volumes=args.scan_all_volumes, scan_max_directories=args.scan_max_directories, allow_bootstrap=not args.no_bootstrap, bootstrap_timeout=args.bootstrap_timeout)
        if code != 0: return code
        if not hold_namespace_tdata_lease(options.namespace): return 3

    result = subprocess.run(build_chat_list_command(tdl, options, json_output=True, filter_expression=args.chat_filter), capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr); return int(result.returncode or 1)
    try:
        chats = sorted(parse_chats_json(result.stdout), key=lambda item: item.name.casefold())
    except ValueError as exc:
        print(str(exc), file=sys.stderr); return 1
    if not chats:
        print(ui_text("NoChats"), file=sys.stderr); return 1
    print("\n" + ui_text("Chats"))
    for index, chat in enumerate(chats, 1):
        topic_text = f" ({len(chat.topics)} {ui_text('Topics')})" if chat.topics else ""
        print(f"{index:>3}. {chat.name} [{chat.type}]{topic_text} ID={chat.id}")
    try:
        selected = parse_selection(input("Select chats [1,3-5 or all]: "), len(chats))
    except (EOFError, ValueError) as exc:
        print(f"Invalid chat selection: {exc}", file=sys.stderr); return 1
    if not selected:
        print(ui_text("NoSelection"), file=sys.stderr); return 1
    topics: dict[int, list[int]] = {}
    try:
        for idx in selected:
            chat = chats[idx]
            if not chat.topics: continue
            print(f"\n{ui_text('Topics')}: {chat.name}")
            for num, topic in enumerate(chat.topics, 1): print(f"{num:>3}. {topic.title} ID={topic.id}")
            topics[chat.id] = parse_selection(input("Select topics [1,3-5 or all]: "), len(chat.topics))
        jobs = build_export_jobs(chats, selected_chat_indices=selected, topic_selections=topics)
    except (EOFError, ValueError) as exc:
        print(f"Invalid topic selection: {exc}", file=sys.stderr); return 1
    media_names = _split_csv(args.media)
    if not media_names:
        try: media_names = _split_csv(input("Media [archive,audio,images,video] (audio): ").strip() or "audio")
        except EOFError: media_names = ["audio"]
    try: extensions = media_extensions(media_names)
    except ValueError as exc: print(str(exc), file=sys.stderr); return 1
    root = args.dir or Path(get_setting("download_dir") or (Path.cwd() / "downloads")); root.mkdir(parents=True, exist_ok=True)
    successes = errors = 0
    for number, job in enumerate(jobs, 1):
        destination = root / safe_component(job.chat_name)
        if job.topic_id is not None: destination /= safe_component(job.topic_name)
        destination.mkdir(parents=True, exist_ok=True)
        suffix = str(job.topic_id) if job.topic_id is not None else "chat"
        export_path = destination / f"{job.chat_id}_{suffix}_tdl-export.json"
        label = job.chat_name + (f" / {job.topic_name}" if job.topic_id is not None else "")
        print(f"\n[{number}/{len(jobs)}] Export: {label}")
        exported = subprocess.run(build_chat_export_command(tdl, options, chat=str(job.chat_id), topic=job.topic_id, output=export_path))
        if exported.returncode != 0 or not export_path.is_file() or export_path.stat().st_size == 0:
            errors += 1; continue
        if not args.no_protect_existing:
            try:
                summary = prepare_existing_files(export_path, destination, comparison=existing_file_comparison_from_args(args), max_filename_length=filename_length_from_args(args))
                if summary.renamed: print(f"[{number}/{len(jobs)}] Protected existing files: {summary.renamed}")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                print(f"Collision precheck skipped: {exc}", file=sys.stderr)
        command = build_download_command(tdl, options, files=[export_path], directory=destination, include=extensions, takeout=args.takeout, continue_download=args.continue_download, restart_download=args.restart_download, rewrite_ext=args.rewrite_ext, desc=args.desc, group=args.group, skip_same=not args.no_skip_same, template=download_template_from_args(args), extra_args=args.extra_arg)
        if args.what_if_download:
            print("WHAT-IF: " + shlex.join(command)); successes += 1; continue
        print(f"[{number}/{len(jobs)}] Download: {label}")
        if subprocess.run(command).returncode == 0: successes += 1
        else: errors += 1
    print(f"\nWizard complete: {successes} successful, {errors} failed, {len(jobs)} total")
    return 0 if errors == 0 else 1


def _add_tdl_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tdl-path", type=Path); parser.add_argument("--language", default=argparse.SUPPRESS)
    parser.add_argument("-n", "--namespace")
    parser.add_argument("-l", "--limit", type=_bounded_int("limit", 1, 128))
    parser.add_argument("-t", "--threads", type=_bounded_int("threads", 1, 128))
    parser.add_argument("--delay", type=_bounded_int("delay", 0, 86400))
    parser.add_argument("--pool", type=_bounded_int("pool", 0, 128))
    parser.add_argument("--proxy"); parser.add_argument("--ntp"); parser.add_argument("--reconnect-timeout", dest="reconnect_timeout"); parser.add_argument("--storage")
    parser.add_argument("--debug", action="store_true"); parser.add_argument("--disable-progress-ps", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tdl-companionwulf")
    parser.add_argument("--version", action="version", version="tdl-CompanionWulf 1.0.0")
    parser.add_argument("--language", help="Override UI language (auto/de/en/fr/es/it/pt/...)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("add"); p.add_argument("urls", nargs="+"); p.add_argument("--priority", "-p", type=int, default=50)
    sub.add_parser("queue"); sub.add_parser("status")
    p = sub.add_parser("run"); p.add_argument("--dir", type=Path); _add_tdl_options(p)
    p.add_argument("-i", "--include"); p.add_argument("-e", "--exclude"); p.add_argument("--media"); p.add_argument("--takeout", action="store_true"); p.add_argument("--continue", dest="continue_download", action="store_true"); p.add_argument("--restart", dest="restart_download", action="store_true"); p.add_argument("--rewrite-ext", action="store_true"); p.add_argument("--desc", action="store_true"); p.add_argument("--group", action="store_true"); p.add_argument("--template"); p.add_argument("--max-filename-length", type=_filename_length); p.add_argument("--what-if-download", "--dry-run", action="store_true"); p.add_argument("--no-skip-same", action="store_true"); p.add_argument("--extra-arg", action="append", default=[])
    p = sub.add_parser("chats"); _add_tdl_options(p); p.add_argument("--json", action="store_true"); p.add_argument("-f", "--filter", default="")
    p = sub.add_parser("export"); _add_tdl_options(p); p.add_argument("-c", "--chat", default=""); p.add_argument("--topic", type=int); p.add_argument("--reply", type=int); p.add_argument("-T", "--type", dest="export_type", choices=["time","id","last"], default="time"); p.add_argument("-i", "--input", default=""); p.add_argument("-o", "--output", type=Path, default=Path("tdl-export.json")); p.add_argument("-f", "--filter", default=""); p.add_argument("--all", dest="all_messages", action="store_true"); p.add_argument("--with-content", action="store_true"); p.add_argument("--raw", action="store_true")
    p = sub.add_parser("wizard"); p.add_argument("--dir", type=Path); _add_tdl_options(p); p.add_argument("--media"); p.add_argument("--chat-filter", default=""); p.add_argument("--no-auto-auth", action="store_true"); p.add_argument("--no-bootstrap", action="store_true"); p.add_argument("--bootstrap-timeout", type=float); p.add_argument("--scan-root", action="append", type=Path, default=[]); p.add_argument("--scan-all-volumes", action="store_true"); p.add_argument("--scan-max-directories", type=int); p.add_argument("--no-protect-existing", action="store_true"); p.add_argument("--existing-file-comparison", choices=["size","hash"]); p.add_argument("--what-if-download", "--dry-run", action="store_true"); p.add_argument("--takeout", action="store_true"); p.add_argument("--continue", dest="continue_download", action="store_true"); p.add_argument("--restart", dest="restart_download", action="store_true"); p.add_argument("--rewrite-ext", action="store_true"); p.add_argument("--desc", action="store_true"); p.add_argument("--group", action="store_true"); p.add_argument("--template"); p.add_argument("--max-filename-length", type=_filename_length); p.add_argument("--no-skip-same", action="store_true"); p.add_argument("--extra-arg", action="append", default=[])
    p = sub.add_parser("auth"); auth = p.add_subparsers(dest="auth_command", required=True)
    a = auth.add_parser("status"); _add_tdl_options(a)
    a = auth.add_parser("candidates"); a.add_argument("-n", "--namespace", default="default")
    a = auth.add_parser("login"); _add_tdl_options(a); a.add_argument("--tdata", type=Path, required=True)
    a = auth.add_parser("bootstrap"); _add_tdl_options(a); a.add_argument("--timeout", type=float)
    a = auth.add_parser("scan"); a.add_argument("roots", nargs="*", type=Path); a.add_argument("--all-volumes", action="store_true"); a.add_argument("--max-directories", type=int)
    a = auth.add_parser("auto"); _add_tdl_options(a); a.add_argument("--scan-root", action="append", type=Path, default=[]); a.add_argument("--scan-all-volumes", action="store_true"); a.add_argument("--scan-max-directories", type=int); a.add_argument("--no-bootstrap", action="store_true"); a.add_argument("--bootstrap-timeout", type=float)
    p = sub.add_parser("requeue"); p.add_argument("job_id", type=int)
    p = sub.add_parser("config"); cfg = p.add_subparsers(dest="config_command", required=True); cfg.add_parser("list"); c=cfg.add_parser("get"); c.add_argument("key"); c=cfg.add_parser("set"); c.add_argument("key"); c.add_argument("value"); c=cfg.add_parser("unset"); c.add_argument("key")
    sub.add_parser("doctor")
    return parser


def main() -> int:
    args = build_parser().parse_args(); set_language_override(getattr(args,"language",None)); set_tdl_path_override(getattr(args,"tdl_path",None))
    if args.command == "add":
        for url in args.urls: add_url(url,args.priority)
        return 0
    if args.command == "queue": show_queue(); return 0
    if args.command == "status": show_status(); return 0
    if args.command == "run":
        if args.continue_download and args.restart_download: return 2
        options=options_from_args(args); directory=args.dir or Path(get_setting("download_dir") or (Path.cwd()/"downloads")); include=_split_csv(args.include)
        if args.media: include=list(dict.fromkeys(include+media_extensions(_split_csv(args.media))))
        return run_next(directory,options,include=include,exclude=_split_csv(args.exclude),takeout=args.takeout,continue_download=args.continue_download,restart_download=args.restart_download,rewrite_ext=args.rewrite_ext,desc=args.desc,group=args.group,skip_same=not args.no_skip_same,template=download_template_from_args(args),extra_args=args.extra_arg,dry_run=args.what_if_download)
    if args.command == "chats": return show_chats(options_from_args(args),json_output=args.json,filter_expression=args.filter)
    if args.command == "export": return export_chat(options_from_args(args),chat=args.chat,topic=args.topic,reply=args.reply,export_type=args.export_type,inputs=_split_int_csv(args.input),output=args.output,filter_expression=args.filter,all_messages=args.all_messages,with_content=args.with_content,raw=args.raw)
    if args.command == "wizard": return run_wizard(args)
    if args.command == "auth":
        if args.auth_command == "status": return auth_status(options_from_args(args))
        if args.auth_command == "candidates": return auth_candidates(args.namespace)
        if args.auth_command == "login":
            tdl=find_tdl(); return 2 if not tdl else login_tdata(tdl,options_from_args(args),args.tdata)
        if args.auth_command == "bootstrap": return auth_bootstrap(options_from_args(args),timeout_seconds=args.timeout)
        if args.auth_command == "scan": return auth_scan(args.roots,all_volumes=args.all_volumes,max_directories=args.max_directories)
        if args.auth_command == "auto": return auth_auto(options_from_args(args),scan_roots=args.scan_root,scan_all_volumes=args.scan_all_volumes,scan_max_directories=args.scan_max_directories,allow_bootstrap=not args.no_bootstrap,bootstrap_timeout=args.bootstrap_timeout)
    if args.command == "requeue": return requeue(args.job_id)
    if args.command == "config":
        if args.config_command == "list":
            for key,value in list_settings(): print(f"{key}={value}")
            return 0
        if args.config_command == "get":
            value=get_setting(args.key)
            if value is None: return 1
            print(value); return 0
        if args.config_command == "set": set_setting(args.key,args.value); return 0
        if args.config_command == "unset": return 0 if unset_setting(args.key) else 1
    if args.command == "doctor":
        print(f"language={language()}"); print(f"database={db_path()}"); print(f"tdl={find_tdl() or 'NOT FOUND'}"); return 0 if find_tdl() else 2
    return 1

_old.find_tdl = find_tdl
_old.language = language
_old.tr = tr
_old.options_from_args = options_from_args

if __name__ == "__main__":
    raise SystemExit(main())
