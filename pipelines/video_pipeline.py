from __future__ import annotations

from pathlib import Path

from core.contracts import AnalysisResult, Assessment
from core.trust_score import (
    authenticity_confidence,
    calculate_trust_score,
    risk_level,
)
from services.detection_adapter import convert_video_detection_to_evidence
from services.detection_service import detect_video
from services.video_ingestion import ingest_video_file
from services.video_metadata_analyzer import analyze_video_metadata


def analyze_video(
    video_path: str | Path,
) -> AnalysisResult:
    """
    Run the complete DeepTrace video analysis pipeline.

    Steps:
    1. Ingest and validate the video.
    2. Extract technical properties (resolution, fps, duration) and
       build metadata findings/evidence from them.
    3. Run detection (detect_video() delegates to Hive V3 via
       services/video_service.py — see that file's own size limit,
       MAX_VIDEO_SIZE_MB).
    4. Convert detection results into evidence (raw, unflipped
       scores — see detection_adapter's docstring).
    5. Calculate the Trust Score from the raw detector score.
    6. Determine risk level and classification.
    7. Compute a display-only, label-flipped confidence value.
    8. Return the unified AnalysisResult.

    Note on suspicious segments: core.contracts.AnalysisResult is a
    slots dataclass with a fixed field set (status, file_info,
    assessment, evidence, metadata) — there is no separate
    `suspicious_segments` field to populate, and adding one directly
    as an attribute would raise AttributeError. Hive's per-timestamp
    findings are instead folded into `result.evidence` as individual
    Evidence entries with type="SUSPICIOUS_SEGMENT". The frontend
    reads those out of the evidence list rather than a dedicated key.
    """

    # Step 1: Validate video and collect file information.
    result = ingest_video_file(video_path)

    # Step 2: Extract technical properties and metadata evidence.
    metadata, metadata_evidence = analyze_video_metadata(video_path)

    result.metadata = metadata
    result.evidence.extend(metadata_evidence)

    # Step 3: Run detection (Hive V3, via detection_service.detect_video).
    detection_result = detect_video(video_path)

    # Step 4: Convert detector output into standardized DeepTrace
    # evidence — this includes both the overall verdict and any
    # per-timestamp suspicious segments Hive returned. Evidence
    # scores here are always raw/unflipped.
    detection_evidence = convert_video_detection_to_evidence(
        detection_result
    )

    result.evidence.extend(detection_evidence)

    classification = detection_result["status"].lower()
    detector_score = float(detection_result["score"])

    # Step 5: Calculate Trust Score from the RAW detector score.
    trust_score = calculate_trust_score(
        detector_score,
        classification,
    )

    # Step 6: Determine risk level.
    current_risk = risk_level(trust_score)

    # Step 7: Display-only confidence, flipped for AUTHENTIC so the
    # shown percentage matches the shown label. Never fed back into
    # calculate_trust_score or evidence scoring.
    display_confidence = authenticity_confidence(
        detector_score,
        classification,
    )

    # Step 8: Build the final assessment.
    result.assessment = Assessment(
        classification=classification,
        confidence=display_confidence,
        trust_score=trust_score,
        risk_level=current_risk,
    )

    return result