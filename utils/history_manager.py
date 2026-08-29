"""
DeepTrace analysis history manager.

Handles saving and loading completed analyses so the Dashboard
can display persistent analysis history.
"""

import json
from datetime import datetime
from pathlib import Path


# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

HISTORY_FILE = DATA_DIR / "analysis_history.json"


# -------------------------------------------------
# INITIALIZE STORAGE
# -------------------------------------------------

def _ensure_history_file() -> None:
    """Create the data directory and history file if they don't exist."""

    DATA_DIR.mkdir(exist_ok=True)

    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


# -------------------------------------------------
# LOAD HISTORY
# -------------------------------------------------

def load_history() -> list[dict]:
    """
    Load all previously saved analysis history.

    Returns an empty list if no history exists yet.
    """

    _ensure_history_file()

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

        if isinstance(history, list):
            return history

        return []

    except (json.JSONDecodeError, OSError):
        return []


# -------------------------------------------------
# SAVE ANALYSIS
# -------------------------------------------------

def save_analysis(
    result: dict,
    modality: str,
) -> None:
    """
    Save a completed analysis to persistent history.

    Parameters
    ----------
    result : dict
        Complete result returned by an analysis pipeline.

    modality : str
        Type of media: image, video, or audio.
    """

    _ensure_history_file()

    history = load_history()

    assessment = result.get("assessment", {})
    file_info = result.get("file_info", {})

    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),

        "timestamp": datetime.now().isoformat(),

        "filename": file_info.get(
            "filename",
            f"uploaded_{modality}",
        ),

        "modality": modality.lower(),

        "classification": assessment.get(
            "classification",
            "Unknown",
        ),

        "risk_level": assessment.get(
            "risk_level",
            "LOW",
        ).upper(),

        "trust_score": assessment.get(
            "trust_score",
            0,
        ),

        "confidence": assessment.get(
            "confidence",
            0,
        ),
    }

    # Add newest analysis at the beginning
    history.insert(0, entry)

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                history,
                file,
                indent=4,
            )

    except OSError:
        pass