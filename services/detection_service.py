from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# COMMON PATH VALIDATION
# ============================================================

def _validate_media_path(
    media_path: str | Path,
) -> Path:

    if media_path is None:
        raise TypeError(
            "media_path cannot be None."
        )

    if not isinstance(
        media_path,
        (str, Path),
    ):
        raise TypeError(
            "media_path must be a string or pathlib.Path."
        )

    if str(media_path).strip() == "":
        raise ValueError(
            "media_path cannot be empty."
        )

    path = Path(media_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    return path


# ============================================================
# REALITY DEFENDER
# IMAGE + AUDIO
# ============================================================

async def _detect_async(
    media_path: Path,
) -> dict[str, Any]:

    api_key = os.getenv(
        "REALITY_DEFENDER_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "REALITY_DEFENDER_API_KEY is not configured."
        )

    try:

        from realitydefender import RealityDefender

    except ImportError as exc:

        raise RuntimeError(
            "realitydefender is not installed.\n"
            "Run:\n"
            "pip install realitydefender"
        ) from exc

    # --------------------------------------------------------
    # CREATE CLIENT
    # --------------------------------------------------------

    detector = RealityDefender(
        api_key=api_key
    )

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    try:

        upload_response = await detector.upload(
            file_path=str(media_path)
        )

    except Exception as exc:

        raise RuntimeError(
            "Reality Defender upload failed.\n"
            f"{exc}"
        ) from exc

    # --------------------------------------------------------
    # NORMALIZE UPLOAD RESPONSE
    # --------------------------------------------------------

    if hasattr(
        upload_response,
        "model_dump",
    ):

        upload_response = (
            upload_response.model_dump()
        )

    elif hasattr(
        upload_response,
        "dict",
    ):

        upload_response = (
            upload_response.dict()
        )

    if not isinstance(
        upload_response,
        dict,
    ):

        raise RuntimeError(
            "Reality Defender returned "
            "an invalid upload response."
        )

    # --------------------------------------------------------
    # REQUEST ID
    # --------------------------------------------------------

    request_id = (
        upload_response.get(
            "request_id"
        )
        or upload_response.get(
            "requestId"
        )
        or upload_response.get(
            "id"
        )
    )

    if not request_id:

        raise RuntimeError(
            "Reality Defender did not return "
            "a request_id.\n"
            f"Response: {upload_response}"
        )

    # --------------------------------------------------------
    # GET RESULT
    # --------------------------------------------------------

    try:

        result = await detector.get_result(
            request_id
        )

    except Exception as exc:

        raise RuntimeError(
            "Reality Defender result request failed.\n"
            f"{exc}"
        ) from exc

    # --------------------------------------------------------
    # NORMALIZE RESULT OBJECT
    # --------------------------------------------------------

    if hasattr(
        result,
        "model_dump",
    ):

        result = result.model_dump()

    elif hasattr(
        result,
        "dict",
    ):

        result = result.dict()

    if not isinstance(
        result,
        dict,
    ):

        raise RuntimeError(
            "Reality Defender returned "
            "an invalid detection result."
        )

    # ========================================================
    # EXTRACT STATUS
    # ========================================================

    status = (
        result.get("status")
        or result.get("classification")
        or result.get("label")
        or ""
    )

    status = str(
        status
    ).upper().strip()

    # ========================================================
    # EXTRACT SCORE
    # ========================================================

    score = (
        result.get("score")
        if "score" in result
        else result.get("confidence")
    )

    # --------------------------------------------------------
    # DO NOT FABRICATE A SCORE
    # --------------------------------------------------------

    if score is not None:

        try:

            score = float(score)

        except (
            TypeError,
            ValueError,
        ):

            score = None

    # ========================================================
    # MODELS
    # ========================================================

    models = result.get(
        "models",
        [],
    )

    if not isinstance(
        models,
        list,
    ):

        models = []

    # ========================================================
    # REASONS
    # ========================================================

    reasons: list[Any] = []

    metadata = result.get(
        "metadata"
    )

    if isinstance(
        metadata,
        dict,
    ):

        metadata_reasons = metadata.get(
            "reasons",
            []
        )

        if isinstance(
            metadata_reasons,
            list,
        ):

            reasons.extend(
                metadata_reasons
            )

    results_summary = result.get(
        "resultsSummary"
    )

    if isinstance(
        results_summary,
        dict,
    ):

        summary_metadata = (
            results_summary.get(
                "metadata"
            )
        )

        if isinstance(
            summary_metadata,
            dict,
        ):

            summary_reasons = (
                summary_metadata.get(
                    "reasons",
                    []
                )
            )

            if isinstance(
                summary_reasons,
                list,
            ):

                reasons.extend(
                    summary_reasons
                )

    # ========================================================
    # PRESERVE RAW RESPONSE
    # ========================================================

    return {
        "provider":
            "Reality Defender",

        "request_id":
            request_id,

        "status":
            status,

        "score":
            score,

        "models":
            models,

        "reasons":
            reasons,

        "raw_result":
            result,
    }


# ============================================================
# IMAGE DETECTION
# ============================================================

def detect_image(
    image_path: str | Path,
) -> dict[str, Any]:

    path = _validate_media_path(
        image_path
    )

    return asyncio.run(
        _detect_async(path)
    )


# ============================================================
# AUDIO DETECTION
# ============================================================

def detect_audio(
    audio_path: str | Path,
) -> dict[str, Any]:

    path = _validate_media_path(
        audio_path
    )

    return asyncio.run(
        _detect_async(path)
    )


# ============================================================
# VIDEO DETECTION
#
# IMPORTANT:
# Hive V3 video detection lives entirely inside
# services/video_service.py.
#
# This function only delegates to that service.
# ============================================================

def detect_video(
    video_path: str | Path,
) -> dict[str, Any]:

    path = _validate_media_path(
        video_path
    )

    try:

        from services.video_service import (
            detect_video as hive_detect_video,
        )

    except ImportError as exc:

        raise RuntimeError(
            "Could not import "
            "services.video_service.\n"
            "Make sure video_service.py exists "
            "inside the services folder."
        ) from exc

    return hive_detect_video(
        path
    )