"""
DeepTrace Results Page.
"""

import streamlit as st

from assets.components import (
    render_assessment_card,
    render_evidence_list,
    render_metadata_findings,
)

from utils.report_generator import (
    generate_report,
)


def _md_html(html: str) -> str:
    """
    Strip leading whitespace from every line of an HTML block before
    handing it to st.markdown().

    Same fix as assets/components.py's _md_html: Streamlit's Markdown
    renderer treats any line indented 4+ spaces as a preformatted
    code block. The HTML blocks below are written with Python-source
    indentation for readability, which is invisible in this file but
    is literally part of the string passed to st.markdown() — without
    stripping it, these cards render as raw literal tags instead of
    HTML, even with unsafe_allow_html=True.
    """

    return "\n".join(
        line.lstrip()
        for line in html.strip("\n").splitlines()
    )


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    '<div class="dt-eyebrow">Results</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h2 class="dt-display" '
    'style="margin-top:0;">'
    'Analysis Results'
    '</h2>',
    unsafe_allow_html=True,
)


# ============================================================
# GET RESULT
# ============================================================

result = st.session_state.get(
    "current_result"
)


# ============================================================
# EMPTY STATE
# ============================================================

if not result:

    st.markdown(
        _md_html("""
        <div class="dt-card">

            <h3>No analysis yet</h3>

            <p style="color:#9FB3C8;">
                Upload an image, video, or audio file
                to see forensic results here.
            </p>

        </div>
        """),
        unsafe_allow_html=True,
    )

else:

    # ========================================================
    # ASSESSMENT
    # ========================================================

    st.markdown(
        '<h3 class="dt-display" '
        'style="margin-top:0;">'
        'Assessment'
        '</h3>',
        unsafe_allow_html=True,
    )

    # ========================================================
    # VIEW SELECTOR
    # ========================================================

    view = st.radio(
        "Result view",
        options=[
            "Simple View",
            "Forensic View",
        ],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    # ========================================================
    # ASSESSMENT CARD
    # ========================================================

    assessment = result.get(
        "assessment",
        {},
    )

    if not isinstance(
        assessment,
        dict,
    ):
        assessment = {}

    classification_upper = str(
        assessment.get(
            "classification",
            "",
        )
    ).upper().strip()

    # NOT_APPLICABLE / UNABLE_TO_EVALUATE mean the detector declined
    # to score the file at all — showing that through the normal
    # numeric card (confidence=0%, trust_score=0/100) reads exactly
    # like a maximally-untrustworthy verdict, which is misleading:
    # it's "no verdict available," not "high risk." Render a plain
    # status notice instead. (pages/audio_analysis.py already does
    # this same check for its own "already analyzed" view — this is
    # the same logic applied here too, since every analysis redirects
    # to this page immediately after completing, so this is the view
    # that actually needs it.)
    if classification_upper in {
        "NOT_APPLICABLE",
        "UNABLE_TO_EVALUATE",
    }:

        st.markdown(
            _md_html("""
            <div class="dt-card">

                <div class="dt-eyebrow">
                    Detection Status
                </div>

                <p style="
                    color:#9FB3C8;
                    margin-top:0.5rem;
                    margin-bottom:0;
                ">
                    The detector could not reliably evaluate this
                    file, so no authenticity score was generated.
                    This is not the same as a low-trust or high-risk
                    result — it simply means no verdict is available.
                    Check the evidence details below for the
                    detector's stated reason, if any.
                </p>

            </div>
            """),
            unsafe_allow_html=True,
        )

    else:

        render_assessment_card(
            assessment
        )

    # ========================================================
    # SIMPLE VIEW
    # ========================================================

    if view == "Simple View":

        evidence = result.get(
            "evidence",
            [],
        )

        if not isinstance(
            evidence,
            list,
        ):
            evidence = []

        evidence_count = len(
            evidence
        )

        signal_word = (
            "signal"
            if evidence_count == 1
            else "signals"
        )

        st.markdown(
            _md_html(f"""
            <p style="
                color:#9FB3C8;
                margin-top:1rem;
            ">
                Backed by {evidence_count}
                evidence {signal_word}.

                Select <b>Forensic View</b>
                above for the full breakdown.
            </p>
            """),
            unsafe_allow_html=True,
        )

    # ========================================================
    # FORENSIC VIEW
    # ========================================================

    else:

        # ====================================================
        # EVIDENCE
        # ====================================================

        st.markdown(
            '<h3 class="dt-display" '
            'style="margin-top:1.5rem;">'
            'Evidence'
            '</h3>',
            unsafe_allow_html=True,
        )

        evidence = result.get(
            "evidence",
            [],
        )

        if not isinstance(
            evidence,
            list,
        ):
            evidence = []

        if evidence:

            try:

                render_evidence_list(
                    evidence
                )

            except Exception as exc:

                st.error(
                    f"Unable to display evidence: {exc}"
                )

        else:

            st.info(
                "No evidence entries were returned."
            )

        # ====================================================
        # METADATA
        # ====================================================

        metadata = result.get(
            "metadata",
            {},
        )

        if metadata:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'Metadata'
                '</h3>',
                unsafe_allow_html=True,
            )

            try:

                render_metadata_findings(
                    metadata
                )

            except Exception as exc:

                st.error(
                    f"Unable to display metadata: {exc}"
                )

        # ====================================================
        # VIDEO SEGMENTS
        # ====================================================

        suspicious_segments = result.get(
            "suspicious_segments",
            [],
        )

        if not isinstance(
            suspicious_segments,
            list,
        ):
            suspicious_segments = []

        if suspicious_segments:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'Suspicious Video Segments'
                '</h3>',
                unsafe_allow_html=True,
            )

            for segment in suspicious_segments:

                if not isinstance(
                    segment,
                    dict,
                ):
                    continue

                severity = str(
                    segment.get(
                        "severity",
                        "UNKNOWN",
                    )
                ).upper()

                start_pct = segment.get(
                    "start_pct",
                    0,
                )

                end_pct = segment.get(
                    "end_pct",
                    0,
                )

                timestamp = segment.get(
                    "timestamp"
                )

                score = segment.get(
                    "score"
                )

                # --------------------------------------------
                # VIDEO SEGMENT CARD
                # --------------------------------------------

                details = (
                    f"From {start_pct}% to "
                    f"{end_pct}% of the video."
                )

                if timestamp is not None:

                    details += (
                        f" Timestamp: "
                        f"{timestamp}s."
                    )

                if score is not None:

                    try:

                        score_pct = round(
                            float(score) * 100
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        score_pct = None

                    if score_pct is not None:

                        details += (
                            f" Detection score: "
                            f"{score_pct}%."
                        )

                st.markdown(
                    _md_html(f"""
                    <div class="dt-card">

                        <div class="dt-eyebrow">
                            {severity} RISK
                        </div>

                        <p style="
                            margin:0.4rem 0 0 0;
                        ">
                            {details}
                        </p>

                    </div>
                    """),
                    unsafe_allow_html=True,
                )

        # ====================================================
        # AUDIO RANGES
        # ====================================================

        suspicious_ranges = result.get(
            "suspicious_ranges",
            [],
        )

        if not isinstance(
            suspicious_ranges,
            list,
        ):
            suspicious_ranges = []

        if suspicious_ranges:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'Flagged Audio Regions'
                '</h3>',
                unsafe_allow_html=True,
            )

            for audio_range in suspicious_ranges:

                if (
                    not isinstance(
                        audio_range,
                        (list, tuple),
                    )
                    or len(audio_range) < 2
                ):
                    continue

                start = audio_range[0]
                end = audio_range[1]

                st.markdown(
                    _md_html(f"""
                    <div class="dt-card">

                        <div class="dt-eyebrow">
                            FLAGGED REGION
                        </div>

                        <p style="
                            margin:0.4rem 0 0 0;
                        ">
                            {start}s – {end}s
                        </p>

                    </div>
                    """),
                    unsafe_allow_html=True,
                )

        # ====================================================
        # FILE INFORMATION
        # ====================================================

        file_info = result.get(
            "file_info",
            {},
        )

        if not isinstance(
            file_info,
            dict,
        ):
            file_info = {}

        if file_info:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'File Information'
                '</h3>',
                unsafe_allow_html=True,
            )

            for key, value in file_info.items():

                formatted_key = (
                    str(key)
                    .replace(
                        "_",
                        " ",
                    )
                    .title()
                )

                col1, col2 = st.columns(
                    [1, 2]
                )

                with col1:

                    st.markdown(
                        f"**{formatted_key}**"
                    )

                with col2:

                    st.code(
                        str(value),
                        language=None,
                    )

    # ========================================================
    # PDF REPORT
    # ========================================================

    st.markdown(
        '<h3 class="dt-display" '
        'style="margin-top:2rem;">'
        'Forensic Report'
        '</h3>',
        unsafe_allow_html=True,
    )

    st.markdown(
        _md_html("""
        <p style="color:#9FB3C8;">
            Generate a downloadable PDF containing
            the assessment, evidence signals,
            metadata findings, and flagged regions.
        </p>
        """),
        unsafe_allow_html=True,
    )

    try:

        pdf_buffer = generate_report(
            result
        )

        file_info = result.get(
            "file_info",
            {},
        )

        if not isinstance(
            file_info,
            dict,
        ):
            file_info = {}

        filename = file_info.get(
            "filename",
            "deeptrace_analysis",
        )

        safe_name = str(
            filename
        ).rsplit(
            ".",
            1,
        )[0]

        st.download_button(
            label="Download Forensic Report PDF",
            data=pdf_buffer,
            file_name=(
                f"{safe_name}"
                "_DeepTrace_Report.pdf"
            ),
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    except Exception as error:

        st.error(
            f"Unable to generate report: {error}"
        )