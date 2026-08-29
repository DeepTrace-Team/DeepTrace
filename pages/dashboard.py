"""
DeepTrace History / Statistics Dashboard.

Uses mock history data for the dashboard and also includes
results generated during the current Streamlit session.

The dashboard displays:
- Total analyses
- High-risk analyses
- Average trust score
- Modality distribution
- Risk distribution
- Trust score trend
- Manipulation categories
- Recent analyses
"""

import pandas as pd
import streamlit as st

from assets.mock_data import generate_history
from assets.components import (
    RISK_COLORS,
    render_distribution_bar,
    render_history_row,
)


# -------------------------------------------------
# PAGE HEADER
# -------------------------------------------------

st.markdown(
    '<div class="dt-eyebrow">Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h2 class="dt-display">Overview</h2>',
    unsafe_allow_html=True,
)


# -------------------------------------------------
# SESSION RESULTS
# -------------------------------------------------

def _session_results_as_history() -> list[dict]:
    """
    Convert analysis results generated during the current
    Streamlit session into dashboard history format.
    """

    items = []


    # ---------------------------------------------
    # IMAGE RESULT
    # ---------------------------------------------

    img = st.session_state.get("last_result")

    if img:

        assessment = img.get(
            "assessment",
            {}
        )

        file_info = img.get(
            "file_info",
            {}
        )

        items.append(
            {
                "filename": file_info.get(
                    "filename",
                    "uploaded_image",
                ),

                "modality": "image",

                "classification": assessment.get(
                    "classification",
                    "Unknown",
                ),

                "risk_level": assessment.get(
                    "risk_level",
                    "LOW",
                ),

                "trust_score": assessment.get(
                    "trust_score",
                    0,
                ),

                "confidence": assessment.get(
                    "confidence",
                    0,
                ),

                "date": "Today",
            }
        )


    # ---------------------------------------------
    # VIDEO RESULT
    # ---------------------------------------------

    vid = st.session_state.get("video_result")

    if vid:

        assessment = vid.get(
            "assessment",
            {}
        )

        file_info = vid.get(
            "file_info",
            {}
        )

        items.append(
            {
                "filename": file_info.get(
                    "filename",
                    "uploaded_video.mp4",
                ),

                "modality": "video",

                "classification": assessment.get(
                    "classification",
                    "Unknown",
                ),

                "risk_level": assessment.get(
                    "risk_level",
                    "LOW",
                ),

                "trust_score": assessment.get(
                    "trust_score",
                    0,
                ),

                "confidence": assessment.get(
                    "confidence",
                    0,
                ),

                "date": "Today",
            }
        )


    # ---------------------------------------------
    # AUDIO RESULT
    # ---------------------------------------------

    aud = st.session_state.get("audio_result")

    if aud:

        assessment = aud.get(
            "assessment",
            {}
        )

        file_info = aud.get(
            "file_info",
            {}
        )

        items.append(
            {
                "filename": file_info.get(
                    "filename",
                    "uploaded_audio.wav",
                ),

                "modality": "audio",

                "classification": assessment.get(
                    "classification",
                    "Unknown",
                ),

                "risk_level": assessment.get(
                    "risk_level",
                    "LOW",
                ),

                "trust_score": assessment.get(
                    "trust_score",
                    0,
                ),

                "confidence": assessment.get(
                    "confidence",
                    0,
                ),

                "date": "Today",
            }
        )


    return items


# -------------------------------------------------
# LOAD DASHBOARD HISTORY
# -------------------------------------------------

session_history = _session_results_as_history()

mock_history = generate_history(
    n=18
)

history = (
    session_history
    + mock_history
)


# -------------------------------------------------
# TOP STATISTICS
# -------------------------------------------------

total = len(
    history
)

high_risk = sum(
    1
    for item in history
    if item.get(
        "risk_level",
        "",
    ).upper() == "HIGH"
)

avg_trust = round(
    sum(
        item.get(
            "trust_score",
            0,
        )
        for item in history
    )
    / total
) if total else 0


col1, col2, col3 = st.columns(
    3
)


stats = [
    (
        "Total analyses",
        str(total),
    ),

    (
        "High risk flagged",
        str(high_risk),
    ),

    (
        "Avg. trust score",
        f"{avg_trust}/100",
    ),
]


for column, (label, value) in zip(
    [
        col1,
        col2,
        col3,
    ],
    stats,
):

    with column:

        st.markdown(
            f'<div class="dt-card">'
            f'<div class="dt-eyebrow">{label}</div>'
            f'<h2 class="dt-display" '
            f'style="margin:0.3rem 0 0 0;">'
            f'{value}'
            f'</h2>'
            f'</div>',
            unsafe_allow_html=True,
        )


st.markdown(
    "<div style='height:1.5rem;'></div>",
    unsafe_allow_html=True,
)


# -------------------------------------------------
# DISTRIBUTIONS
# -------------------------------------------------

col_a, col_b = st.columns(
    2
)


# -------------------------------------------------
# MODALITY DISTRIBUTION
# -------------------------------------------------

with col_a:

    st.markdown(
        '<h3 class="dt-display">'
        'Modality distribution'
        '</h3>',
        unsafe_allow_html=True,
    )


    modality_colors = {

        "image":
            "#4FD1C5",

        "video":
            "#7C5CFC",

        "audio":
            "#FBBF24",

    }


    modality_counts = {}


    for item in history:

        modality = item.get(
            "modality",
            "unknown",
        ).lower()


        modality_counts[
            modality
        ] = (
            modality_counts.get(
                modality,
                0,
            )
            + 1
        )


    render_distribution_bar(

        [

            {

                "label":
                    modality.title(),

                "value":
                    count,

                "color":
                    modality_colors.get(
                        modality,
                        "#9FB3C8",
                    ),

            }

            for modality, count
            in modality_counts.items()

        ]

    )


# -------------------------------------------------
# RISK DISTRIBUTION
# -------------------------------------------------

with col_b:

    st.markdown(
        '<h3 class="dt-display">'
        'Risk distribution'
        '</h3>',
        unsafe_allow_html=True,
    )


    risk_counts = {}


    for item in history:

        risk = item.get(
            "risk_level",
            "LOW",
        ).upper()


        risk_counts[
            risk
        ] = (
            risk_counts.get(
                risk,
                0,
            )
            + 1
        )


    render_distribution_bar(

        [

            {

                "label":
                    risk.title(),

                "value":
                    count,

                "color":
                    RISK_COLORS.get(
                        risk,
                        "#9FB3C8",
                    ),

            }

            for risk, count
            in risk_counts.items()

        ]

    )


st.markdown(
    "<div style='height:0.75rem;'></div>",
    unsafe_allow_html=True,
)


# -------------------------------------------------
# TRUST SCORE TREND
# -------------------------------------------------

st.markdown(
    '<h3 class="dt-display">'
    'Trust score trend'
    '</h3>',
    unsafe_allow_html=True,
)


trend_rows = [

    item

    for item in history

    if (
        item.get("date") != "Today"
        and "date_obj" in item
    )

]


if trend_rows:

    df = pd.DataFrame(
        trend_rows
    )


    daily_avg = (

        df.groupby(
            df["date_obj"].dt.date
        )["trust_score"]

        .mean()

        .sort_index()

    )


    st.line_chart(
        daily_avg,
        height=200,
    )


else:

    st.markdown(
        '<div class="dt-card">'
        'Not enough history yet to chart a trend.'
        '</div>',
        unsafe_allow_html=True,
    )


st.markdown(
    "<div style='height:0.75rem;'></div>",
    unsafe_allow_html=True,
)


# -------------------------------------------------
# MANIPULATION CATEGORIES
# -------------------------------------------------

st.markdown(
    '<h3 class="dt-display">'
    'Manipulation categories'
    '</h3>',
    unsafe_allow_html=True,
)


category_counts = {}


for item in history:

    classification = item.get(
        "classification",
        "Unknown",
    )


    category_counts[
        classification
    ] = (

        category_counts.get(
            classification,
            0,
        )

        + 1

    )


category_colors = [

    "#4FD1C5",

    "#7C5CFC",

    "#FBBF24",

    "#F87171",

    "#34D399",

    "#9FB3C8",

]


render_distribution_bar(

    [

        {

            "label":
                label,

            "value":
                count,

            "color":
                category_colors[
                    index
                    % len(category_colors)
                ],

        }

        for index, (
            label,
            count,
        ) in enumerate(

            sorted(

                category_counts.items(),

                key=lambda item: item[1],

                reverse=True,

            )

        )

    ]

)


st.markdown(
    "<div style='height:1rem;'></div>",
    unsafe_allow_html=True,
)


# -------------------------------------------------
# RECENT ANALYSES
# -------------------------------------------------

st.markdown(
    '<h3 class="dt-display">'
    'Recent analyses'
    '</h3>',
    unsafe_allow_html=True,
)


for item in history[:8]:

    render_history_row(
        item
    )


# -------------------------------------------------
# SAVED REPORTS
# -------------------------------------------------

st.markdown(
    '<h3 class="dt-display" '
    'style="margin-top:1.5rem;">'
    'Saved reports'
    '</h3>',
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="dt-card">'
    'Forensic reports can be generated from the '
    'Results page after every completed analysis.'
    '</div>',
    unsafe_allow_html=True,
)