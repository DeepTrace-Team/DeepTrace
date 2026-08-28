from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
}

SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/tiff",
}


@dataclass(slots=True)
class ImageInput:
    file_path: str | Path
    filename: str
    extension: str
    mime_type: str | None = None
    size: int = 0
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return Path(self.file_path)

    @classmethod
    def from_path(cls, file_path: str | Path) -> "ImageInput":
        path = Path(file_path)
        suffix = path.suffix.lower()
        return cls(
            file_path=path,
            filename=path.name,
            extension=suffix,
            mime_type=None,
            size=path.stat().st_size if path.exists() else 0,
            is_valid=suffix in SUPPORTED_IMAGE_EXTENSIONS,
        )


def is_supported_image_extension(ext: str) -> bool:
    return ext.lower() in SUPPORTED_IMAGE_EXTENSIONS


def is_supported_mime_type(mime_type: str | None) -> bool:
    if mime_type is None:
        return False
    return mime_type.lower() in {item.lower() for item in SUPPORTED_IMAGE_MIME_TYPES}
