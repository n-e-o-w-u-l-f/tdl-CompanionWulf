from __future__ import annotations

MEDIA_PROFILES: dict[str, tuple[str, ...]] = {
    "archive": (
        "zip", "rar", "7z", "tar", "gz", "bz2", "xz", "tgz", "tbz", "tbz2",
        "tar.gz", "tar.bz2", "tar.xz",
    ),
    "audio": (
        "mp3", "flac", "wav", "m4a", "aac", "ogg", "oga", "opus", "wma", "aiff",
        "aif", "alac", "ape", "ac3", "mka", "amr",
    ),
    "images": (
        "jpg", "jpeg", "png", "gif", "webp", "bmp", "tif", "tiff", "heic", "heif",
        "avif",
    ),
    "video": (
        "mp4", "mkv", "avi", "mov", "webm", "m4v", "wmv", "flv", "mpeg", "mpg",
        "3gp", "ts", "m2ts", "mts",
    ),
}

PROFILE_ALIASES = {
    "image": "images",
    "img": "images",
    "videos": "video",
    "archives": "archive",
}


def normalize_profile(name: str) -> str:
    key = name.strip().lower()
    return PROFILE_ALIASES.get(key, key)


def media_extensions(profiles: list[str] | tuple[str, ...]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for profile in profiles:
        key = normalize_profile(profile)
        if key not in MEDIA_PROFILES:
            raise ValueError(f"unknown media profile: {profile}")
        for extension in MEDIA_PROFILES[key]:
            if extension not in seen:
                seen.add(extension)
                result.append(extension)
    return result
