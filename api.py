from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from pipelines.image_pipeline import analyze_image


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


@app.post("/api/analyze/image")
async def analyze_image_api(
    file: UploadFile = File(...),
) -> dict:
    """
    Upload an image and run the complete DeepTrace
    image authenticity analysis pipeline.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    suffix = Path(file.filename).suffix.lower()

    # Accept the upload when either the MIME type
    # or the file extension identifies it as an image.
    if (
        file.content_type not in ALLOWED_IMAGE_TYPES
        and suffix not in ALLOWED_IMAGE_EXTENSIONS
    ):
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported image type. "
                "Allowed types: JPEG, PNG, WEBP."
            ),
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

        # Run the synchronous DeepTrace pipeline
        # in a worker thread so it does not conflict
        # with FastAPI's running event loop.
        result = await asyncio.to_thread(
            analyze_image,
            temp_path,
        )

        return result.to_dict()

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {exc}",
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
