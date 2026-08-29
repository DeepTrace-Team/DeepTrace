from pathlib import Path

import pytest
from PIL import Image

from pipelines.image_pipeline import analyze_image


def _write_png(path: Path) -> None:
    image = Image.new("RGB", (100, 80), "white")
    image.save(path)


def test_analyze_image_pipeline(tmp_path: Path, monkeypatch) -> None:
    image_path = tmp_path / "pipeline_test.png"
    _write_png(image_path)

    # Mock Reality Defender so this unit test does not call
    # the external API.
    def fake_detect_image(path):
        return {
            "status": "AUTHENTIC",
            "score": 0.10,
            "models": [],
        }

    monkeypatch.setattr(
        "pipelines.image_pipeline.detect_image",
        fake_detect_image,
    )

    result = analyze_image(image_path)

    assert result.status == "success"
    assert result.file_info.filename == "pipeline_test.png"
    assert result.file_info.file_type == "image/png"
    assert result.file_info.size > 0

    assert result.assessment.classification == "authentic"
    assert result.assessment.confidence == 0.10
    assert result.assessment.trust_score == 90
    assert result.assessment.risk_level == "LOW"

    assert result.metadata.available is False
    assert result.metadata.findings == []

    assert len(result.evidence) == 1
    assert result.evidence[0].type == "AI_DETECTION"


def test_analyze_image_missing_file(tmp_path: Path) -> None:
    image_path = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        analyze_image(image_path)


def test_analyze_image_unsupported_file(tmp_path: Path) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("not an image")

    with pytest.raises(ValueError, match="Unsupported|image"):
        analyze_image(file_path)


def test_analyze_image_invalid_input() -> None:
    with pytest.raises(TypeError):
        analyze_image(None)

    with pytest.raises(ValueError):
        analyze_image("")
