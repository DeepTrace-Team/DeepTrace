from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _validate_image_path(image_path: str | Path) -> Path:
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

    return path


async def _detect_async(image_path: Path) -> dict[str, Any]:
    api_key = os.getenv("REALITY_DEFENDER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "REALITY_DEFENDER_API_KEY is not configured."
        )

    try:
        from realitydefender import RealityDefender
    except ImportError as exc:
        raise RuntimeError(
            "realitydefender is not installed."
        ) from exc

    detector = RealityDefender(api_key=api_key)

    upload_response = await detector.upload(
        file_path=str(image_path)
    )

    request_id = upload_response.get("request_id")

    if not request_id:
        raise RuntimeError(
            "Reality Defender did not return a request_id."
        )

    result = await detector.get_result(request_id)

    if not isinstance(result, dict):
        raise RuntimeError(
            "Reality Defender returned an invalid result."
        )

    return result


def detect_image(image_path: str | Path) -> dict[str, Any]:
    """
    Run the configured AI detector against an image.

    Returns the raw detector response.
    """

    path = _validate_image_path(image_path)
    return asyncio.run(_detect_async(path))
