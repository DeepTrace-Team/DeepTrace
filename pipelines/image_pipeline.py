from __future__ import annotations

from pathlib import Path

from core.contracts import AnalysisResult, Assessment
from core.trust_score import calculate_trust_score, risk_level
from services.detection_adapter import convert_detection_to_evidence
from services.detection_service import detect_image
from services.image_ingestion import ingest_image_file
from services.metadata_analyzer import analyze_image_metadata
from utils.preprocessing import preprocess_image


def analyze_image(
    image_path: str | Path,
) -> AnalysisResult:
    """
    Run the complete DeepTrace image analysis pipeline.

    Steps:
    1. Ingest and validate the image.
    2. Preprocess the image.
    3. Analyze image metadata.
    4. Run Reality Defender detection.
    5. Convert detection results into evidence.
    6. Calculate the Trust Score.
    7. Determine risk level and classification.
    8. Return the unified AnalysisResult.
    """

    # Step 1: Validate image and collect file information.
    result = ingest_image_file(image_path)

    # Step 2: Preprocess the image.
    preprocess_image(image_path)

    # Step 3: Analyze metadata.
    metadata, metadata_evidence = analyze_image_metadata(image_path)

    result.metadata = metadata
    result.evidence.extend(metadata_evidence)

    # Step 4: Run Reality Defender.
    detection_result = detect_image(image_path)

    # Step 5: Convert Reality Defender output into
    # standardized DeepTrace evidence.
    detection_evidence = convert_detection_to_evidence(
        detection_result
    )

    result.evidence.extend(detection_evidence)

    # Step 6: Calculate Trust Score using
    # Reality Defender's detector confidence.
    classification = detection_result["status"].lower()
    detector_score = float(detection_result["score"])

    trust_score = calculate_trust_score(
        detector_score,
        classification,
    )

    # Step 7: Determine risk level.
    current_risk = risk_level(trust_score)

    # Step 8: Build the final assessment.
    result.assessment = Assessment(
        classification=classification,
        confidence=detector_score,
        trust_score=trust_score,
        risk_level=current_risk,
    )

    return result
