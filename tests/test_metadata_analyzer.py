from __future__ import annotations

from pathlib import Path

from PIL import Image

from services.metadata_analyzer import analyze_image_metadata


def test_image_without_exif_returns_unavailable(tmp_path: Path) -> None:
    image_path = tmp_path / "no_exif.jpg"

    image = Image.new("RGB", (10, 10), "white")
    image.save(image_path, format="JPEG")

    metadata, evidence = analyze_image_metadata(image_path)

    assert metadata.available is False
    assert metadata.findings == []
    assert evidence == []


def test_image_with_exif_returns_metadata(tmp_path: Path) -> None:
    image_path = tmp_path / "with_exif.jpg"

    image = Image.new("RGB", (10, 10), "white")

    exif = image.getexif()
    exif[270] = "DeepTrace Test Image"

    image.save(image_path, format="JPEG", exif=exif.tobytes())

    metadata, evidence = analyze_image_metadata(image_path)

    assert metadata.available is True
    assert len(metadata.findings) >= 1

    assert len(evidence) == 1
    assert evidence[0].source == "metadata"
    assert evidence[0].modality == "image"
    assert evidence[0].type == "EXIF"
    assert 0.0 <= evidence[0].score <= 1.0
    assert 0.0 <= evidence[0].confidence <= 1.0


def test_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jpg"

    try:
        analyze_image_metadata(missing)
    except FileNotFoundError:
        return

    raise AssertionError("Expected FileNotFoundError")


def test_invalid_input_raises() -> None:
    try:
        analyze_image_metadata("")
    except ValueError:
        return

    raise AssertionError("Expected ValueError")
def test_none_input_raises_type_error() -> None:
    try:
        analyze_image_metadata(None)
    except TypeError:
        return

    raise AssertionError("Expected TypeError")


def test_invalid_input_type_raises_type_error() -> None:
    try:
        analyze_image_metadata(123)
    except TypeError:
        return

    raise AssertionError("Expected TypeError")


def test_whitespace_input_raises_value_error() -> None:
    try:
        analyze_image_metadata("   ")
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_directory_input_raises_value_error(tmp_path: Path) -> None:
    try:
        analyze_image_metadata(tmp_path)
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_invalid_image_file_raises_value_error(tmp_path: Path) -> None:
    image_path = tmp_path / "invalid.jpg"
    image_path.write_text("this is not a valid image")

    try:
        analyze_image_metadata(image_path)
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_exif_bytes_are_decoded(tmp_path: Path) -> None:
    image_path = tmp_path / "bytes_exif.jpg"

    image = Image.new("RGB", (10, 10), "white")

    exif = image.getexif()
    exif[270] = b"DeepTrace Bytes"

    image.save(
        image_path,
        format="JPEG",
        exif=exif.tobytes(),
    )

    metadata, evidence = analyze_image_metadata(image_path)

    assert metadata.available is True
    assert len(metadata.findings) >= 1
    assert len(evidence) == 1
