from __future__ import annotations

from typing import Any

from core.contracts import Evidence
from core.evidence_engine import create_evidence


AUTHENTIC_STATUSES = {
    "AUTHENTIC",
    "REAL",
    "GENUINE",
}

MANIPULATED_STATUSES = {
    "MANIPULATED",
    "FAKE",
    "SYNTHETIC",
    "AI_GENERATED",
}


def _normalize_score(
    value: Any,
) -> float | None:

    if value is None:
        return None

    try:

        score = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return None

    return max(
        0.0,
        min(
            1.0,
            score,
        ),
    )


def _format_reasons(
    reasons: list[Any],
) -> str:

    if not reasons:
        return ""

    formatted = []

    for reason in reasons:

        if isinstance(
            reason,
            dict,
        ):

            message = (
                reason.get(
                    "message"
                )
                or reason.get(
                    "code"
                )
            )

            if message:
                formatted.append(
                    str(message)
                )

        elif reason:

            formatted.append(
                str(reason)
            )

    if not formatted:
        return ""

    return (
        " Reasons: "
        + "; ".join(
            formatted
        )
        + "."
    )


def convert_detection_to_evidence(
    result: dict[str, Any],
    modality: str = "image",
) -> list[Evidence]:
    """
    Convert a detector's raw result into standardized DeepTrace
    Evidence objects.

    IMPORTANT — evidence scores are ALWAYS the raw, unflipped
    detector score, for every provider (Reality Defender, Hive V3)
    and every label. Both providers' scores already mean "confidence
    this is manipulated," regardless of the assigned status — see
    core.trust_score.calculate_trust_score's docstring for the
    worked examples that establish this. There is no flip here.
    (A label-aware flip IS correct in exactly one other place —
    core.trust_score.authenticity_confidence, for the assessment
    card's display-only "Confidence: X%" text — but that must never
    be applied to evidence scores or fed back into
    calculate_trust_score.)
    """

    if not isinstance(
        result,
        dict,
    ):

        raise TypeError(
            "Detection result must be a dictionary."
        )

    media_label = {
        "image": "image",
        "video": "video",
        "audio": "audio file",
    }.get(
        modality,
        "media",
    )

    provider = result.get(
        "provider",
        "Reality Defender",
    )

    evidence = []

    # ========================================================
    # OVERALL DETECTION
    # ========================================================

    status = str(
        result.get(
            "status",
            "",
        )
    ).upper().strip()

    detector_score = _normalize_score(
        result.get(
            "score"
        )
    )

    # --------------------------------------------------------
    # NORMAL SCORED RESULT
    # --------------------------------------------------------

    if (
        status
        and detector_score is not None
    ):

        explanation = result.get(
            "explanation"
        )

        if not explanation:

            explanation = (
                f"{provider} classified the "
                f"{media_label} as "
                f"{status} with a detector "
                f"score of "
                f"{detector_score:.2f}."
            )

        evidence.append(
            create_evidence(
                source=provider,
                modality=modality,
                evidence_type="AI_DETECTION",
                score=detector_score,
                confidence=0.95,
                explanation=str(
                    explanation
                ),
            )
        )

    # --------------------------------------------------------
    # NOT APPLICABLE
    #
    # IMPORTANT:
    # Do NOT create a fake numeric score.
    # --------------------------------------------------------

    elif status == "NOT_APPLICABLE":

        reasons_text = _format_reasons(
            result.get(
                "reasons",
                [],
            )
        )

        explanation = (
            f"{provider} could not reliably "
            f"evaluate the {media_label}."
            f"{reasons_text}"
        )

        evidence.append(
            create_evidence(
                source=provider,
                modality=modality,
                evidence_type="AI_DETECTION",
                score=0.0,
                confidence=0.0,
                explanation=explanation,
            )
        )

    # --------------------------------------------------------
    # UNABLE TO EVALUATE
    # --------------------------------------------------------

    elif status == "UNABLE_TO_EVALUATE":

        evidence.append(
            create_evidence(
                source=provider,
                modality=modality,
                evidence_type="AI_DETECTION",
                score=0.0,
                confidence=0.0,
                explanation=(
                    f"{provider} was unable to "
                    f"evaluate the {media_label}. "
                    "No authenticity score was generated."
                ),
            )
        )

    # ========================================================
    # INDIVIDUAL MODEL RESULTS
    # ========================================================

    models = result.get(
        "models",
        [],
    )

    if not isinstance(
        models,
        list,
    ):

        models = []

    for model in models:

        if not isinstance(
            model,
            dict,
        ):

            continue

        model_status = str(
            model.get(
                "status",
                "",
            )
        ).upper().strip()

        model_score = _normalize_score(
            model.get(
                "score"
            )
        )

        # ----------------------------------------------------
        # Ignore models without usable scores.
        # ----------------------------------------------------

        if (
            not model_status
            or model_score is None
            or model_status == "NOT_APPLICABLE"
        ):

            continue

        model_name = str(
            model.get(
                "name",
                "unknown",
            )
        ).strip()

        timestamp = model.get(
            "timestamp"
        )

        explanation = (
            f"{provider} model "
            f"{model_name} classified "
            f"the {media_label} as "
            f"{model_status} with a "
            f"detector score of "
            f"{model_score:.2f}."
        )

        if timestamp is not None:

            explanation += (
                f" Timestamp: "
                f"{timestamp}s."
            )

        evidence.append(
            create_evidence(
                source=provider,
                modality=modality,
                evidence_type="MODEL_DETECTION",
                score=model_score,
                confidence=0.95,
                explanation=explanation,
            )
        )

    # ========================================================
    # VIDEO SUSPICIOUS SEGMENTS (Hive-specific)
    #
    # timestamp is folded into the explanation text rather than
    # passed as a separate keyword to create_evidence(), since
    # create_evidence() (core/evidence_engine.py) doesn't accept
    # a timestamp override — it always auto-generates one.
    # ========================================================

    suspicious_segments = result.get(
        "suspicious_segments",
        [],
    )

    if isinstance(
        suspicious_segments,
        list,
    ):

        for segment in suspicious_segments:

            if not isinstance(
                segment,
                dict,
            ):
                continue

            timestamp = segment.get(
                "timestamp"
            )

            segment_score = _normalize_score(
                segment.get(
                    "score"
                )
            )

            if segment_score is None:
                continue

            severity = str(
                segment.get(
                    "severity",
                    "MEDIUM",
                )
            ).upper()

            explanation = (
                f"{provider} identified a "
                f"suspicious region in the "
                f"video at "
                f"{timestamp}s with a "
                f"suspicion score of "
                f"{segment_score:.2f}. "
                f"Severity: {severity}."
            )

            evidence.append(
                create_evidence(
                    source=provider,
                    modality=modality,
                    evidence_type="SUSPICIOUS_SEGMENT",
                    score=segment_score,
                    confidence=0.90,
                    explanation=explanation,
                )
            )

    return evidence


def convert_video_detection_to_evidence(
    result: dict[str, Any],
) -> list[Evidence]:

    return convert_detection_to_evidence(
        result,
        modality="video",
    )


def convert_audio_detection_to_evidence(
    result: dict[str, Any],
) -> list[Evidence]:

    return convert_detection_to_evidence(
        result,
        modality="audio",
    )