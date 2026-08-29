from pathlib import Path

from core.image_types import (
    ImageInput,
    is_supported_image_extension,
    is_supported_mime_type,
)


def test_image_input_path():
    image = ImageInput(
        file_path="test.png",
        filename="test.png",
        extension=".png",
    )

    assert image.path == Path("test.png")


def test_image_input_from_existing_path(tmp_path):
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"test image data")

    image = ImageInput.from_path(image_path)

    assert image.file_path == image_path
    assert image.filename == "test.png"
    assert image.extension == ".png"
    assert image.size == len(b"test image data")
    assert image.is_valid is True


def test_image_input_from_missing_path(tmp_path):
    image_path = tmp_path / "missing.png"

    image = ImageInput.from_path(image_path)

    assert image.size == 0
    assert image.is_valid is True
    assert image.filename == "missing.png"


def test_supported_image_extension():
    assert is_supported_image_extension(".png") is True
    assert is_supported_image_extension(".JPG") is True
    assert is_supported_image_extension(".txt") is False


def test_supported_mime_type():
    assert is_supported_mime_type("image/png") is True
    assert is_supported_mime_type("IMAGE/JPEG") is True
    assert is_supported_mime_type("text/plain") is False


def test_supported_mime_type_none():
    assert is_supported_mime_type(None) is False
