from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Topic:
    id: int
    title: str


@dataclass(frozen=True, slots=True)
class Chat:
    id: int
    type: str = "unknown"
    visible_name: str = ""
    username: str = ""
    topics: tuple[Topic, ...] = ()

    @property
    def name(self) -> str:
        return self.visible_name.strip() or self.username.strip() or "(unnamed chat)"


@dataclass(frozen=True, slots=True)
class ExportJob:
    chat_id: int
    chat_name: str
    topic_id: int | None = None
    topic_name: str = ""


def parse_chats_json(payload: str) -> list[Chat]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid tdl chat JSON") from exc
    if not isinstance(data, list):
        raise ValueError("tdl chat JSON must contain a list")

    chats: list[Chat] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("each chat must be an object")
        raw_topics = item.get("topics") or []
        if not isinstance(raw_topics, list):
            raise ValueError("chat topics must be a list")
        topics = tuple(
            Topic(id=int(topic["id"]), title=str(topic.get("title") or "(unnamed topic)"))
            for topic in raw_topics
            if isinstance(topic, dict) and "id" in topic
        )
        chats.append(
            Chat(
                id=int(item["id"]),
                type=str(item.get("type") or "unknown"),
                visible_name=str(item.get("visible_name") or ""),
                username=str(item.get("username") or ""),
                topics=topics,
            )
        )
    return chats


def parse_selection(text: str, count: int) -> list[int]:
    if count < 0:
        raise ValueError("count must not be negative")
    value = text.strip().lower()
    if value in {"all", "*"}:
        return list(range(count))
    if not value:
        return []

    selected: list[int] = []
    seen: set[int] = set()
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            parts = token.split("-", 1)
            if not all(part.isdigit() for part in parts):
                raise ValueError(f"invalid selection: {token}")
            start, end = map(int, parts)
            if start > end:
                raise ValueError(f"invalid selection range: {token}")
            numbers = range(start, end + 1)
        else:
            if not token.isdigit():
                raise ValueError(f"invalid selection: {token}")
            numbers = (int(token),)
        for number in numbers:
            if number < 1 or number > count:
                raise ValueError(f"selection out of range: {number}")
            index = number - 1
            if index not in seen:
                seen.add(index)
                selected.append(index)
    return selected


def build_export_jobs(
    chats: list[Chat],
    *,
    selected_chat_indices: list[int],
    topic_selections: dict[int, list[int]],
) -> list[ExportJob]:
    jobs: list[ExportJob] = []
    for chat_index in selected_chat_indices:
        if chat_index < 0 or chat_index >= len(chats):
            raise ValueError(f"chat selection out of range: {chat_index + 1}")
        chat = chats[chat_index]
        if not chat.topics:
            jobs.append(ExportJob(chat_id=chat.id, chat_name=chat.name))
            continue
        selected_topics = topic_selections.get(chat.id, [])
        if not selected_topics:
            raise ValueError(f"no topics selected for {chat.name}")
        for topic_index in selected_topics:
            if topic_index < 0 or topic_index >= len(chat.topics):
                raise ValueError(f"topic selection out of range for {chat.name}")
            topic = chat.topics[topic_index]
            jobs.append(
                ExportJob(
                    chat_id=chat.id,
                    chat_name=chat.name,
                    topic_id=topic.id,
                    topic_name=topic.title,
                )
            )
    return jobs


_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def safe_component(value: str, *, max_length: int = 100) -> str:
    if max_length < 1:
        raise ValueError("max_length must be positive")
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(value))
    cleaned = cleaned.strip().rstrip(". ")
    if not cleaned:
        cleaned = "unnamed"
    stem = cleaned.split(".", 1)[0].upper()
    if stem in _RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    cleaned = cleaned[:max_length].rstrip(". ")
    return cleaned or "unnamed"
