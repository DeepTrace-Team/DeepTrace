from __future__ import annotations

SUPPORTED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
}

SUPPORTED_AUDIO_MIME_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a",
}


def is_supported_audio_extension(ext: str) -> bool:
    return ext.lower() in SUPPORTED_AUDIO_EXTENSIONS


def is_supported_audio_mime_type(mime_type: str | None) -> bool:
    if mime_type is None:
        return False
    return mime_type.lower() in {
        item.lower() for item in SUPPORTED_AUDIO_MIME_TYPES
    }