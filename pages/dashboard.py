"""History / stats dashboard. Person 2 owns this file (PHASE 10 / Section 6 Step 10).

Uses generate_history() as placeholder data until real results start
persisting (DB or file store) once Person 1's pipelines are connected.
Any results already generated this session (Image/Video/Audio pages) are
folded into the top of the list so the dashboard feels connected to the
rest of the app rather than fully static.
"""

import pandas as pd
import streamlit as st

from assets.mock_data import generate_history
from assets.components import RISK_COLORS, render_distribution_bar, render_history_row

st.markdown('<div class="dt-eyebrow">Dashboard</div>', unsafe_allow_html=True)
st.markdown('<h2 class="dt-display">Overview</h2>', unsafe_allow_html=True)


def _session_results_as_history() -> list[dict]:
    """Fold any results generated this session into history-row format."""
    items = []

    img = st.session_state.get("last_result")
    if img:
        a = img["assessment"]
        items.append({
            "filename": img.get("file_info", {}).get("filename", "uploaded_image"),
            "modality": "image",
            "classification": a["classification"],
            "risk_level": a["risk_level"],
            "trust_score": a["trust_score"],
            "confidence": a["confidence"],
            "date": "Today",
        })

    vid = st.session_state.get("video_result")
    if vid:
        a = vid["assessment"]
        items.append({
            "filename": "uploaded_video.mp4",
            "modality": "video",
            "classification": a["classification"],
            "risk_level": a["risk_level"],
            "trust_score": a["trust_score"],
            "confidence": a["confidence"],
            "date": "Today",
        })

    aud = st.session_state.get("audio_result")
    if aud:
        a = aud["assessment"]
        items.append({
            "filename": "uploaded_audio.wav",
            "modality": "audio",
            "classification": a["classification"],
            "risk_level": a["risk_level"],
            "trust_score": a["trust_score"],
            "confidence": a["confidence"],
            "date": "Today",
        })

    return items


history = _session_results_as_history() + generate_history(n=18)

# ---- Top stat cards ----
total = len(history)
high_risk = sum(1 for h in history if h["risk_level"] == "HIGH")
avg_trust = round(sum(h["trust_score"] for h in history) / total) if total else 0

col1, col2, col3 = st.columns(3)
for col, label, value in zip(
    [col1, col2, col3],
    ["Total analyses", "High risk flagged", "Avg. trust score"],
    [str(total), str(high_risk), f"{avg_trust}/100"],
):
    with col:
        st.markdown(
            f'<div class="dt-card"><div class="dt-eyebrow">{label}</div>'
            f'<h2 class="dt-display" style="margin:0.3rem 0 0 0;">{value}</h2></div>',
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# ---- Distributions ----
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<h3 class="dt-display">Modality distribution</h3>', unsafe_allow_html=True)
    modality_colors = {"image": "#4FD1C5", "video": "#7C5CFC", "audio": "#FBBF24"}
    modality_counts = {}
    for h in history:
        modality_counts[h["modality"]] = modality_counts.get(h["modality"], 0) + 1
    render_distribution_bar([
        {"label": m.title(), "value": c, "color": modality_colors.get(m, "#4FD1C5")}
        for m, c in modality_counts.items()
    ])

with col_b:
    st.markdown('<h3 class="dt-display">Risk distribution</h3>', unsafe_allow_html=True)
    risk_counts = {}
    for h in history:
        risk_counts[h["risk_level"]] = risk_counts.get(h["risk_level"], 0) + 1
    render_distribution_bar([
        {"label": r.title(), "value": c, "color": RISK_COLORS.get(r, "#4FD1C5")}
        for r, c in risk_counts.items()
    ])

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ---- Trust score trend ----
st.markdown('<h3 class="dt-display">Trust score trend</h3>', unsafe_allow_html=True)
trend_rows = [h for h in history if h.get("date") != "Today" and "date_obj" in h]
if trend_rows:
    df = pd.DataFrame(trend_rows)
    daily_avg = (
        df.groupby(df["date_obj"].dt.date)["trust_score"]
        .mean()
        .sort_index()
    )
    st.line_chart(daily_avg, height=200)
else:
    st.markdown('<div class="dt-card">Not enough history yet to chart a trend.</div>',
                unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ---- Manipulation categories ----
st.markdown('<h3 class="dt-display">Manipulation categories</h3>', unsafe_allow_html=True)
category_counts = {}
for h in history:
    category_counts[h["classification"]] = category_counts.get(h["classification"], 0) + 1
category_colors = ["#4FD1C5", "#7C5CFC", "#FBBF24", "#F87171", "#34D399", "#9FB3C8"]
render_distribution_bar([
    {"label": label, "value": count, "color": category_colors[i % len(category_colors)]}
    for i, (label, count) in enumerate(sorted(category_counts.items(), key=lambda x: -x[1]))
])

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ---- Recent analyses ----
st.markdown('<h3 class="dt-display">Recent analyses</h3>', unsafe_allow_html=True)
for item in history[:8]:
    render_history_row(item)

# ---- Saved reports ----
st.markdown('<h3 class="dt-display" style="margin-top:1rem;">Saved reports</h3>', unsafe_allow_html=True)
st.markdown(
    '<div class="dt-card"> PDF export isn\'t wired up yet — this section will list '
    'downloadable forensic reports once <code>utils/report_generator.py</code> is built '
    '(Phase 9).</div>',
    unsafe_allow_html=True,
)
