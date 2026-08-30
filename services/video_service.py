from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# HIVE V3 CONFIGURATION
# ============================================================

HIVE_V3_URL = (
    "https://api.thehive.ai/api/v3/chat/completions"
)

HIVE_MODEL = (
    "hive/vision-language-model"
)

# DeepTrace application limit
MAX_VIDEO_SIZE_MB = 200
MAX_VIDEO_SIZE_BYTES = (
    MAX_VIDEO_SIZE_MB * 1024 * 1024
)


SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".m4v",
}


# ============================================================
# VALIDATE VIDEO
# ============================================================

def _validate_video_path(
    video_path: str | Path,
) -> Path:

    if video_path is None:
        raise TypeError(
            "video_path cannot be None."
        )

    if not isinstance(
        video_path,
        (str, Path),
    ):
        raise TypeError(
            "video_path must be a string or pathlib.Path."
        )

    if str(video_path).strip() == "":
        raise ValueError(
            "video_path cannot be empty."
        )

    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Video file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Video path is not a file: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_VIDEO_EXTENSIONS:
        raise ValueError(
            f"Unsupported video format: {extension}\n"
            f"Supported formats: "
            f"{', '.join(sorted(SUPPORTED_VIDEO_EXTENSIONS))}"
        )

    # --------------------------------------------------------
    # 200 MB DeepTrace limit
    # --------------------------------------------------------

    file_size_bytes = path.stat().st_size

    if file_size_bytes > MAX_VIDEO_SIZE_BYTES:

        file_size_mb = (
            file_size_bytes
            / (1024 * 1024)
        )

        raise ValueError(
            f"Video is {file_size_mb:.1f} MB. "
            f"DeepTrace supports videos up to "
            f"{MAX_VIDEO_SIZE_MB} MB."
        )

    return path


# ============================================================
# GET HIVE API KEY
# ============================================================

def _get_hive_api_key() -> str:

    api_key = os.getenv(
        "HIVE_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "HIVE_API_KEY is not configured.\n"
            "Add it to your .env file."
        )

    return api_key.strip()


# ============================================================
# GET VIDEO URL
# ============================================================

def _get_video_url(
    video_path: Path,
) -> str:
    """
    Hive V3 needs an HTTP/HTTPS URL for URL-based video
    analysis.

    The local Windows path cannot be sent directly to Hive.

    Configure HIVE_VIDEO_URL in .env.
    """

    video_url = os.getenv(
        "HIVE_VIDEO_URL"
    )

    if not video_url:

        raise RuntimeError(
            "HIVE_VIDEO_URL is not configured.\n\n"
            "Hive V3 URL-based video analysis requires "
            "a publicly accessible HTTP/HTTPS video URL.\n\n"
            f"Local video:\n{video_path}\n\n"
            "Add this to .env:\n"
            "HIVE_VIDEO_URL=https://your-public-url/video.mp4"
        )

    video_url = video_url.strip()

    if not (
        video_url.startswith("http://")
        or video_url.startswith("https://")
    ):

        raise ValueError(
            "HIVE_VIDEO_URL must be a valid "
            "HTTP/HTTPS URL."
        )

    return video_url


# ============================================================
# DEEPFAKE ANALYSIS PROMPT
# ============================================================

DEEPFAKE_PROMPT = """
You are a forensic media analysis assistant.

Analyze the supplied video for signs of:

- AI-generated video
- deepfake manipulation
- face swapping
- identity manipulation
- synthetic facial regions
- unnatural facial motion
- temporal inconsistencies
- frame-to-frame artifacts
- facial boundary warping
- unnatural skin or texture patterns
- inconsistent lighting
- inconsistent shadows
- inconsistent reflections
- lip-sync inconsistencies
- unnatural eyes, mouth, teeth, or facial features
- other visual evidence of manipulation

Do not classify a video as fake merely because it looks unusual.

Be conservative and evidence-based.

Return ONLY valid JSON.

Use exactly this structure:

{
    "classification": "AUTHENTIC",
    "confidence": 0.95,
    "reasoning": "Brief forensic explanation.",
    "suspicious_segments": [
        {
            "timestamp": 12.5,
            "score": 0.91,
            "reason": "Brief explanation."
        }
    ]
}

Classification must be exactly one of:

AUTHENTIC
MANIPULATED
UNCERTAIN

Rules:

1. confidence must be between 0 and 1.

2. suspicious segment score must be between 0 and 1.

3. AUTHENTIC means there is no meaningful visible evidence
   of AI/deepfake manipulation.

4. MANIPULATED means there is meaningful visual evidence
   suggesting AI/deepfake manipulation.

5. UNCERTAIN means the available evidence is insufficient
   for a reliable determination.

6. Never invent timestamps.

7. Only provide suspicious segments when the video provides
   evidence for those timestamps.

8. Do not claim absolute forensic certainty.

9. Do not infer manipulation merely from poor video quality,
   compression, lighting, camera movement, or unusual behavior.

10. Return JSON only.
"""


# ============================================================
# EXTRACT JSON FROM HIVE RESPONSE
# ============================================================

def _extract_json(
    content: str,
) -> dict[str, Any]:

    if not content:
        raise RuntimeError(
            "Hive returned an empty analysis response."
        )

    text = content.strip()

    # --------------------------------------------------------
    # Remove Markdown code fences if present
    # --------------------------------------------------------

    if text.startswith("```"):

        lines = text.splitlines()

        cleaned_lines = []

        for line in lines:

            if line.strip().startswith("```"):
                continue

            cleaned_lines.append(line)

        text = "\n".join(
            cleaned_lines
        ).strip()

    # --------------------------------------------------------
    # Try complete response
    # --------------------------------------------------------

    try:

        parsed = json.loads(
            text
        )

        if isinstance(
            parsed,
            dict,
        ):
            return parsed

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Try extracting JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:

        candidate = text[
            start:end + 1
        ]

        try:

            parsed = json.loads(
                candidate
            )

            if isinstance(
                parsed,
                dict,
            ):
                return parsed

        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        "Hive returned an invalid JSON analysis.\n"
        f"Raw response:\n{text}"
    )


# ============================================================
# NORMALIZE CLASSIFICATION
# ============================================================

def _normalize_classification(
    value: Any,
) -> str:

    classification = str(
        value or ""
    ).upper().strip()

    if classification in {
        "AUTHENTIC",
        "REAL",
        "GENUINE",
        "NON_AI",
    }:

        return "AUTHENTIC"

    if classification in {
        "MANIPULATED",
        "FAKE",
        "SYNTHETIC",
        "AI_GENERATED",
        "DEEPFAKE",
    }:

        return "MANIPULATED"

    if classification in {
        "UNCERTAIN",
        "UNKNOWN",
        "NOT_APPLICABLE",
        "N/A",
    }:

        return "UNCERTAIN"

    return "UNCERTAIN"


# ============================================================
# NORMALIZE SCORE
# ============================================================

def _normalize_score(
    value: Any,
) -> float:

    try:

        score = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0

    return max(
        0.0,
        min(
            1.0,
            score,
        ),
    )


# ============================================================
# NORMALIZE SUSPICIOUS SEGMENTS
# ============================================================

def _normalize_segments(
    value: Any,
) -> list[dict[str, Any]]:

    if not isinstance(
        value,
        list,
    ):
        return []

    segments = []

    for segment in value:

        if not isinstance(
            segment,
            dict,
        ):
            continue

        timestamp = segment.get(
            "timestamp"
        )

        if timestamp is None:
            continue

        try:

            timestamp = float(
                timestamp
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

        score = _normalize_score(
            segment.get(
                "score"
            )
        )

        reason = str(
            segment.get(
                "reason",
                "",
            )
        ).strip()

        segments.append(
            {
                "timestamp":
                    timestamp,

                "score":
                    score,

                "reason":
                    reason,
            }
        )

    return segments


# ============================================================
# HIVE V3 VIDEO DETECTOR
# ============================================================

def detect_video(
    video_path: str | Path,
) -> dict[str, Any]:
    """
    Analyze a video using Hive V3.

    The DeepTrace application accepts videos up to 200 MB.

    Hive receives the video through HIVE_VIDEO_URL rather
    than Base64, avoiding the 20 MB Base64 request problem.
    """

    # --------------------------------------------------------
    # Validate local video
    # --------------------------------------------------------

    path = _validate_video_path(
        video_path
    )

    # --------------------------------------------------------
    # API key
    # --------------------------------------------------------

    api_key = _get_hive_api_key()

    # --------------------------------------------------------
    # Public video URL
    # --------------------------------------------------------

    video_url = _get_video_url(
        path
    )

    # --------------------------------------------------------
    # Headers
    # --------------------------------------------------------

    headers = {
        "Authorization":
            f"Bearer {api_key}",

        "Content-Type":
            "application/json",

        "Accept":
            "application/json",
    }

    # --------------------------------------------------------
    # Hive V3 payload
    # --------------------------------------------------------

    payload = {

        "model":
            HIVE_MODEL,

        "messages": [

            {

                "role":
                    "user",

                "content": [

                    {

                        "type":
                            "media_url",

                        "media_url": {

                            "url":
                                video_url,

                            "sampling": {

                                "strategy":
                                    "fps",

                                "fps":
                                    1,
                            },

                            "prompt_scope":
                                "once",
                        },
                    },

                    {

                        "type":
                            "text",

                        "text":
                            DEEPFAKE_PROMPT,
                    },
                ],
            }
        ],

        "temperature":
            0,

        "top_p":
            0.1,

        "max_tokens":
            2048,
    }

    # --------------------------------------------------------
    # SEND REQUEST
    # --------------------------------------------------------

    try:

        response = requests.post(
            HIVE_V3_URL,
            headers=headers,
            json=payload,
            timeout=300,
        )

    except requests.RequestException as exc:

        raise RuntimeError(
            "Unable to connect to Hive V3.\n"
            f"{exc}"
        ) from exc

    # --------------------------------------------------------
    # HANDLE HTTP ERRORS
    # --------------------------------------------------------

    if not response.ok:

        try:

            error_body = (
                response.json()
            )

        except Exception:

            error_body = (
                response.text
            )

        raise RuntimeError(
            "Hive V3 video request failed.\n"
            f"HTTP {response.status_code}\n"
            f"{error_body}"
        )

    # --------------------------------------------------------
    # PARSE RESPONSE
    # --------------------------------------------------------

    try:

        hive_response = (
            response.json()
        )

    except ValueError as exc:

        raise RuntimeError(
            "Hive V3 returned a non-JSON response.\n"
            f"{response.text}"
        ) from exc

    # --------------------------------------------------------
    # GET CHOICES
    # --------------------------------------------------------

    choices = hive_response.get(
        "choices",
        []
    )

    if not isinstance(
        choices,
        list,
    ) or not choices:

        raise RuntimeError(
            "Hive V3 returned no analysis choices.\n"
            f"Response: {hive_response}"
        )

    choice = choices[0]

    if not isinstance(
        choice,
        dict,
    ):

        raise RuntimeError(
            "Hive V3 returned an invalid choice."
        )

    # --------------------------------------------------------
    # GET MESSAGE
    # --------------------------------------------------------

    message = choice.get(
        "message",
        {}
    )

    if not isinstance(
        message,
        dict,
    ):

        raise RuntimeError(
            "Hive V3 returned an invalid message."
        )

    content = message.get(
        "content",
        ""
    )

    if not isinstance(
        content,
        str,
    ):

        content = str(
            content
        )

    # --------------------------------------------------------
    # PARSE FORENSIC RESPONSE
    # --------------------------------------------------------

    analysis = _extract_json(
        content
    )

    classification = (
        _normalize_classification(
            analysis.get(
                "classification"
            )
        )
    )

    confidence = _normalize_score(
        analysis.get(
            "confidence"
        )
    )

    reasoning = str(
        analysis.get(
            "reasoning",
            "",
        )
    ).strip()

    suspicious_segments = (
        _normalize_segments(
            analysis.get(
                "suspicious_segments",
                [],
            )
        )
    )

    # --------------------------------------------------------
    # CONVERT TO DEEPTRACE SCORE
    #
    # DeepTrace:
    # 0.0 = completely trustworthy
    # 1.0 = highly suspicious
    # --------------------------------------------------------

    if classification == "AUTHENTIC":

        suspicion_score = (
            1.0 - confidence
        )

    elif classification == "MANIPULATED":

        suspicion_score = confidence

    else:

        suspicion_score = 0.5

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if classification == "AUTHENTIC":

        if confidence >= 0.80:
            risk_level = "LOW"

        else:
            risk_level = "MEDIUM"

    elif classification == "MANIPULATED":

        if confidence >= 0.80:
            risk_level = "HIGH"

        else:
            risk_level = "MEDIUM"

    else:

        risk_level = "UNKNOWN"

    # --------------------------------------------------------
    # FINAL NORMALIZED RESULT
    # --------------------------------------------------------

    return {

        "provider":
            "Hive V3",

        "model":
            HIVE_MODEL,

        "request_id":
            hive_response.get(
                "id"
            ),

        "status":
            classification,

        "score":
            suspicion_score,

        "confidence":
            confidence,

        "reasoning":
            reasoning,

        "risk_level":
            risk_level,

        "suspicious_segments":
            suspicious_segments,

        "video_url":
            video_url,

        "hive_analysis":
            analysis,

        "raw_result":
            hive_response,
    }