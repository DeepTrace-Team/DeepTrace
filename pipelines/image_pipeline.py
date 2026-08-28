from __future__ import annotations

from pathlib import Path

from core.contracts import AnalysisResult, Assessment
from services.image_ingestion import ingest_image_file
from services.metadata_analyzer import analyze_image_metadata
from utils.preprocessing import preprocess_image


def analyze_image(
    image_path: str | Path,
) -> AnalysisResult:
    """
    Run the complete image analysis pipeline.

    Steps:
    1. Ingest and validate the image.
    2. Preprocess the image.
    3. Analyze image metadata.
    4. Attach metadata evidence to the result.
    5. Return the unified AnalysisResult.

    The actual AI/forensic detection models will be
    added in later pipeline stages.
    """

    # Step 1: Validate image and collect file information.
    result = ingest_image_file(image_path)

    # Step 2: Preprocess the image.
    # The processed image will be used by future
    # AI/forensic detection modules.
    preprocess_image(image_path)

    # Step 3: Analyze metadata.
    metadata, metadata_evidence = analyze_image_metadata(image_path)

    # Step 4: Attach metadata results.
    result.metadata = metadata
    result.evidence.extend(metadata_evidence)

    # Step 5: Keep the assessment as "unknown" until
    # actual forensic detectors are integrated.
    result.assessment = Assessment(
        classification="unknown",
        confidence=0.0,
        trust_score=0,
        risk_level="unknown",
    )

    return result
