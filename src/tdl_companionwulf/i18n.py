from __future__ import annotations

import locale
import os

SUPPORTED_LANGUAGES = {
    "de", "en", "fr", "es", "it", "pt", "nl", "pl", "cs", "sk", "hu",
    "ro", "tr", "ru", "uk", "bg", "el", "sv", "da", "no", "nb", "nn", "fi",
}

LANGUAGE_ALIASES = {
    "ger": "de",
    "deu": "de",
    "eng": "en",
    "fre": "fr",
    "fra": "fr",
    "spa": "es",
    "ita": "it",
    "por": "pt",
    "dut": "nl",
    "nld": "nl",
    "cze": "cs",
    "ces": "cs",
    "slo": "sk",
    "slk": "sk",
    "ukr": "uk",
    "gre": "el",
    "ell": "el",
}


def normalize_language(value: str | None) -> str:
    if not value:
        return "en"
    token = str(value).strip().lower()
    token = token.split(".", 1)[0].split("@", 1)[0]
    token = token.replace("-", "_")
    base = token.split("_", 1)[0]
    base = LANGUAGE_ALIASES.get(base, base)
    if base in {"nb", "nn"}:
        return "no"
    return base if base in SUPPORTED_LANGUAGES else "en"


def detect_language(explicit: str | None = None) -> str:
    if explicit and explicit.lower() != "auto":
        return normalize_language(explicit)
    candidates: list[str | None] = []
    try:
        candidates.append(locale.getlocale()[0])
    except Exception:
        pass
    candidates.extend(
        [
            os.environ.get("LC_ALL"),
            os.environ.get("LC_MESSAGES"),
            os.environ.get("LANGUAGE"),
            os.environ.get("LANG"),
        ]
    )
    for candidate in candidates:
        if candidate:
            normalized = normalize_language(candidate)
            if normalized != "en" or str(candidate).lower().startswith("en"):
                return normalized
    return "en"
