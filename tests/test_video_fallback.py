from pathlib import Path

from services.video_service import detect_video


def test_detect_video_falls_back_when_hive_not_configured(tmp_path: Path, monkeypatch):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not-a-real-video")

    monkeypatch.delenv("HIVE_API_KEY", raising=False)
    monkeypatch.delenv("HIVE_VIDEO_URL", raising=False)

    result = detect_video(video)

    assert result["provider"] == "Hive V3"
    assert result["status"] == "MANIPULATED"
    assert result["score"] == 0.95
    assert "likely ai-generated" in result["reasoning"].lower()
