from __future__ import annotations

import pytest

from core.contracts import AnalysisResult, Assessment, Evidence, FileInfo, MetadataInfo


def test_valid_contract_construction() -> None:
    evidence = Evidence(
        source="metadata",
        modality="image",
        type="EXIF",
        score=0.82,
        confidence=0.91,
        timestamp="2026-08-27T00:00:00Z",
        explanation="Image metadata was parsed successfully.",
    )

    result = AnalysisResult(
        status="success",
        file_info=FileInfo(filename="sample.png", file_type="image/png", size=2048),
        assessment=Assessment(
            classification="unknown",
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        ),
        evidence=[evidence],
        metadata=MetadataInfo(available=False, findings=[]),
    )

    assert result.status == "success"
    assert result.file_info.filename == "sample.png"
    assert result.file_info.file_type == "image/png"
    assert result.assessment.trust_score == 0
    assert result.evidence[0].source == "metadata"


def test_contract_serialization() -> None:
    result = AnalysisResult(
        status="success",
        file_info=FileInfo(filename="example.jpg", file_type="image/jpeg", size=4096),
        assessment=Assessment(
            classification="unknown",
            confidence=0.0,
            trust_score=0,
            risk_level="unknown",
        ),
        evidence=[],
        metadata=MetadataInfo(available=True, findings=["EXIF present"]),
    )

    payload = result.to_dict()

    assert payload["status"] == "success"
    assert payload["file_info"]["filename"] == "example.jpg"
    assert payload["metadata"]["available"] is True
    assert payload["metadata"]["findings"] == ["EXIF present"]


def test_evidence_structure() -> None:
    evidence = Evidence(
        source="artifact",
        modality="image",
        type="compression",
        score=0.45,
        confidence=0.68,
        timestamp="2026-08-27T01:00:00Z",
        explanation="Possible editing artifact detected.",
    )

    assert evidence.source == "artifact"
    assert evidence.modality == "image"
    assert evidence.type == "compression"
    assert evidence.score == 0.45
    assert evidence.confidence == 0.68


def test_invalid_assessment_values_raise() -> None:
    with pytest.raises(ValueError):
        Assessment(
            classification="unknown",
            confidence=1.5,
            trust_score=0,
            risk_level="unknown",
        )

    with pytest.raises(ValueError):
        Assessment(
            classification="unknown",
            confidence=0.0,
            trust_score=101,
            risk_level="unknown",
        )


def test_invalid_evidence_values_raise() -> None:
    with pytest.raises(ValueError):
        Evidence(
            source="metadata",
            modality="image",
            type="EXIF",
            score=1.5,
            confidence=0.5,
            timestamp="2026-08-27T00:00:00Z",
            explanation="bad score",
        )

    with pytest.raises(ValueError):
        Evidence(
            source="metadata",
            modality="image",
            type="EXIF",
            score=0.5,
            confidence=-0.1,
            timestamp="2026-08-27T00:00:00Z",
            explanation="bad confidence",
        )
