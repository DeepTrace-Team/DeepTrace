from __future__ import annotations

from pathlib import Path

from core.contracts import (
    AnalysisResult,
    Assessment,
)

from core.trust_score import (
    authenticity_confidence,
    calculate_trust_score,
    risk_level,
)

from services.detection_adapter import (
    convert_audio_detection_to_evidence,
)

from services.detection_service import (
    detect_audio,
)

from services.audio_ingestion import (
    ingest_audio_file,
)

from services.audio_metadata_analyzer import (
    analyze_audio_metadata,
)


# ============================================================
# AUDIO ANALYSIS PIPELINE
# ============================================================

def analyze_audio(
    audio_path: str | Path,
) -> AnalysisResult:

    """
    Complete DeepTrace audio analysis pipeline.

    Pipeline:

        Audio file
             ↓
        Validation
             ↓
        Technical metadata
             ↓
        Reality Defender
             ↓
        API verdict
             ↓
        Trust score / assessment
             ↓
        AnalysisResult

    IMPORTANT:

    Reality Defender can legitimately return:

        AUTHENTIC
        MANIPULATED / FAKE
        NOT_APPLICABLE
        UNABLE_TO_EVALUATE

    NOT_APPLICABLE and UNABLE_TO_EVALUATE do NOT have a
    trustworthy numeric authenticity score.

    DeepTrace therefore does NOT fabricate a score for these
    cases.
    """

    # ========================================================
    # STEP 1
    # INGEST AUDIO
    # ========================================================

    result = ingest_audio_file(
        audio_path
    )

    # ========================================================
    # STEP 2
    # TECHNICAL METADATA
    # ========================================================

    metadata, metadata_evidence = (
        analyze_audio_metadata(
            audio_path
        )
    )

    result.metadata = metadata

    result.evidence.extend(
        metadata_evidence
    )

    # ========================================================
    # STEP 3
    # REALITY DEFENDER
    # ========================================================

    detection_result = detect_audio(
        audio_path
    )

    # ========================================================
    # STEP 4
    # CONVERT API RESPONSE → EVIDENCE
    # ========================================================

    detection_evidence = (
        convert_audio_detection_to_evidence(
            detection_result
        )
    )

    result.evidence.extend(
        detection_evidence
    )

    # ========================================================
    # STEP 5
    # READ API VERDICT
    # ========================================================

    classification = str(
        detection_result.get(
            "status",
            "UNKNOWN",
        )
    ).upper().strip()

    raw_score = detection_result.get(
        "score"
    )

    # ========================================================
    # CASE A:
    # NOT APPLICABLE
    # ========================================================

    if classification == "NOT_APPLICABLE":

        result.assessment = Assessment(
            classification="NOT_APPLICABLE",
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        )

        return result

    # ========================================================
    # CASE B:
    # UNABLE TO EVALUATE
    # ========================================================

    if classification == "UNABLE_TO_EVALUATE":

        result.assessment = Assessment(
            classification="UNABLE_TO_EVALUATE",
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        )

        return result

    # ========================================================
    # CASE C:
    # NO SCORE
    #
    # This should never be silently converted into 0.
    # ========================================================

    if raw_score is None:

        result.assessment = Assessment(
            classification=(
                classification
                or "UNKNOWN"
            ),
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        )

        return result

    # ========================================================
    # NORMAL SCORED RESULT
    # ========================================================

    try:

        detector_score = float(
            raw_score
        )

    except (
        TypeError,
        ValueError,
    ):

        result.assessment = Assessment(
            classification=(
                classification
                or "UNKNOWN"
            ),
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        )

        return result

    # Clamp API score to valid range.

    detector_score = max(
        0.0,
        min(
            1.0,
            detector_score,
        ),
    )

    # ========================================================
    # STEP 6
    # TRUST SCORE
    # ========================================================

    trust_score = calculate_trust_score(
        detector_score,
        classification,
    )

    # ========================================================
    # STEP 7
    # RISK LEVEL
    # ========================================================

    current_risk = risk_level(
        trust_score
    )

    # ========================================================
    # STEP 8
    # DISPLAY CONFIDENCE
    # ========================================================

    display_confidence = (
        authenticity_confidence(
            detector_score,
            classification,
        )
    )

    # ========================================================
    # STEP 9
    # FINAL ASSESSMENT
    # ========================================================

    result.assessment = Assessment(
        classification=classification,
        confidence=display_confidence,
        trust_score=trust_score,
        risk_level=current_risk,
    )

    return result