"""
DeepTrace UI Components.

Reusable Streamlit components for:
- Assessment cards
- Evidence lists
- Metadata findings
- Waveforms / distribution bars / history rows (dashboard + audio page)
"""

from __future__ import annotations

import random
from typing import Any

import streamlit as st


# ============================================================
# SHARED CONSTANTS
# ============================================================

RISK_COLORS = {
    "HIGH": "#F87171",
    "MEDIUM": "#FBBF24",
    "LOW": "#34D399",
}


# ============================================================
# HELPERS
# ============================================================

def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """Safely convert a value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Clamp a number between minimum and maximum."""

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _escape_html(value: Any) -> str:
    """Basic HTML escaping for values inserted into UI."""

    text = str(value)

    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _md_html(html: str) -> str:
    """
    Strip leading whitespace from every line of an HTML block before
    handing it to st.markdown().

    Standard Markdown (which Streamlit's renderer follows) treats any
    line indented 4+ spaces as a preformatted code block. HTML blocks
    in this file are written with Python-source-level indentation for
    readability, which is invisible in the .py file but is literally
    part of the string passed to st.markdown() — without stripping it,
    cards render as raw literal tags in a code block instead of as
    HTML, even with unsafe_allow_html=True set correctly. HTML doesn't
    care about whitespace between tags, so stripping it per-line is
    safe and doesn't change how anything looks once it renders.
    """

    return "\n".join(
        line.lstrip()
        for line in html.strip("\n").splitlines()
    )


# ============================================================
# ASSESSMENT CARD
# ============================================================

def render_assessment_card(
    assessment: dict[str, Any],
) -> None:
    """
    Render the main DeepTrace assessment card.

    Expected assessment structure:

    {
        "classification": "authentic",
        "confidence": 0.92,
        "trust_score": 92,
        "risk_level": "low"
    }
    """

    if not isinstance(
        assessment,
        dict,
    ):
        assessment = {}

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    classification = str(
        assessment.get(
            "classification",
            "unknown",
        )
    ).strip().upper()

    if not classification:
        classification = "UNKNOWN"

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = _safe_float(
        assessment.get(
            "confidence",
            0.0,
        )
    )

    # Support both:
    # 0.92
    # and
    # 92

    if confidence > 1:
        confidence = confidence / 100.0

    confidence = _clamp(
        confidence
    )

    confidence_pct = round(
        confidence * 100
    )

    # --------------------------------------------------------
    # TRUST SCORE
    # --------------------------------------------------------

    trust_score = _safe_float(
        assessment.get(
            "trust_score",
            confidence_pct,
        )
    )

    # Support both:
    # 0.92
    # and
    # 92

    if trust_score <= 1:
        trust_score = trust_score * 100.0

    trust_score = max(
        0.0,
        min(
            100.0,
            trust_score,
        ),
    )

    trust_pct = round(
        trust_score
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    risk_level = str(
        assessment.get(
            "risk_level",
            "",
        )
    ).strip().upper()

    if not risk_level:

        if trust_pct >= 67:
            risk_level = "LOW"

        elif trust_pct >= 34:
            risk_level = "MEDIUM"

        else:
            risk_level = "HIGH"

    # --------------------------------------------------------
    # COLOR / VISUAL STATE
    # --------------------------------------------------------

    risk_color = RISK_COLORS.get(
        risk_level,
        "#9FB3C8",
    )

    # --------------------------------------------------------
    # CARD
    # --------------------------------------------------------

    st.markdown(
        _md_html(f"""
        <div class="dt-card"
             style="
                margin-top:0.75rem;
                margin-bottom:1rem;
             ">

            <span class="dt-mono"
                  style="
                    color:{risk_color};
                    font-size:0.82rem;
                    letter-spacing:0.08em;
                  ">
                {_escape_html(risk_level)} RISK
            </span>

            <h2 class="dt-display"
                style="
                    margin:0.35rem 0;
                ">
                {_escape_html(classification)}
            </h2>

            <div class="dt-eyebrow">
                Authenticity Confidence
            </div>

            <div style="
                font-size:2rem;
                font-weight:700;
                margin-top:0.4rem;
            ">
                {confidence_pct}%
            </div>

            <p style="
                color:#9FB3C8;
                margin-top:0.5rem;
                margin-bottom:1.2rem;
            ">
                Trust Score: {trust_pct}/100
            </p>

            <div style="
                display:flex;
                justify-content:space-between;
                margin-bottom:0.4rem;
            ">

                <span class="dt-mono"
                      style="
                        font-size:0.78rem;
                        color:#9FB3C8;
                        letter-spacing:0.08em;
                      ">
                    TRUST SCORE
                </span>

                <span class="dt-mono"
                      style="
                        font-size:0.78rem;
                        color:{risk_color};
                      ">
                    {trust_pct}/100
                </span>

            </div>

            <div style="
                position:relative;
                height:10px;
                border-radius:6px;
                background:
                    linear-gradient(
                        90deg,
                        rgba(248,113,113,0.45) 0%,
                        rgba(248,113,113,0.45) 33%,
                        rgba(251,191,36,0.45) 33%,
                        rgba(251,191,36,0.45) 66%,
                        rgba(52,211,153,0.45) 66%,
                        rgba(52,211,153,0.45) 100%
                    );
            ">

                <div style="
                    position:absolute;
                    top:-3px;
                    left:calc({trust_pct}% - 2px);
                    width:4px;
                    height:16px;
                    background:#fff;
                    border-radius:2px;
                    box-shadow:
                        0 0 8px 2px
                        rgba(255,255,255,0.7);
                "></div>

            </div>

        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================
# EVIDENCE LIST
# ============================================================

def render_evidence_list(
    evidence: list[Any],
) -> None:
    """
    Render forensic evidence entries.
    """

    if not isinstance(
        evidence,
        list,
    ):
        evidence = []

    if not evidence:

        st.info(
            "No evidence entries were returned."
        )

        return

    for index, item in enumerate(
        evidence,
        start=1,
    ):

        # ----------------------------------------------------
        # NORMALIZE
        # ----------------------------------------------------

        if isinstance(
            item,
            dict,
        ):

            source = item.get(
                "source",
                "Unknown source",
            )

            modality = item.get(
                "modality",
                "Unknown",
            )

            evidence_type = item.get(
                "type",
                item.get(
                    "evidence_type",
                    "Detection signal",
                ),
            )

            score = item.get(
                "score",
                0.0,
            )

            confidence = item.get(
                "confidence",
                0.0,
            )

            timestamp = item.get(
                "timestamp",
            )

            explanation = item.get(
                "explanation",
                "No explanation provided.",
            )

        else:

            source = "Unknown"
            modality = "Unknown"
            evidence_type = "Detection signal"
            score = 0.0
            confidence = 0.0
            timestamp = None
            explanation = str(item)

        # ----------------------------------------------------
        # NORMALIZE SCORES
        # ----------------------------------------------------

        score = _safe_float(
            score
        )

        confidence = _safe_float(
            confidence
        )

        if score <= 1:
            score_pct = round(
                _clamp(score) * 100
            )
        else:
            score_pct = round(
                max(
                    0.0,
                    min(
                        100.0,
                        score,
                    ),
                )
            )

        if confidence <= 1:
            confidence_pct = round(
                _clamp(confidence) * 100
            )
        else:
            confidence_pct = round(
                max(
                    0.0,
                    min(
                        100.0,
                        confidence,
                    ),
                )
            )

        # ----------------------------------------------------
        # SCORE COLOR
        # ----------------------------------------------------

        if score_pct >= 67:

            score_color = "#F87171"

        elif score_pct >= 34:

            score_color = "#FBBF24"

        else:

            score_color = "#34D399"

        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp_html = ""

        if timestamp is not None:

            timestamp_html = _md_html(f"""
                <div style="
                    color:#9FB3C8;
                    font-size:0.78rem;
                    margin-top:0.25rem;
                ">
                    Timestamp: {_escape_html(timestamp)}
                </div>
            """)

        # ----------------------------------------------------
        # CARD
        # ----------------------------------------------------

        st.markdown(
            _md_html(f"""
            <div class="dt-card"
                 style="
                    margin-bottom:0.75rem;
                 ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:flex-start;
                    gap:1rem;
                ">

                    <div>

                        <div class="dt-eyebrow">
                            EVIDENCE {index}
                        </div>

                        <h4 style="
                            margin:0.35rem 0 0.2rem 0;
                        ">
                            {_escape_html(evidence_type)}
                        </h4>

                        <div style="
                            color:#9FB3C8;
                            font-size:0.82rem;
                        ">
                            Source:
                            {_escape_html(source)}
                        </div>

                        <div style="
                            color:#9FB3C8;
                            font-size:0.82rem;
                        ">
                            Modality:
                            {_escape_html(modality)}
                        </div>

                        {timestamp_html}

                    </div>

                    <div style="
                        text-align:right;
                        min-width:80px;
                    ">

                        <div class="dt-mono"
                             style="
                                color:{score_color};
                                font-size:1.15rem;
                                font-weight:700;
                             ">
                            {score_pct}%
                        </div>

                        <div style="
                            color:#9FB3C8;
                            font-size:0.72rem;
                            margin-top:0.15rem;
                        ">
                            SIGNAL
                        </div>

                    </div>

                </div>

                <div style="
                    margin-top:0.85rem;
                    padding-top:0.75rem;
                    border-top:
                        1px solid
                        rgba(255,255,255,0.06);
                ">

                    <p style="
                        color:#C5D1DE;
                        margin:0;
                        line-height:1.55;
                    ">
                        {_escape_html(explanation)}
                    </p>

                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    margin-top:0.75rem;
                ">

                    <span class="dt-mono"
                          style="
                            color:#9FB3C8;
                            font-size:0.72rem;
                            letter-spacing:0.06em;
                          ">
                        DETECTOR CONFIDENCE
                    </span>

                    <span class="dt-mono"
                          style="
                            color:#9FB3C8;
                            font-size:0.72rem;
                          ">
                        {confidence_pct}%
                    </span>

                </div>

            </div>
            """),
            unsafe_allow_html=True,
        )


# ============================================================
# METADATA FINDINGS
# ============================================================

def render_metadata_findings(
    metadata: dict[str, Any],
) -> None:
    """
    Render technical metadata findings.
    """

    if not isinstance(
        metadata,
        dict,
    ):
        st.info(
            "No metadata information available."
        )
        return

    available = metadata.get(
        "available",
        False,
    )

    findings = metadata.get(
        "findings",
        [],
    )

    if not isinstance(
        findings,
        list,
    ):
        findings = []

    # --------------------------------------------------------
    # UNAVAILABLE
    # --------------------------------------------------------

    if not available:

        st.markdown(
            _md_html("""
            <div class="dt-card">

                <p style="
                    color:#9FB3C8;
                    margin:0;
                ">
                    Technical metadata was not available
                    for this file.
                </p>

            </div>
            """),
            unsafe_allow_html=True,
        )

        return

    # --------------------------------------------------------
    # AVAILABLE BUT EMPTY
    # --------------------------------------------------------

    if not findings:

        st.markdown(
            _md_html("""
            <div class="dt-card">

                <p style="
                    color:#9FB3C8;
                    margin:0;
                ">
                    Metadata was available, but no
                    technical findings were returned.
                </p>

            </div>
            """),
            unsafe_allow_html=True,
        )

        return

    # --------------------------------------------------------
    # FINDINGS
    # --------------------------------------------------------

    for index, finding in enumerate(
        findings,
        start=1,
    ):

        st.markdown(
            _md_html(f"""
            <div class="dt-card"
                 style="
                    margin-bottom:0.6rem;
                 ">

                <div style="
                    display:flex;
                    align-items:flex-start;
                    gap:0.75rem;
                ">

                    <div class="dt-mono"
                         style="
                            color:#4FD1C5;
                            font-size:0.78rem;
                            min-width:28px;
                         ">
                        {index:02d}
                    </div>

                    <div style="
                        color:#C5D1DE;
                        line-height:1.5;
                    ">
                        {_escape_html(finding)}
                    </div>

                </div>

            </div>
            """),
            unsafe_allow_html=True,
        )


# ============================================================
# WAVEFORM (used by pages/audio_analysis.py)
# ============================================================

def render_waveform(
    bar_count: int = 60,
    highlight_ranges: list[tuple] | None = None,
    seed_key: str = "waveform",
) -> None:
    """
    Deterministic-per-session fake waveform, with optional index
    ranges highlighted (used to show flagged regions when real
    per-region data is available).
    """

    highlight_ranges = highlight_ranges or []

    if seed_key not in st.session_state:
        rng = random.Random(seed_key)
        st.session_state[seed_key] = [
            rng.randint(15, 100) for _ in range(bar_count)
        ]

    heights = st.session_state[seed_key]

    bars = ""

    for i, h in enumerate(heights):

        flagged = any(
            start <= i <= end
            for start, end in highlight_ranges
        )

        color = "#F87171" if flagged else "#4FD1C5"
        opacity = "0.9" if flagged else "0.5"

        bars += (
            f'<div style="width:4px; height:{h}%; '
            f'background:{color}; opacity:{opacity}; '
            f'border-radius:2px;"></div>'
        )

    st.markdown(
        _md_html(f"""
        <div style="display:flex; align-items:flex-end; gap:2px; height:90px; padding:0.6rem;
                    background:rgba(255,255,255,0.03); border-radius:10px;
                    border:1px solid rgba(79,209,197,0.12);">
            {bars}
        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================
# DISTRIBUTION BAR (used by pages/dashboard.py)
# ============================================================

def render_distribution_bar(
    items: list[dict],
) -> None:
    """
    Segmented horizontal bar + legend.

    items: [{label, value, color}]
    """

    total = sum(i["value"] for i in items) or 1

    segments = ""
    legend = ""

    for i in items:

        pct = round(i["value"] / total * 100, 1)

        segments += (
            f'<div style="width:{pct}%; '
            f'background:{i["color"]};"></div>'
        )

        legend += (
            '<div style="display:flex; align-items:center; '
            'gap:0.4rem; margin-right:1.2rem; margin-bottom:0.3rem;">'
            f'<span style="width:10px; height:10px; border-radius:3px; '
            f'background:{i["color"]}; display:inline-block;"></span>'
            f'<span style="color:#C4D0DC; font-size:0.9rem;">'
            f'{_escape_html(i["label"])} \u00b7 {i["value"]} ({pct}%)</span>'
            '</div>'
        )

    st.markdown(
        _md_html(f"""
        <div style="display:flex; height:14px; border-radius:7px; overflow:hidden; margin-bottom:0.75rem;">
            {segments}
        </div>
        <div style="display:flex; flex-wrap:wrap;">{legend}</div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================
# HISTORY ROW (used by pages/dashboard.py)
# ============================================================

def render_history_row(
    item: dict,
) -> None:
    """
    One row in a recent-analyses list.

    item needs: filename, modality, classification, risk_level,
    trust_score, date.
    """

    color = RISK_COLORS.get(
        str(item.get("risk_level", "LOW")).upper(),
        "#4FD1C5",
    )

    icon = {
        "image": "\U0001F5BC\uFE0F",
        "video": "\U0001F3AC",
        "audio": "\U0001F399\uFE0F",
    }.get(
        item.get("modality"),
        "\U0001F4C4",
    )

    st.markdown(
        _md_html(f"""
        <div class="dt-card" style="display:flex; justify-content:space-between; align-items:center;
                    margin-bottom:0.6rem; padding:0.9rem 1.2rem;">
            <div style="display:flex; align-items:center; gap:0.8rem;">
                <span style="font-size:1.3rem;">{icon}</span>
                <div>
                    <div style="font-weight:600;">{_escape_html(item.get('filename', 'unknown'))}</div>
                    <div style="color:#9FB3C8; font-size:0.85rem;">
                        {_escape_html(item.get('classification', ''))} \u00b7 {_escape_html(item.get('date', ''))}
                    </div>
                </div>
            </div>
            <div style="text-align:right;">
                <div class="dt-mono" style="color:{color}; font-size:0.85rem;">{_escape_html(item.get('risk_level', ''))}</div>
                <div class="dt-mono" style="font-size:0.85rem; color:#9FB3C8;">
                    {item.get('trust_score', 0)}/100
                </div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )