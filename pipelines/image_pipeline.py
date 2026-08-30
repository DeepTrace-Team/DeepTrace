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
    convert_detection_to_evidence,
)

from services.detection_service import (
    detect_image,
)

from services.image_ingestion import (
    ingest_image_file,
)

from services.metadata_analyzer import (
    analyze_image_metadata,
)

from utils.preprocessing import (
    preprocess_image,
)


def analyze_image(
    image_path: str | Path,
) -> AnalysisResult:

    # --------------------------------------------------
    # 1. INGEST
    # --------------------------------------------------

    result = ingest_image_file(
        image_path
    )

    # --------------------------------------------------
    # 2. PREPROCESS
    # --------------------------------------------------

    preprocess_image(
        image_path
    )

    # --------------------------------------------------
    # 3. METADATA
    # --------------------------------------------------

    metadata, metadata_evidence = (
        analyze_image_metadata(
            image_path
        )
    )

    result.metadata = metadata

    result.evidence.extend(
        metadata_evidence
    )

    # --------------------------------------------------
    # 4. REALITY DEFENDER
    # --------------------------------------------------

    detection_result = detect_image(
        image_path
    )

    # --------------------------------------------------
    # 5. DETECTION EVIDENCE
    #
    # convert_detection_to_evidence() uses the raw, unflipped
    # detector score for every evidence entry — see that
    # function's docstring for why.
    # --------------------------------------------------

    detection_evidence = (
        convert_detection_to_evidence(
            detection_result,
            modality="image",
        )
    )

    result.evidence.extend(
        detection_evidence
    )

    # --------------------------------------------------
    # 6. CLASSIFICATION
    # --------------------------------------------------

    classification = str(
        detection_result.get(
            "status",
            "unknown",
        )
    ).lower().strip()

    detector_score = float(
        detection_result.get(
            "score",
            0.0,
        )
    )

    # --------------------------------------------------
    # 7. TRUST SCORE
    #
    # Uses the RAW detector_score, never the flipped display
    # confidence below — see calculate_trust_score's docstring.
    # --------------------------------------------------

    trust_score = calculate_trust_score(
        detector_score,
        classification,
    )

    # --------------------------------------------------
    # 8. RISK
    # --------------------------------------------------

    current_risk = risk_level(
        trust_score
    )

    # --------------------------------------------------
    # 9. DISPLAY CONFIDENCE
    #
    # Flipped for AUTHENTIC so the shown percentage matches the
    # shown label — display-only, see authenticity_confidence's
    # docstring. Never fed into calculate_trust_score.
    # --------------------------------------------------

    display_confidence = (
        authenticity_confidence(
            detector_score,
            classification,
        )
    )

    # --------------------------------------------------
    # 10. ASSESSMENT
    # --------------------------------------------------

    result.assessment = Assessment(
        classification=classification,
        confidence=display_confidence,
        trust_score=trust_score,
        risk_level=current_risk,
    )

    return result