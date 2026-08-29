from __future__ import annotations

import struct
import zlib
from pathlib import Path

import pytest

from services.image_ingestion import ingest_image_file


def _write_png(path: Path) -> None:
    width = 1
    height = 1

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack("!I", len(data))
            + tag
            + data
            + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = b"\x00\x00\x00\x00\x00"
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png_bytes)


def test_valid_image_input(tmp_path: Path) -> None:
    image_path = tmp_path / "valid.png"
    _write_png(image_path)

    result = ingest_image_file(image_path)

    assert result.status == "success"
    assert result.file_info.filename == "valid.png"
    assert result.file_info.file_type == "image/png"
    assert result.file_info.size > 0
    assert result.metadata.available is False


def test_unsupported_file_type(tmp_path: Path) -> None:
    bad_file = tmp_path / "not_an_image.txt"
    bad_file.write_text("not an image")

    with pytest.raises(ValueError, match="Unsupported|image"):
        ingest_image_file(bad_file)


def test_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        ingest_image_file(missing)


def test_file_metadata_extraction(tmp_path: Path) -> None:
    image_path = tmp_path / "metadata_test.PNG"
    _write_png(image_path)

    result = ingest_image_file(image_path)

    assert result.file_info.filename == "metadata_test.PNG"
    assert result.file_info.file_type == "image/png"
    assert result.file_info.size > 0


def test_invalid_input_handling() -> None:
    with pytest.raises(TypeError):
        ingest_image_file(None)

    with pytest.raises(ValueError):
        ingest_image_file("")
def test_ingest_invalid_input_type_raises_type_error() -> None:
    try:
        ingest_image_file(123)
    except TypeError:
        return
    raise AssertionError("Expected TypeError")
