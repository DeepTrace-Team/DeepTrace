"""
Mock analysis history for the dashboard.

Once Person 1's pipelines are live and results start persisting (DB or file
store), replace generate_history() with a real query. Until then this gives
the dashboard realistic-looking data to render against, seeded so it stays
stable across reruns/navigation within a session.
"""

import random
from datetime import datetime, timedelta

MODALITIES = ["image", "video", "audio"]

CLASSIFICATIONS = {
    "image": ["Likely AI Generated", "Face Swap Detected", "Likely Authentic", "Image Editing Detected"],
    "video": ["Manipulated Segments Detected", "Likely Authentic", "Deepfake Detected"],
    "audio": ["Likely Voice Clone", "Likely Authentic", "Synthetic Speech Detected"],
}

EXTENSIONS = {"image": "jpg", "video": "mp4", "audio": "wav"}
RISK_LEVELS = ["HIGH", "MEDIUM", "LOW"]


def generate_history(n: int = 18, seed: str = "dt_history") -> list[dict]:
    rng = random.Random(seed)
    today = datetime.now()
    history = []

    for i in range(n):
        modality = rng.choice(MODALITIES)
        classification = rng.choice(CLASSIFICATIONS[modality])
        risk = rng.choices(RISK_LEVELS, weights=[0.35, 0.35, 0.3])[0]
        trust_score = {
            "HIGH": rng.randint(0, 33),
            "MEDIUM": rng.randint(34, 66),
            "LOW": rng.randint(67, 100),
        }[risk]
        date_obj = today - timedelta(days=rng.randint(0, 13))

        history.append({
            "filename": f"{modality}_{1000 + i}.{EXTENSIONS[modality]}",
            "modality": modality,
            "classification": classification,
            "risk_level": risk,
            "trust_score": trust_score,
            "confidence": rng.randint(55, 97),
            "date_obj": date_obj,
            "date": date_obj.strftime("%b %d"),
        })

    history.sort(key=lambda h: h["date_obj"], reverse=True)
    return history
