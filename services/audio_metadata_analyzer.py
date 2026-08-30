from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from core.contracts import (
    Evidence,
    MetadataInfo,
)

from utils.preprocessing import (
    preprocess_audio,
)


def analyze_audio_metadata(
    audio_path: str | Path,
) -> tuple[
    MetadataInfo,
    list[Evidence],
]:

    """
    Extract technical properties from an audio file.

    Metadata is informational only.

    It is NOT treated as evidence that the audio is fake.
    """

    properties = preprocess_audio(
        audio_path
    )

    duration = properties.get(
        "duration_seconds"
    )

    bitrate = properties.get(
        "bitrate"
    )

    channels = properties.get(
        "channels"
    )

    sample_rate = properties.get(
        "sample_rate"
    )

    findings = [

        f"Duration: "
        f"{duration if duration is not None else 'unknown'}s",

        f"Bitrate: "
        f"{bitrate if bitrate is not None else 'unknown'}",

        f"Channels: "
        f"{channels if channels is not None else 'unknown'}",

        f"Sample rate: "
        f"{sample_rate if sample_rate is not None else 'unknown'}",
    ]

    metadata = MetadataInfo(
        available=True,
        findings=findings,
    )

    evidence = [

        Evidence(
            source="metadata",
            modality="audio",
            type="TECHNICAL_PROPERTIES",
            score=0.0,
            confidence=0.95,
            timestamp=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            explanation=(
                "Technical audio properties "
                "were extracted from the file "
                "container. These properties are "
                "informational and are not used "
                "alone to determine authenticity."
            ),
        )

    ]

    return (
        metadata,
        evidence,
    )