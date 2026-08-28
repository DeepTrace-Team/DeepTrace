from core.contracts import Evidence
from core.evidence_engine import (
    calculate_evidence_score,
    collect_evidence,
    create_evidence,
)


def test_create_evidence() -> None:
    evidence = create_evidence(
        source="test_detector",
        modality="image",
        evidence_type="AI_DETECTION",
        score=0.91,
        confidence=0.95,
        explanation="Image shows strong AI-generation indicators.",
    )

    assert isinstance(evidence, Evidence)
    assert evidence.source == "test_detector"
    assert evidence.modality == "image"
    assert evidence.type == "AI_DETECTION"
    assert evidence.score == 0.91
    assert evidence.confidence == 0.95
    assert evidence.timestamp
    assert evidence.explanation


def test_create_evidence_rejects_empty_source() -> None:
    try:
        create_evidence(
            source="",
            modality="image",
            evidence_type="AI_DETECTION",
            score=0.9,
            confidence=0.9,
            explanation="Test",
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_collect_evidence() -> None:
    first = create_evidence(
        source="detector_1",
        modality="image",
        evidence_type="AI_DETECTION",
        score=0.9,
        confidence=0.8,
        explanation="Detector result.",
    )

    second = create_evidence(
        source="metadata",
        modality="image",
        evidence_type="EXIF",
        score=0.4,
        confidence=0.5,
        explanation="Metadata finding.",
    )

    result = collect_evidence([first, second])

    assert len(result) == 2
    assert result[0] is first
    assert result[1] is second


def test_collect_evidence_rejects_invalid_item() -> None:
    try:
        collect_evidence(["invalid"])
    except TypeError:
        return

    raise AssertionError("Expected TypeError")


def test_calculate_evidence_score() -> None:
    first = Evidence(
        source="detector_1",
        modality="image",
        type="AI_DETECTION",
        score=0.9,
        confidence=0.8,
        timestamp="2026-01-01T00:00:00+00:00",
        explanation="Detector result.",
    )

    second = Evidence(
        source="detector_2",
        modality="image",
        type="AI_DETECTION",
        score=0.5,
        confidence=0.2,
        timestamp="2026-01-01T00:00:00+00:00",
        explanation="Second detector result.",
    )

    score = calculate_evidence_score([first, second])

    expected = (0.9 * 0.8 + 0.5 * 0.2) / (0.8 + 0.2)

    assert abs(score - expected) < 1e-9


def test_calculate_evidence_score_empty() -> None:
    assert calculate_evidence_score([]) == 0.0
def test_create_evidence_rejects_empty_modality() -> None:
    try:
        create_evidence(
            source="test_detector",
            modality="",
            evidence_type="AI_DETECTION",
            score=0.9,
            confidence=0.9,
            explanation="Test",
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_create_evidence_rejects_empty_evidence_type() -> None:
    try:
        create_evidence(
            source="test_detector",
            modality="image",
            evidence_type="",
            score=0.9,
            confidence=0.9,
            explanation="Test",
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_create_evidence_rejects_empty_explanation() -> None:
    try:
        create_evidence(
            source="test_detector",
            modality="image",
            evidence_type="AI_DETECTION",
            score=0.9,
            confidence=0.9,
            explanation="",
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_collect_evidence_rejects_none() -> None:
    try:
        collect_evidence(None)
    except TypeError:
        return

    raise AssertionError("Expected TypeError")


def test_calculate_evidence_score_zero_confidence() -> None:
    evidence = Evidence(
        source="test_detector",
        modality="image",
        type="AI_DETECTION",
        score=0.9,
        confidence=0.0,
        timestamp="2026-01-01T00:00:00+00:00",
        explanation="Test evidence.",
    )

    assert calculate_evidence_score([evidence]) == 0.0
