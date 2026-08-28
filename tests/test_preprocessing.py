from pathlib import Path

import pytest
from PIL import Image

from utils.preprocessing import preprocess_image


def _write_test_image(path: Path) -> None:
    image = Image.new("RGB", (100, 80), "white")
    image.save(path)
from pathlib import Path

import pytest
from PIL import Image

from utils.preprocessing import preprocess_image


def _write_image(path: Path) -> None:
    image = Image.new("RGB", (100, 80), "white")
    image.save(path)


def test_preprocess_image_resizes_image(tmp_path: Path) -> None:
    image_path = tmp_path / "test.jpg"
    _write_image(image_path)

    result = preprocess_image(image_path)

    assert result.size == (512, 512)


def test_preprocess_image_converts_to_rgb(tmp_path: Path) -> None:
    image_path = tmp_path / "test.png"

    image = Image.new("RGBA", (100, 80), "white")
    image.save(image_path)

    result = preprocess_image(image_path)

    assert result.mode == "RGB"


def test_preprocess_image_custom_size(tmp_path: Path) -> None:
    image_path = tmp_path / "test.jpg"
    _write_image(image_path)

    result = preprocess_image(image_path, size=(224, 224))

    assert result.size == (224, 224)


def test_preprocess_image_invalid_input() -> None:
    with pytest.raises(TypeError):
        preprocess_image(None)

    with pytest.raises(ValueError):
        preprocess_image("")


from pathlib import Path

import pytest
from PIL import Image

from utils.preprocessing import preprocess_image


def _write_image(path: Path) -> None:
    image = Image.new("RGB", (100, 80), "white")
    image.save(path)


def test_preprocess_image_resizes_image(tmp_path: Path) -> None:
    image_path = tmp_path / "test.jpg"
    _write_image(image_path)

    result = preprocess_image(image_path)

    assert result.size == (512, 512)


def test_preprocess_image_converts_to_rgb(tmp_path: Path) -> None:
    image_path = tmp_path / "test.png"

    image = Image.new("RGBA", (100, 80), "white")
    image.save(image_path)

    result = preprocess_image(image_path)

    assert result.mode == "RGB"


def test_preprocess_image_custom_size(tmp_path: Path) -> None:
    image_path = tmp_path / "test.jpg"
    _write_image(image_path)

    result = preprocess_image(image_path, size=(224, 224))

    assert result.size == (224, 224)


def test_preprocess_image_invalid_input() -> None:
    with pytest.raises(TypeError):
        preprocess_image(None)

    with pytest.raises(ValueError):
        preprocess_image("")


def test_preprocess_image_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        preprocess_image("does_not_exist.jpg")
def test_preprocess_image_none():
    with pytest.raises(TypeError):
        preprocess_image(None)


def test_preprocess_image_invalid_type():
    with pytest.raises(TypeError):
        preprocess_image(123)


def test_preprocess_image_empty_path():
    with pytest.raises(ValueError):
        preprocess_image("")


def test_preprocess_image_missing_file(tmp_path):
    missing = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        preprocess_image(missing)


def test_preprocess_image_directory(tmp_path):
    with pytest.raises(ValueError):
        preprocess_image(tmp_path)


def test_preprocess_image_unsupported_extension(tmp_path):
    file = tmp_path / "document.txt"
    file.write_text("not an image")

    with pytest.raises(ValueError):
        preprocess_image(file)


def test_preprocess_image_invalid_size(tmp_path):
    image_path = tmp_path / "test.png"
    _write_test_image(image_path)

    with pytest.raises(ValueError):
        preprocess_image(image_path, size=(0, 512))


def test_preprocess_image_custom_size(tmp_path):
    image_path = tmp_path / "test.png"
    _write_test_image(image_path)

    result = preprocess_image(image_path, size=(256, 256))

    assert result.size == (256, 256)
    assert result.mode == "RGB"
