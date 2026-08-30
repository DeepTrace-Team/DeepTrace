from __future__ import annotations

from pathlib import Path

from core.contracts import AnalysisResult, Assessment, FileInfo, MetadataInfo
from utils.file_utils import safe_file_info, validate_audio_path


def ingest_audio_file(audio_path: str | Path) -> AnalysisResult:
    if audio_path is None:
        raise TypeError("audio_path cannot be None.")

    if not isinstance(audio_path, (str, Path)):
        raise TypeError("audio_path must be a string or pathlib.Path.")

    if str(audio_path).strip() == "":
        raise ValueError("audio_path cannot be empty.")

    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    is_valid, error = validate_audio_path(path)
    if not is_valid:
        raise ValueError(error or "Unsupported audio file.")

    info = safe_file_info(path)

    result = AnalysisResult(
        status="success",
        file_info=FileInfo(
            filename=info["filename"],
            file_type=info["file_type"],
            size=int(info["size"]),
        ),
        assessment=Assessment(
            classification="unknown",
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        ),
        evidence=[],
        metadata=MetadataInfo(available=False, findings=[]),
    )

    return result