"""
DeepTrace History / Statistics Dashboard.

Reads real analysis history persisted by every completed analysis
(utils.history_manager.save_analysis, called from the image, video,
and audio pages) via load_history(). No mock data — a fresh install
with no analyses yet shows an explicit empty state instead of fake
numbers.

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

from datetime import datetime

import pandas as pd
import streamlit as st

from assets.components import (
    RISK_COLORS,
    render_distribution_bar,
    render_history_row,
)
from utils.history_manager import clear_history, load_history


def _md_html(html: str) -> str:
    """
    Strip leading whitespace from every line of an HTML block before
    handing it to st.markdown().

    Same fix as assets/components.py's _md_html: Streamlit's Markdown
    renderer treats any line indented 4+ spaces as a preformatted
    code block. Indented triple-quoted HTML strings hit this even
    with unsafe_allow_html=True set correctly.
    """

    return "\n".join(
        line.lstrip()
        for line in html.strip("\n").splitlines()
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
# REAL PERSISTED HISTORY
# -------------------------------------------------

def _persisted_history_as_dashboard_rows() -> list[dict]:
    """
    Convert entries from load_history() (saved by save_analysis()
    after every completed image/video/audio analysis) into the
    row shape the dashboard's rendering below expects — mainly
    adding date_obj / date, which persisted entries store as a
    single ISO `timestamp` string rather than pre-split fields.
    """

    rows = []

    for entry in load_history():

        timestamp = entry.get("timestamp")

        date_obj = None

        if timestamp:

            try:
                date_obj = datetime.fromisoformat(timestamp)
            except (ValueError, TypeError):
                date_obj = None

        is_today = (
            date_obj is not None
            and date_obj.date() == datetime.now().date()
        )

        rows.append(
            {
                **entry,
                "date_obj": date_obj,
                "date": (
                    "Today"
                    if is_today
                    else (
                        date_obj.strftime("%b %d")
                        if date_obj
                        else "Unknown"
                    )
                ),
            }
        )

    return rows


# -------------------------------------------------
# LOAD DASHBOARD HISTORY
# -------------------------------------------------

# Real history only — save_analysis() runs immediately after every
# completed analysis on the image/video/audio pages, so this already
# includes everything the app has ever produced, not just this
# session. No mock padding: a fresh install with nothing analyzed
# yet gets an explicit empty state below instead of fake entries.
history = _persisted_history_as_dashboard_rows()


# -------------------------------------------------
# EMPTY STATE
# -------------------------------------------------

if not history:

    st.markdown(
        _md_html("""
        <div class="dt-card">

            <h3>No analyses yet</h3>

            <p style="color:#9FB3C8; margin:0;">
                Run an image, video, or audio analysis and it'll
                show up here.
            </p>

        </div>
        """),
        unsafe_allow_html=True,
    )

    st.stop()


# -------------------------------------------------
# TOP STATISTICS
# -------------------------------------------------

total = len(
    history
)

high_risk = sum(
    1
    for item in history
    if str(
        item.get(
            "risk_level",
            "",
        )
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

        modality = str(
            item.get(
                "modality",
                "unknown",
            )
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

        risk = str(
            item.get(
                "risk_level",
                "LOW",
            )
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
        and item.get("date_obj") is not None
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


# -------------------------------------------------
# FLUSH HISTORY
# -------------------------------------------------

st.markdown(
    "<div style='height:1.5rem;'></div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<h3 class="dt-display">'
    'Danger zone'
    '</h3>',
    unsafe_allow_html=True,
)

st.markdown(
    _md_html("""
    <p style="color:#9FB3C8; margin-bottom:0.75rem;">
        Permanently deletes every saved analysis from
        data/analysis_history.json. This can't be undone.
    </p>
    """),
    unsafe_allow_html=True,
)


@st.dialog("Clear all history?")
def _confirm_clear_history() -> None:

    st.write(
        f"This permanently deletes all {total} saved "
        "analyses. This can't be undone."
    )

    col_cancel, col_confirm = st.columns(2)

    with col_cancel:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):
            st.rerun()

    with col_confirm:

        if st.button(
            "Clear history",
            type="primary",
            use_container_width=True,
        ):

            if clear_history():
                st.toast(
                    "History cleared.",
                    icon="\U0001F5D1\uFE0F",
                )
            else:
                st.toast(
                    "Couldn't clear history — check "
                    "file permissions.",
                    icon="\u26A0\uFE0F",
                )

            st.rerun()


if st.button(
    "Flush history",
):

    _confirm_clear_history()