from __future__ import annotations

from typing import Any

from core.contracts import Evidence
from core.evidence_engine import create_evidence


AUTHENTIC_STATUSES = {"AUTHENTIC", "REAL", "GENUINE"}
MANIPULATED_STATUSES = {
    "MANIPULATED",
    "FAKE",
    "SYNTHETIC",
    "AI_GENERATED",
}


def _normalize_score(value: Any) -> float | None:
    """Safely convert a detector score to a value between 0 and 1."""

    if value is None:
        return None

    try:
        score = float(value)
    except (TypeError, ValueError):
        return None

    if not 0.0 <= score <= 1.0:
        return max(0.0, min(1.0, score))

    return score


def _to_suspicion_score(
    score: float,
    status: str,
) -> float:
    """
    Convert Reality Defender's score into DeepTrace suspicion.

    DeepTrace:
        0.0 = no suspicion
        1.0 = maximum suspicion
    """

    if status in AUTHENTIC_STATUSES:
        return 1.0 - score

    return score


def convert_detection_to_evidence(
    result: dict[str, Any],
) -> list[Evidence]:
    """
    Convert Reality Defender detection results into
    standardized DeepTrace Evidence objects.
    """

    if not isinstance(result, dict):
        raise TypeError("Detection result must be a dictionary.")

    evidence: list[Evidence] = []

    # ---------------------------------------------------------
    # Overall detector result
    # ---------------------------------------------------------

    status = str(result.get("status", "")).upper().strip()
    detector_score = _normalize_score(result.get("score"))

    if status and detector_score is not None:
        suspicion_score = _to_suspicion_score(
            detector_score,
            status,
        )

        evidence.append(
            create_evidence(
                source="Reality Defender",
                modality="image",
                evidence_type="AI_DETECTION",
                score=suspicion_score,
                confidence=0.95,
                explanation=(
                    "Reality Defender classified the image as "
                    f"{status} with a detector score of "
                    f"{detector_score:.2f}."
                ),
            )
        )

    # ---------------------------------------------------------
    # Individual model results
    # ---------------------------------------------------------

    models = result.get("models", [])

    if not isinstance(models, list):
        models = []

    for model in models:
        if not isinstance(model, dict):
            continue

        model_status = str(
            model.get("status", "")
        ).upper().strip()

        model_score = _normalize_score(
            model.get("score")
        )

        # Ignore models that have not produced a score yet.
        if not model_status or model_score is None:
            continue

        suspicion_score = _to_suspicion_score(
            model_score,
            model_status,
        )

        model_name = str(
            model.get("name", "unknown")
        ).strip()

        evidence.append(
            create_evidence(
                source="Reality Defender",
                modality="image",
                evidence_type="MODEL_DETECTION",
                score=suspicion_score,
                confidence=0.95,
                explanation=(
                    "Reality Defender model "
                    f"{model_name} classified the image as "
                    f"{model_status} with a detector score of "
                    f"{model_score:.2f}."
                ),
            )
        )

    return evidence
