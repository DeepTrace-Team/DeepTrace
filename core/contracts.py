from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from typing import Any


# ============================================================
# VALIDATION
# ============================================================

def _validate_score(
    value: float,
    name: str,
) -> float:

    value = float(value)

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"{name} must be between 0.0 and 1.0."
        )

    return value


def _validate_trust_score(
    value: int,
) -> int:

    value = int(value)

    if not 0 <= value <= 100:
        raise ValueError(
            "trust_score must be between 0 and 100."
        )

    return value


# ============================================================
# EVIDENCE
# ============================================================

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

        self.score = _validate_score(
            self.score,
            "score",
        )

        self.confidence = _validate_score(
            self.confidence,
            "confidence",
        )


# ============================================================
# FILE INFO
# ============================================================

@dataclass(slots=True)
class FileInfo:

    filename: str
    file_type: str
    size: int


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(slots=True)
class Assessment:

    classification: str
    confidence: float
    trust_score: int
    risk_level: str

    def __post_init__(self) -> None:

        self.confidence = _validate_score(
            self.confidence,
            "confidence",
        )

        self.trust_score = _validate_trust_score(
            self.trust_score
        )


# ============================================================
# METADATA
# ============================================================

@dataclass(slots=True)
class MetadataInfo:

    available: bool

    findings: list[str] = field(
        default_factory=list
    )


# ============================================================
# ANALYSIS RESULT
# ============================================================

@dataclass(slots=True)
class AnalysisResult:

    status: str

    file_info: FileInfo

    assessment: Assessment

    evidence: list[Evidence] = field(
        default_factory=list
    )

    metadata: MetadataInfo = field(
        default_factory=lambda:
            MetadataInfo(
                available=False
            )
    )

    # --------------------------------------------------------
    # Video-specific information
    # --------------------------------------------------------

    suspicious_segments: list[dict[str, Any]] = field(
        default_factory=list
    )

    video_metrics: dict[str, Any] = field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # Audio-specific information
    # --------------------------------------------------------

    suspicious_ranges: list[tuple] = field(
        default_factory=list
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        payload = asdict(
            self
        )

        return payload
