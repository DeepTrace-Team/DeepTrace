"""
DeepTrace shared result-display components.

These render the same visual language (trust gauge, evidence bars, metadata
findings, timelines, waveform) everywhere results show up — results.py,
video_analysis.py, audio_analysis.py — so pages stay thin and consistent.
"""

import random
import streamlit as st

RISK_COLORS = {
    "HIGH": "#F87171",
    "MEDIUM": "#FBBF24",
    "LOW": "#34D399",
}


def render_assessment_card(assessment: dict) -> None:
    """Top-level verdict card: risk badge, classification, confidence, trust gauge."""
    risk = assessment.get("risk_level", "LOW").upper()
    color = RISK_COLORS.get(risk, "#4FD1C5")

    st.markdown(
        f"""
        <div class="dt-card">
            <span class="dt-mono" style="color:{color}; font-size:0.82rem; letter-spacing:0.08em;">
                {risk} RISK
            </span>
            <h2 class="dt-display" style="margin:0.35rem 0;">{assessment.get('classification', 'Unknown')}</h2>
            <p style="color:#C4D0DC; margin:0;">
                Confidence: <b>{assessment.get('confidence', 0)}%</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_trust_gauge(assessment.get("trust_score", 0), risk)


def render_trust_gauge(trust_score: int, risk_level: str) -> None:
    pct = max(0, min(100, trust_score))
    color = RISK_COLORS.get(risk_level.upper(), "#4FD1C5")

    st.markdown(
        f"""
        <div style="margin: 0.75rem 0 1.25rem 0;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                <span class="dt-mono" style="font-size:0.78rem; color:#9FB3C8; letter-spacing:0.08em;">TRUST SCORE</span>
                <span class="dt-mono" style="font-size:0.78rem; color:{color};">{trust_score}/100</span>
            </div>
            <div style="position:relative; height:10px; border-radius:6px;
                        background: linear-gradient(90deg,
                            rgba(248,113,113,0.45) 0%, rgba(248,113,113,0.45) 33%,
                            rgba(251,191,36,0.45) 33%, rgba(251,191,36,0.45) 66%,
                            rgba(52,211,153,0.45) 66%, rgba(52,211,153,0.45) 100%);">
                <div style="position:absolute; top:-3px; left:calc({pct}% - 2px);
                            width:4px; height:16px; background:#fff; border-radius:2px;
                            box-shadow:0 0 8px 2px rgba(255,255,255,0.7);"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_evidence_list(evidence: list[dict]) -> None:
    """Each item: {source, score (0-1 or 0-100), explanation}."""
    if not evidence:
        st.markdown('<div class="dt-card">No evidence returned.</div>', unsafe_allow_html=True)
        return

    cards = ""
    for item in evidence:
        raw_score = item.get("score", 0)
        score_pct = round(raw_score * 100) if raw_score <= 1 else round(raw_score)
        cards += f"""
        <div class="dt-card" style="margin-bottom:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span style="font-weight:600;">{item.get('source', 'Unknown source')}</span>
                <span class="dt-mono" style="color:#4FD1C5;">{score_pct}%</span>
            </div>
            <div style="height:6px; border-radius:4px; background:rgba(255,255,255,0.08); margin:0.55rem 0;">
                <div style="height:100%; width:{score_pct}%; border-radius:4px;
                            background:linear-gradient(90deg,#4FD1C5,#7C5CFC);"></div>
            </div>
            <p style="color:#9FB3C8; margin:0; font-size:0.92rem;">{item.get('explanation', '')}</p>
        </div>
        """
    st.markdown(cards, unsafe_allow_html=True)


def render_metadata_findings(metadata: dict) -> None:
    findings = metadata.get("findings", [])
    if not findings:
        st.markdown(
            '<div class="dt-card">✅ No metadata irregularities found.</div>',
            unsafe_allow_html=True,
        )
        return
    items = "".join(f"<li style='margin-bottom:0.35rem;'>{f}</li>" for f in findings)
    st.markdown(
        f'<div class="dt-card"><ul style="margin:0; padding-left:1.1rem; color:#C4D0DC;">{items}</ul></div>',
        unsafe_allow_html=True,
    )


def render_timeline(segments: list[dict], duration_label: str = "00:00 – 00:30") -> None:
    """Horizontal duration bar with flagged regions highlighted.
    segments: [{start_pct, end_pct, severity}], severity in HIGH/MEDIUM/LOW."""
    seg_html = ""
    for s in segments:
        color = RISK_COLORS.get(s.get("severity", "MEDIUM").upper(), "#FBBF24")
        width = max(1, s["end_pct"] - s["start_pct"])
        seg_html += (
            f'<div style="position:absolute; left:{s["start_pct"]}%; width:{width}%; '
            f'top:0; bottom:0; background:{color}; opacity:0.6; border-radius:3px;"></div>'
        )

    start_label, _, end_label = duration_label.partition(" – ")
    st.markdown(
        f"""
        <div style="margin: 0.75rem 0;">
            <div style="position:relative; height:28px; border-radius:6px;
                        background:rgba(255,255,255,0.05); overflow:hidden;">
                {seg_html}
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:0.3rem;">
                <span class="dt-mono" style="font-size:0.75rem; color:#9FB3C8;">{start_label}</span>
                <span class="dt-mono" style="font-size:0.75rem; color:#9FB3C8;">{end_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_waveform(bar_count: int = 60, highlight_ranges: list[tuple] | None = None,
                     seed_key: str = "waveform") -> None:
    """Fake waveform (deterministic per session) with flagged index ranges highlighted."""
    highlight_ranges = highlight_ranges or []

    if seed_key not in st.session_state:
        rng = random.Random(seed_key)
        st.session_state[seed_key] = [rng.randint(15, 100) for _ in range(bar_count)]
    heights = st.session_state[seed_key]

    bars = ""
    for i, h in enumerate(heights):
        flagged = any(start <= i <= end for start, end in highlight_ranges)
        color = "#F87171" if flagged else "#4FD1C5"
        opacity = "0.9" if flagged else "0.5"
        bars += f'<div style="width:4px; height:{h}%; background:{color}; opacity:{opacity}; border-radius:2px;"></div>'

    st.markdown(
        f"""
        <div style="display:flex; align-items:flex-end; gap:2px; height:90px; padding:0.6rem;
                    background:rgba(255,255,255,0.03); border-radius:10px;
                    border:1px solid rgba(79,209,197,0.12);">
            {bars}
        </div>
        """,
        unsafe_allow_html=True,
    )
