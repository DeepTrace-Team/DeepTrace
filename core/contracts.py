from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _validate_score(value: float, name: str) -> float:
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0.")
    return float(value)


def _validate_trust_score(value: int) -> int:
    if not 0 <= int(value) <= 100:
        raise ValueError("trust_score must be between 0 and 100.")
    return int(value)


@dataclass(slots=True)
class Evidence:
    source: str
    modality: str
    type: str
    score: float
    confidence: float
    timestamp: str
    explanation: str

    def __post_init__(self) -> None:
        self.score = _validate_score(self.score, "score")
        self.confidence = _validate_score(self.confidence, "confidence")


@dataclass(slots=True)
class FileInfo:
    filename: str
    file_type: str
    size: int


@dataclass(slots=True)
class Assessment:
    classification: str
    confidence: float
    trust_score: int
    risk_level: str

    def __post_init__(self) -> None:
        self.confidence = _validate_score(self.confidence, "confidence")
        self.trust_score = _validate_trust_score(self.trust_score)


@dataclass(slots=True)
class MetadataInfo:
    available: bool
    findings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AnalysisResult:
    status: str
    file_info: FileInfo
    assessment: Assessment
    evidence: list[Evidence] = field(default_factory=list)
    metadata: MetadataInfo = field(default_factory=MetadataInfo)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["file_info"] = asdict(self.file_info)
        payload["assessment"] = asdict(self.assessment)
        payload["metadata"] = asdict(self.metadata)
        payload["evidence"] = [asdict(item) for item in self.evidence]
        return payload
