from pathlib import Path

import pytest
from PIL import Image

from pipelines.image_pipeline import analyze_image


def _write_png(path: Path) -> None:
    image = Image.new("RGB", (100, 80), "white")
    image.save(path)


def test_analyze_image_pipeline(tmp_path: Path) -> None:
    image_path = tmp_path / "pipeline_test.png"
    _write_png(image_path)

    result = analyze_image(image_path)

    assert result.status == "success"
    assert result.file_info.filename == "pipeline_test.png"
    assert result.file_info.file_type == "image/png"
    assert result.file_info.size > 0

    assert result.assessment.classification == "unknown"
    assert result.assessment.confidence == 0.0
    assert result.assessment.trust_score == 0
    assert result.assessment.risk_level == "unknown"

    assert result.metadata.available is False
    assert result.metadata.findings == []
    assert result.evidence == []


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
