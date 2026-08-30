from __future__ import annotations

from pathlib import Path

from core.contracts import (
    AnalysisResult,
    Assessment,
    FileInfo,
    MetadataInfo,
)
from utils.file_utils import (
    safe_file_info,
    validate_video_path,
)


def ingest_video_file(
    video_path: str | Path,
) -> AnalysisResult:
    """
    Validate a video file and create the initial
    DeepTrace AnalysisResult.
    """

    # --------------------------------------------------
    # Validate input
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

    if str(video_path).strip() == "":
        raise ValueError(
            "video_path cannot be empty."
        )

    path = Path(
        video_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    # --------------------------------------------------
    # Validate video format
    # --------------------------------------------------

    is_valid, error = validate_video_path(
        path
    )

    if not is_valid:
        raise ValueError(
            error or "Unsupported video file."
        )

    # --------------------------------------------------
    # Extract basic file information
    # --------------------------------------------------

    info = safe_file_info(
        path
    )

    # --------------------------------------------------
    # Create initial result
    # --------------------------------------------------

    result = AnalysisResult(
        status="success",

        file_info=FileInfo(
            filename=info["filename"],
            file_type=info["file_type"],
            size=int(
                info["size"]
            ),
        ),

        assessment=Assessment(
            classification="unknown",
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        ),

        evidence=[],

        metadata=MetadataInfo(
            available=False,
            findings=[],
        ),
    )

    return result