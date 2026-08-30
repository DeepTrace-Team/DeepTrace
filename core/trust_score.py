from __future__ import annotations


AUTHENTIC_LABELS = {
    "authentic",
    "real",
    "genuine",
}

MANIPULATED_LABELS = {
    "manipulated",
    "fake",
    "synthetic",
    "ai_generated",
}


def calculate_trust_score(
    confidence: float,
    classification: str,
) -> int:
    """
    Convert detector output into a DeepTrace Trust Score.

    Both Reality Defender and Hive V3's scores represent confidence
    that the content IS manipulated — universally, regardless of
    which label was assigned. That's why both branches below use the
    identical formula; there's nothing to special-case per label.

    For AUTHENTIC:
        detector score 0.06
        -> trust score 94

    For MANIPULATED:
        detector score 0.94
        -> trust score 6

    IMPORTANT: pass the RAW detector score here, never the flipped
    authenticity_confidence() value below — that's a display-only
    transform and would double-invert the math if fed in here.
    """

    confidence = max(
        0.0,
        min(1.0, float(confidence)),
    )

    classification = (
        str(classification)
        .lower()
        .strip()
    )

    if classification in AUTHENTIC_LABELS:
        trust_score = (
            1.0 - confidence
        ) * 100

    elif classification in MANIPULATED_LABELS:
        trust_score = (
            1.0 - confidence
        ) * 100

    else:
        trust_score = 50

    return max(
        0,
        min(
            100,
            round(trust_score),
        ),
    )


def risk_level(
    trust_score: int,
) -> str:
    """
    Convert Trust Score into DeepTrace risk level.

    67–100 -> LOW
    34–66  -> MEDIUM
    0–33   -> HIGH
    """

    trust_score = int(trust_score)

    if trust_score >= 67:
        return "LOW"

    if trust_score >= 34:
        return "MEDIUM"

    return "HIGH"


def authenticity_confidence(
    score: float,
    classification: str,
) -> float:
    """
    Convert a detector's manipulation-probability score into a
    "confidence in the displayed label" value, for UI display only.

    Detector scores (Reality Defender, Hive V3) represent confidence
    the content IS manipulated, regardless of the assigned label —
    see calculate_trust_score's docstring for the worked examples
    that establish this. Shown raw, that reads backwards next to an
    AUTHENTIC verdict (e.g. "6% confidence" for a genuinely
    trustworthy result). This flips it for AUTHENTIC only, so the
    displayed percentage matches the displayed label:

        AUTHENTIC,   score 0.06 -> 0.94 ("94% confidence")
        MANIPULATED, score 0.94 -> 0.94 ("94% confidence")

    This is a DISPLAY-ONLY transform. Evidence suspicion scores and
    calculate_trust_score() must both keep using the raw, unflipped
    score — feeding this function's output into either would
    double-invert the math.
    """

    score = max(
        0.0,
        min(1.0, float(score)),
    )

    classification = (
        str(classification)
        .lower()
        .strip()
    )

    if classification in AUTHENTIC_LABELS:
        return 1.0 - score

    return score