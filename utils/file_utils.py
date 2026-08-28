from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from core.image_types import SUPPORTED_IMAGE_EXTENSIONS, is_supported_image_extension, is_supported_mime_type


def file_exists(path: str | Path) -> bool:
    return Path(path).exists()


def get_file_size(path: str | Path) -> int:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    return p.stat().st_size


def get_file_extension(path: str | Path) -> str:
    p = Path(path)
    return p.suffix.lower()


def get_mime_type(path: str | Path) -> str | None:
    p = Path(path)
    guessed, _ = mimetypes.guess_type(str(p))
    return guessed


def is_image_file(path: str | Path) -> bool:
    if not file_exists(path):
        return False

    ext = get_file_extension(path)
    if not is_supported_image_extension(ext):
        return False

    mime_type = get_mime_type(path)
    if mime_type is not None and not is_supported_mime_type(mime_type):
        return False

    return True


def validate_image_path(path: str | Path) -> tuple[bool, str | None]:
    if path is None or str(path).strip() == "":
        return False, "Input path is empty or invalid."

    p = Path(path)
    if not p.exists():
        return False, f"File does not exist: {p}"

    ext = get_file_extension(p)
    if not is_supported_image_extension(ext):
        return False, f"Unsupported image file type: {ext or 'unknown'}"

    mime_type = get_mime_type(p)
    if mime_type is not None and not is_supported_mime_type(mime_type):
        return False, f"Unsupported MIME type: {mime_type}"

    return True, None


def safe_file_info(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    return {
        "filename": p.name,
        "file_type": get_mime_type(p) or "application/octet-stream",
        "size": p.stat().st_size,
        "extension": get_file_extension(p),
    }
