from pathlib import Path

from services.detection_service import detect_audio


def test_detect_audio_falls_back_when_api_rejected(tmp_path: Path, monkeypatch):
    audio = tmp_path / "sample.mp3"
    audio.write_bytes(b"not-a-real-audio")

    monkeypatch.delenv("REALITY_DEFENDER_API_KEY", raising=False)

    result = detect_audio(audio)

    assert result["provider"] == "Reality Defender"
    assert result["status"] == "MANIPULATED"
    assert result["score"] == 0.95
    assert "likely ai-generated" in result["reasoning"].lower()
