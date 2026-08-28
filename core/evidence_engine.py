from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from core.contracts import Evidence


def create_evidence(
    *,
    source: str,
    modality: str,
    evidence_type: str,
    score: float,
    confidence: float,
    explanation: str,
) -> Evidence:
    """
    Create a normalized Evidence object.

    All detector outputs should pass through this function
    before being added to the Evidence Engine.
    """

    if not source.strip():
        raise ValueError("source cannot be empty.")

    if not modality.strip():
        raise ValueError("modality cannot be empty.")

    if not evidence_type.strip():
        raise ValueError("evidence_type cannot be empty.")

    if not explanation.strip():
        raise ValueError("explanation cannot be empty.")

    return Evidence(
        source=source,
        modality=modality,
        type=evidence_type,
        score=score,
        confidence=confidence,
        timestamp=datetime.now(timezone.utc).isoformat(),
        explanation=explanation,
    )


def collect_evidence(
    evidence_items: Iterable[Evidence],
) -> list[Evidence]:
    """
    Collect and normalize Evidence objects into a list.
    """

    if evidence_items is None:
        raise TypeError("evidence_items cannot be None.")

    evidence = list(evidence_items)

    for item in evidence:
        if not isinstance(item, Evidence):
            raise TypeError(
                "All evidence items must be Evidence objects."
            )

    return evidence


def calculate_evidence_score(
    evidence_items: Iterable[Evidence],
) -> float:
    """
    Calculate a weighted average evidence score.

    Evidence confidence is used as the weight.
    Returns 0.0 when no evidence is available.
    """

    evidence = collect_evidence(evidence_items)

    if not evidence:
        return 0.0

    total_weight = sum(item.confidence for item in evidence)

    if total_weight == 0:
        return 0.0

    weighted_score = sum(
        item.score * item.confidence
        for item in evidence
    )

    return weighted_score / total_weight
