"""
DeepTrace Results Page.

Displays the latest analysis result for image, video, or audio
and allows the user to download a forensic PDF report.
"""

import streamlit as st

from assets.components import (
    render_assessment_card,
    render_evidence_list,
    render_metadata_findings,
)

from utils.report_generator import generate_report


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    '<div class="dt-eyebrow">Results</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# GET CURRENT RESULT
# --------------------------------------------------

result = st.session_state.get(
    "current_result"
)


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

if not result:

    st.markdown(
        """
        <div class="dt-card">
            No analysis yet.

            Upload an image, video, or audio file
            to see forensic results here.
        </div>
        """,
        unsafe_allow_html=True,
    )


else:

    # --------------------------------------------------
    # ASSESSMENT
    # --------------------------------------------------

    st.markdown(
        '<h2 class="dt-display" style="margin-top:0;">'
        'Assessment'
        '</h2>',
        unsafe_allow_html=True,
    )


    view = st.radio(
        "View",
        [
            "Simple View",
            "Forensic View",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )


    render_assessment_card(
        result.get(
            "assessment",
            {},
        )
    )


    # --------------------------------------------------
    # SIMPLE VIEW
    # --------------------------------------------------

    if view == "Simple View":

        evidence = result.get(
            "evidence",
            [],
        )

        evidence_count = len(
            evidence
        )

        st.markdown(
            f"""
            <p style="color:#9FB3C8;">
                Backed by {evidence_count} evidence
                {"signal" if evidence_count == 1 else "signals"}.
                Switch to Forensic View for the full breakdown.
            </p>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------
    # FORENSIC VIEW
    # --------------------------------------------------

    else:

        # ---------------- EVIDENCE ----------------

        st.markdown(
            '<h3 class="dt-display" '
            'style="margin-top:1.5rem;">'
            'Evidence'
            '</h3>',
            unsafe_allow_html=True,
        )

        render_evidence_list(
            result.get(
                "evidence",
                [],
            )
        )


        # ---------------- METADATA ----------------

        metadata = result.get(
            "metadata",
            {}
        )

        if metadata:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'Metadata'
                '</h3>',
                unsafe_allow_html=True,
            )

            render_metadata_findings(
                metadata
            )


        # ---------------- VIDEO SEGMENTS ----------------

        suspicious_segments = result.get(
            "suspicious_segments",
            []
        )

        if suspicious_segments:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'Suspicious Video Segments'
                '</h3>',
                unsafe_allow_html=True,
            )

            for segment in suspicious_segments:

                st.markdown(
                    f"""
                    <div class="dt-card">
                        <div class="dt-eyebrow">
                            {segment.get("severity", "UNKNOWN")} RISK
                        </div>

                        <p style="margin:0.4rem 0 0 0;">
                            From {segment.get("start_pct", 0)}%
                            to {segment.get("end_pct", 0)}%
                            of the video.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


        # ---------------- AUDIO RANGES ----------------

        suspicious_ranges = result.get(
            "suspicious_ranges",
            []
        )

        if suspicious_ranges:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'Flagged Audio Regions'
                '</h3>',
                unsafe_allow_html=True,
            )

            for start, end in suspicious_ranges:

                st.markdown(
                    f"""
                    <div class="dt-card">
                        <div class="dt-eyebrow">
                            FLAGGED REGION
                        </div>

                        <p style="margin:0.4rem 0 0 0;">
                            {start}s – {end}s
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


        # ---------------- FILE INFO ----------------

        file_info = result.get(
            "file_info",
            {}
        )

        if file_info:

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'File Information'
                '</h3>',
                unsafe_allow_html=True,
            )

            info_cols = st.columns(
                len(file_info)
            )

            for column, (
                key,
                value,
            ) in zip(
                info_cols,
                file_info.items(),
            ):

                with column:

                    st.markdown(
                        f"""
                        <div class="dt-card">

                            <div class="dt-eyebrow">
                                {key.replace("_", " ").title()}
                            </div>

                            <p class="dt-mono"
                               style="margin:0.3rem 0 0 0;">
                                {value}
                            </p>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


    # --------------------------------------------------
    # PDF REPORT DOWNLOAD
    # --------------------------------------------------

    st.markdown(
        '<h3 class="dt-display" '
        'style="margin-top:2rem;">'
        'Forensic Report'
        '</h3>',
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <p style="color:#9FB3C8;">
            Generate a downloadable PDF containing the assessment,
            evidence signals, metadata findings, and flagged regions.
        </p>
        """,
        unsafe_allow_html=True,
    )


    try:

        pdf_buffer = generate_report(
            result
        )

        file_info = result.get(
            "file_info",
            {}
        )

        filename = file_info.get(
            "filename",
            "deeptrace_analysis"
        )

        safe_name = filename.rsplit(
            ".",
            1,
        )[0]


        st.download_button(
            label="Download Forensic Report PDF",
            data=pdf_buffer,
            file_name=f"{safe_name}_DeepTrace_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )


    except Exception as error:

        st.error(
            f"Unable to generate report: {error}"
        )