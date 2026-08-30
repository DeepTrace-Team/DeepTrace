from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

from core.image_types import is_supported_image_extension
from core.video_types import is_supported_video_extension
from core.audio_types import is_supported_audio_extension


DEFAULT_IMAGE_SIZE = (512, 512)


def preprocess_image(
    image_path: str | Path,
    size: tuple[int, int] = DEFAULT_IMAGE_SIZE,
) -> Image.Image:
    """
    Load and preprocess an image for DeepTrace analysis.

    Steps:
    1. Validate input path.
    2. Check supported image extension.
    3. Load image using Pillow.
    4. Convert image to RGB.
    5. Resize image to the requested size.
    """

    if image_path is None:
        raise TypeError("image_path cannot be None.")

    if not isinstance(image_path, (str, Path)):
        raise TypeError("image_path must be a string or pathlib.Path.")

    if str(image_path).strip() == "":
        raise ValueError("image_path cannot be empty.")

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if not is_supported_image_extension(path.suffix):
        raise ValueError(
            f"Unsupported image file type: {path.suffix or 'unknown'}"
        )

    if (
        not isinstance(size, tuple)
        or len(size) != 2
        or not all(isinstance(value, int) and value > 0 for value in size)
    ):
        raise ValueError("size must be a tuple of two positive integers.")

    try:
        with Image.open(path) as image:
            image.load()
            processed = image.convert("RGB")
            processed = processed.resize(size)

    except (OSError, ValueError) as exc:
        raise ValueError(f"Unable to process image: {path}") from exc

    return processed


def preprocess_video(video_path: str | Path) -> dict[str, Any]:
    """
    Validate a video file and extract its basic technical properties.

    Unlike preprocess_image, this doesn't transform the media (there's
    nothing downstream that consumes resized frames yet) — it validates
    the file opens correctly as a video and returns properties used by
    the metadata step: resolution, frame rate, frame count, duration.

    Requires opencv-python-headless (imported lazily so importing this
    module doesn't hard-fail if it isn't installed and video isn't used).
    """

    if video_path is None:
        raise TypeError("video_path cannot be None.")

    if not isinstance(video_path, (str, Path)):
        raise TypeError("video_path must be a string or pathlib.Path.")

    if str(video_path).strip() == "":
        raise ValueError("video_path cannot be empty.")

    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if not is_supported_video_extension(path.suffix):
        raise ValueError(
            f"Unsupported video file type: {path.suffix or 'unknown'}"
        )

    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "opencv-python-headless is not installed."
        ) from exc

    capture = cv2.VideoCapture(str(path))

    try:
        if not capture.isOpened():
            raise ValueError(f"Unable to open video: {path}")

        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration_seconds = (frame_count / fps) if fps else 0.0

    finally:
        capture.release()

    return {
        "frame_count": frame_count,
        "fps": round(fps, 2),
        "width": width,
        "height": height,
        "duration_seconds": round(duration_seconds, 2),
    }


def preprocess_audio(audio_path: str | Path) -> dict[str, Any]:
    """
    Validate an audio file and extract its basic technical properties.

    Returns duration, bitrate, channel count, and sample rate. Requires
    mutagen (imported lazily), which reads container metadata without
    needing ffmpeg installed.
    """

    if audio_path is None:
        raise TypeError("audio_path cannot be None.")

    if not isinstance(audio_path, (str, Path)):
        raise TypeError("audio_path must be a string or pathlib.Path.")

    if str(audio_path).strip() == "":
        raise ValueError("audio_path cannot be empty.")

    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if not is_supported_audio_extension(path.suffix):
        raise ValueError(
            f"Unsupported audio file type: {path.suffix or 'unknown'}"
        )

    try:
        from mutagen import File as MutagenFile
    except ImportError as exc:
        raise RuntimeError(
            "mutagen is not installed."
        ) from exc

    audio = MutagenFile(str(path))

    if audio is None or audio.info is None:
        raise ValueError(f"Unable to read audio file: {path}")

    return {
        "duration_seconds": round(getattr(audio.info, "length", 0.0) or 0.0, 2),
        "bitrate": getattr(audio.info, "bitrate", None),
        "channels": getattr(audio.info, "channels", None),
        "sample_rate": getattr(audio.info, "sample_rate", None),
    }