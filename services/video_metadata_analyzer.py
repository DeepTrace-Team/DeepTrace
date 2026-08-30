from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from core.contracts import (
    Evidence,
    MetadataInfo,
)
from utils.preprocessing import (
    preprocess_video,
)


def analyze_video_metadata(
    video_path: str | Path,
) -> tuple[
    MetadataInfo,
    list[Evidence],
]:
    """
    Extract technical properties from a video.

    The metadata is informational only. It is NOT used
    as the deepfake detector.

    Extracted properties:
        - Resolution
        - Frame rate
        - Frame count
        - Duration

    Returns
    -------
    tuple
        MetadataInfo and a list of Evidence objects.
    """

    # --------------------------------------------------
    # Validate path
    # --------------------------------------------------

    if video_path is None:
        raise TypeError(
            "video_path cannot be None."
        )

    if not isinstance(
        video_path,
        (str, Path),
    ):
        raise TypeError(
            "video_path must be a string or pathlib.Path."
        )

    path = Path(
        video_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Video file not found: {path}"
        )

    # --------------------------------------------------
    # Extract technical properties
    # --------------------------------------------------

    properties = preprocess_video(
        path
    )

    width = properties.get(
        "width",
        0,
    )

    height = properties.get(
        "height",
        0,
    )

    fps = properties.get(
        "fps",
        0,
    )

    frame_count = properties.get(
        "frame_count",
        0,
    )

    duration = properties.get(
        "duration_seconds",
        0,
    )

    # --------------------------------------------------
    # Metadata findings
    # --------------------------------------------------

    findings = [
        f"Resolution: {width}x{height}",

        f"Frame rate: {fps} fps",

        f"Frame count: {frame_count}",

        f"Duration: {duration}s",
    ]

    metadata = MetadataInfo(
        available=True,
        findings=findings,
    )

    # --------------------------------------------------
    # Technical evidence
    # --------------------------------------------------

    evidence = [
        Evidence(
            source="metadata",
            modality="video",
            type="TECHNICAL_PROPERTIES",
            score=0.0,
            confidence=0.95,
            timestamp=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            explanation=(
                "Technical properties were "
                "successfully extracted from "
                "the video container."
            ),
        )
    ]

    return (
        metadata,
        evidence,
    )