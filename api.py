from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from pipelines.image_pipeline import analyze_image
from pipelines.video_pipeline import analyze_video
from pipelines.audio_pipeline import analyze_audio
from services.video_service import MAX_VIDEO_SIZE_MB


app = FastAPI(
    title="DeepTrace API",
    description="Multimodal AI-powered digital media authenticity analysis API",
    version="1.0.0",
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".webm",
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a",
}

ALLOWED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
}

MAX_VIDEO_UPLOAD_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024


@app.get("/")
def root() -> dict:
    return {
        "name": "DeepTrace API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
    }


async def _analyze_upload(
    file: UploadFile,
    allowed_types: set[str],
    allowed_extensions: set[str],
    unsupported_message: str,
    analyze_fn,
    max_size_bytes: int | None = None,
    max_size_message: str | None = None,
) -> dict:
    """
    Shared upload-to-temp-file-to-pipeline flow used by all three
    /api/analyze/* endpoints, so each stays a thin wrapper.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    suffix = Path(file.filename).suffix.lower()

    # Accept the upload when either the MIME type
    # or the file extension identifies it correctly.
    if (
        file.content_type not in allowed_types
        and suffix not in allowed_extensions
    ):
        raise HTTPException(
            status_code=415,
            detail=unsupported_message,
        )

    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_path = Path(temp_file.name)

            shutil.copyfileobj(
                file.file,
                temp_file,
            )

        # Fail fast on oversized uploads (e.g. video's Hive V3 limit)
        # instead of letting the pipeline hit a generic 500 later.
        if max_size_bytes is not None:
            actual_size = temp_path.stat().st_size

            if actual_size > max_size_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        max_size_message
                        or (
                            f"File is too large "
                            f"({actual_size / 1024 / 1024:.1f} MB). "
                            f"Maximum allowed size is "
                            f"{max_size_bytes / 1024 / 1024:.0f} MB."
                        )
                    ),
                )

        # Run the synchronous DeepTrace pipeline
        # in a worker thread so it does not conflict
        # with FastAPI's running event loop.
        result = await asyncio.to_thread(
            analyze_fn,
            temp_path,
        )

        return result.to_dict()

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {exc}",
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


@app.post("/api/analyze/image")
async def analyze_image_api(
    file: UploadFile = File(...),
) -> dict:
    """
    Upload an image and run the complete DeepTrace
    image authenticity analysis pipeline.
    """

    return await _analyze_upload(
        file,
        ALLOWED_IMAGE_TYPES,
        ALLOWED_IMAGE_EXTENSIONS,
        "Unsupported image type. Allowed types: JPEG, PNG, WEBP.",
        analyze_image,
    )


@app.post("/api/analyze/video")
async def analyze_video_api(
    file: UploadFile = File(...),
) -> dict:
    """
    Upload a video and run the complete DeepTrace
    video authenticity analysis pipeline (Hive V3).
    """

    return await _analyze_upload(
        file,
        ALLOWED_VIDEO_TYPES,
        ALLOWED_VIDEO_EXTENSIONS,
        "Unsupported video type. Allowed types: MP4, MOV, WEBM.",
        analyze_video,
        max_size_bytes=MAX_VIDEO_UPLOAD_BYTES,
        max_size_message=(
            f"Video exceeds the {MAX_VIDEO_SIZE_MB} MB limit "
            "for video analysis."
        ),
    )


@app.post("/api/analyze/audio")
async def analyze_audio_api(
    file: UploadFile = File(...),
) -> dict:
    """
    Upload an audio file and run the complete DeepTrace
    audio authenticity analysis pipeline.
    """

    return await _analyze_upload(
        file,
        ALLOWED_AUDIO_TYPES,
        ALLOWED_AUDIO_EXTENSIONS,
        "Unsupported audio type. Allowed types: MP3, WAV, M4A.",
        analyze_audio,
    )
