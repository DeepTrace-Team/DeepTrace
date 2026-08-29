from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from core.contracts import Evidence, MetadataInfo


def analyze_image_metadata(
    image_path: str | Path,
) -> tuple[MetadataInfo, list[Evidence]]:
    """
    Analyze an image for available EXIF metadata.

    Returns:
        A MetadataInfo object and a list of forensic Evidence objects.

    Raises:
        TypeError: If image_path is not a string or Path.
        ValueError: If image_path is empty, invalid, or cannot be analyzed.
        FileNotFoundError: If the image does not exist.
    """

    if image_path is None:
        raise TypeError("image_path cannot be None.")

    if not isinstance(image_path, (str, Path)):
        raise TypeError("image_path must be a string or pathlib.Path.")

    if str(image_path).strip() == "":
        raise ValueError("image_path cannot be empty.")

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    try:
        with Image.open(path) as image:
            exif = image.getexif()

            findings: list[str] = []
            evidence: list[Evidence] = []

            if not exif:
                metadata = MetadataInfo(
                    available=False,
                    findings=[],
                )

                return metadata, evidence

            for tag_id, value in exif.items():
                tag_name = str(tag_id)

                if isinstance(value, bytes):
                    value = value.decode(
                        "utf-8",
                        errors="replace",
                    )

                findings.append(
                    f"EXIF {tag_name}: {value}"
                )

            metadata = MetadataInfo(
                available=True,
                findings=findings,
            )

            evidence.append(
                Evidence(
                    source="metadata",
                    modality="image",
                    type="EXIF",
                    score=0.0,
                    confidence=0.95,
                    timestamp=datetime.now(
                        timezone.utc
                    ).isoformat(),
                    explanation=(
                        f"Image contains {len(findings)} "
                        "EXIF metadata field(s)."
                    ),
                )
            )

            return metadata, evidence

    except (OSError, SyntaxError) as exc:
        raise ValueError(
            f"Unable to analyze image metadata: {exc}"
        ) from exc