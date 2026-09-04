from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class TdlOptions:
    namespace: str = "default"
    limit: int = 2
    threads: int = 4
    delay: int = 0
    pool: int = 8
    proxy: str = ""
    ntp: str = ""
    reconnect_timeout: str = ""
    storage: str = ""
    debug: bool = False
    disable_progress_ps: bool = False


def build_global_args(options: TdlOptions) -> list[str]:
    args = [
        "-n", options.namespace or "default",
        "-l", str(options.limit),
        "-t", str(options.threads),
        "--delay", f"{options.delay}s",
        "--pool", str(options.pool),
    ]
    if options.debug:
        args.append("--debug")
    if options.disable_progress_ps:
        args.append("--disable-progress-ps")
    if options.proxy:
        args.extend(["--proxy", options.proxy])
    if options.ntp:
        args.extend(["--ntp", options.ntp])
    if options.reconnect_timeout:
        args.extend(["--reconnect-timeout", options.reconnect_timeout])
    if options.storage:
        args.extend(["--storage", options.storage])
    return args


def build_chat_list_command(
    tdl_path: str,
    options: TdlOptions,
    *,
    json_output: bool = False,
    filter_expression: str = "",
) -> list[str]:
    command = [tdl_path, *build_global_args(options), "chat", "ls"]
    if filter_expression:
        command.extend(["-f", filter_expression])
    if json_output:
        command.extend(["-o", "json"])
    return command


def _csv(values: Iterable[str] | None) -> str:
    return ",".join(str(value).lstrip(".") for value in (values or []) if str(value).strip())


def build_download_command(
    tdl_path: str,
    options: TdlOptions,
    *,
    urls: Iterable[str] | None = None,
    files: Iterable[str | Path] | None = None,
    directory: str | Path = "downloads",
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    takeout: bool = False,
    continue_download: bool = False,
    restart_download: bool = False,
    rewrite_ext: bool = False,
    desc: bool = False,
    group: bool = False,
    skip_same: bool = True,
    template: str = "{{ filenamify .FileName 180 }}",
    extra_args: Iterable[str] | None = None,
) -> list[str]:
    if continue_download and restart_download:
        raise ValueError("--continue and --restart are mutually exclusive")

    command = [tdl_path, *build_global_args(options), "dl"]
    for url in urls or []:
        command.extend(["-u", str(url)])
    for file_path in files or []:
        command.extend(["-f", str(file_path)])
    command.extend(["-d", str(directory)])

    include_csv = _csv(include)
    exclude_csv = _csv(exclude)
    if include_csv and exclude_csv:
        raise ValueError("include and exclude filters are mutually exclusive")
    if include_csv:
        command.extend(["-i", include_csv])
    if exclude_csv:
        command.extend(["-e", exclude_csv])
    if template:
        command.extend(["--template", template])
    if skip_same:
        command.append("--skip-same")
    if takeout:
        command.append("--takeout")
    if continue_download:
        command.append("--continue")
    if restart_download:
        command.append("--restart")
    if rewrite_ext:
        command.append("--rewrite-ext")
    if desc:
        command.append("--desc")
    if group:
        command.append("--group")
    for argument in extra_args or []:
        if str(argument).strip():
            command.append(str(argument))
    return command
