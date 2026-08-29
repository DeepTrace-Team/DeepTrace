from __future__ import annotations


def calculate_trust_score(
    confidence: float,
    classification: str,
) -> int:
    """
    Convert detector confidence into a DeepTrace Trust Score.

    Authentic:
        confidence 0.10 -> trust 90
        confidence 0.90 -> trust 10

    Manipulated:
        confidence 0.90 -> trust 10
        confidence 0.10 -> trust 90
    """

    confidence = max(0.0, min(1.0, float(confidence)))
    classification = str(classification).lower().strip()

    if classification == "authentic":
        trust_score = (1.0 - confidence) * 100

    elif classification in {"manipulated", "fake", "synthetic"}:
        trust_score = (1.0 - confidence) * 100

    else:
        trust_score = 50

    return max(0, min(100, round(trust_score)))


def risk_level(trust_score: int) -> str:
    """
    Convert Trust Score into DeepTrace risk level.

    67–100 -> LOW
    34–66  -> MEDIUM
    0–33   -> HIGH
    """

    if trust_score >= 67:
        return "LOW"

    if trust_score >= 34:
        return "MEDIUM"

    return "HIGH"
