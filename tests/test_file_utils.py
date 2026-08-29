from pathlib import Path

from utils.file_utils import (
    file_exists,
    get_file_extension,
    get_file_size,
    get_mime_type,
    is_image_file,
    validate_image_path,
    safe_file_info,
)


def test_file_exists(tmp_path: Path):
    file = tmp_path / "test.png"
    file.write_bytes(b"test")

    assert file_exists(file) is True
    assert file_exists(tmp_path / "missing.png") is False


def test_get_file_size(tmp_path: Path):
    file = tmp_path / "test.png"
    file.write_bytes(b"12345")

    assert get_file_size(file) == 5


def test_get_file_size_missing_file(tmp_path: Path):
    file = tmp_path / "missing.png"

    try:
        get_file_size(file)
        assert False
    except FileNotFoundError:
        assert True


def test_get_file_extension(tmp_path: Path):
    file = tmp_path / "photo.PNG"

    assert get_file_extension(file) == ".png"


def test_get_mime_type(tmp_path: Path):
    file = tmp_path / "photo.png"

    assert get_mime_type(file) == "image/png"


def test_is_image_file(tmp_path: Path):
    image = tmp_path / "photo.png"
    image.write_bytes(b"fake")

    assert is_image_file(image) is True


def test_is_image_file_unsupported_extension(tmp_path: Path):
    file = tmp_path / "document.txt"
    file.write_text("hello")

    assert is_image_file(file) is False


def test_validate_image_path_empty():
    valid, error = validate_image_path("")

    assert valid is False
    assert error == "Input path is empty or invalid."


def test_validate_image_path_missing(tmp_path: Path):
    file = tmp_path / "missing.png"

    valid, error = validate_image_path(file)

    assert valid is False
    assert "File does not exist" in error


def test_validate_image_path_unsupported(tmp_path: Path):
    file = tmp_path / "document.txt"
    file.write_text("hello")

    valid, error = validate_image_path(file)

    assert valid is False
    assert "Unsupported image file type" in error


def test_safe_file_info(tmp_path: Path):
    file = tmp_path / "photo.png"
    file.write_bytes(b"12345")

    info = safe_file_info(file)

    assert info["filename"] == "photo.png"
    assert info["file_type"] == "image/png"
    assert info["size"] == 5
    assert info["extension"] == ".png"


def test_safe_file_info_missing(tmp_path: Path):
    file = tmp_path / "missing.png"

    try:
        safe_file_info(file)
        assert False
    except FileNotFoundError:
        assert True
def test_validate_image_path_unsupported_mime_type(
    tmp_path: Path,
    monkeypatch,
):
    file = tmp_path / "photo.png"
    file.write_bytes(b"fake")

    monkeypatch.setattr(
        "utils.file_utils.get_mime_type",
        lambda path: "application/pdf",
    )

    valid, error = validate_image_path(file)

    assert valid is False
    assert "Unsupported MIME type" in error


def test_is_image_file_unsupported_mime_type(
    tmp_path: Path,
    monkeypatch,
):
    file = tmp_path / "photo.png"
    file.write_bytes(b"fake")

    monkeypatch.setattr(
        "utils.file_utils.get_mime_type",
        lambda path: "application/pdf",
    )

    assert is_image_file(file) is False


def test_safe_file_info_unknown_mime_type(
    tmp_path: Path,
    monkeypatch,
):
    file = tmp_path / "unknown.xyz"
    file.write_bytes(b"12345")

    monkeypatch.setattr(
        "utils.file_utils.get_mime_type",
        lambda path: None,
    )

    info = safe_file_info(file)

    assert info["file_type"] == "application/octet-stream"
