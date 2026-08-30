from __future__ import annotations

SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".webm",
}

SUPPORTED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}


def is_supported_video_extension(ext: str) -> bool:
    return ext.lower() in SUPPORTED_VIDEO_EXTENSIONS


def is_supported_video_mime_type(mime_type: str | None) -> bool:
    if mime_type is None:
        return False
    return mime_type.lower() in {
        item.lower() for item in SUPPORTED_VIDEO_MIME_TYPES
    }