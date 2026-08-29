from __future__ import annotations

from pathlib import Path

from PIL import Image

from core.image_types import is_supported_image_extension


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