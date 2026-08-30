"""
DeepTrace Audio Analysis Page.
"""

import tempfile
from pathlib import Path

import streamlit as st

from pipelines.audio_pipeline import (
    analyze_audio,
)

from utils.history_manager import (
    save_analysis,
)

from assets.components import (
    render_assessment_card,
    render_evidence_list,
    render_waveform,
)


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    '<div class="dt-eyebrow">'
    'Audio Analysis'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h2 class="dt-display">'
    'Upload audio'
    '</h2>',
    unsafe_allow_html=True,
)


# ============================================================
# UPLOAD
# ============================================================

uploaded = st.file_uploader(
    "Audio file",
    type=[
        "mp3",
        "wav",
        "m4a",
        "aac",
        "ogg",
        "flac",
    ],
    label_visibility="collapsed",
)


# ============================================================
# AUDIO PREVIEW
# ============================================================

if uploaded:

    col_preview, col_action = (
        st.columns(
            [2, 1]
        )
    )

    with col_preview:

        st.audio(
            uploaded
        )

    with col_action:

        st.markdown(
            '<div class="dt-card">',
            unsafe_allow_html=True,
        )

        st.write(
            f"**File:** {uploaded.name}"
        )

        st.write(
            f"**Size:** "
            f"{uploaded.size / 1024:.1f} KB"
        )

        analyze = st.button(
            "Run analysis",
            type="primary",
            use_container_width=True,
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

    # ========================================================
    # RUN ANALYSIS
    # ========================================================

    if analyze:

        audio_result = None
        temp_path: Path | None = None

        with st.status(
            "Analyzing...",
            expanded=True,
        ) as status:

            try:

                st.write(
                    "Saving upload..."
                )

                suffix = (
                    Path(
                        uploaded.name
                    ).suffix.lower()
                    or ".wav"
                )

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:

                    temp_file.write(
                        uploaded.getvalue()
                    )

                    temp_path = Path(
                        temp_file.name
                    )

                st.write(
                    "Extracting technical properties..."
                )

                st.write(
                    "Sending audio to Reality Defender..."
                )

                st.write(
                    "Waiting for detector response..."
                )

                analysis_result = (
                    analyze_audio(
                        temp_path
                    )
                )

                audio_result = (
                    analysis_result.to_dict()
                )

                # ------------------------------------------------
                # RESTORE ORIGINAL FILE INFO
                # ------------------------------------------------

                audio_result[
                    "file_info"
                ] = {

                    **audio_result.get(
                        "file_info",
                        {},
                    ),

                    "filename":
                        uploaded.name,

                    "file_type":
                        uploaded.type,

                    "size":
                        f"{uploaded.size / 1024:.1f} KB",
                }

                status.update(
                    label="Analysis complete",
                    state="complete",
                )

            except Exception as error:

                status.update(
                    label="Analysis failed",
                    state="error",
                )

                st.error(
                    f"Audio analysis failed: "
                    f"{error}"
                )

            finally:

                if temp_path is not None:

                    temp_path.unlink(
                        missing_ok=True
                    )

        # ====================================================
        # SAVE RESULT
        # ====================================================

        if audio_result is not None:

            st.session_state[
                "audio_result"
            ] = audio_result

            st.session_state[
                "current_result"
            ] = {

                **audio_result,

                "modality":
                    "audio",
            }

            save_analysis(
                audio_result,
                "audio",
            )

            st.switch_page(
                "pages/results.py"
            )


# ============================================================
# SHOW EXISTING RESULT
# ============================================================

if "audio_result" in st.session_state:

    ar = st.session_state[
        "audio_result"
    ]

    assessment = ar.get(
        "assessment",
        {},
    )

    classification = str(
        assessment.get(
            "classification",
            "UNKNOWN",
        )
    ).upper()

    # ========================================================
    # NOT APPLICABLE
    # ========================================================

    if classification == "NOT_APPLICABLE":

        st.markdown(
            '<h3 class="dt-display" '
            'style="margin-top:1.5rem;">'
            'Detection Status'
            '</h3>',
            unsafe_allow_html=True,
        )

        st.warning(
            "Reality Defender could not reliably "
            "evaluate this audio file. "
            "No authenticity score was generated."
        )

    # ========================================================
    # NORMAL RESULT
    # ========================================================

    else:

        st.markdown(
            '<h3 class="dt-display" '
            'style="margin-top:1.5rem;">'
            'Assessment'
            '</h3>',
            unsafe_allow_html=True,
        )

        render_assessment_card(
            assessment
        )

    # ========================================================
    # WAVEFORM
    # ========================================================

    suspicious_ranges = ar.get(
        "suspicious_ranges",
        [],
    )

    st.markdown(
        '<h3 class="dt-display" '
        'style="margin-top:1.5rem;">'
        'Waveform'
        '</h3>',
        unsafe_allow_html=True,
    )

    render_waveform(
        bar_count=60,
        highlight_ranges=(
            suspicious_ranges
            if isinstance(
                suspicious_ranges,
                list,
            )
            else []
        ),
        seed_key="audio_waveform",
    )

    if suspicious_ranges:

        st.markdown(
            """
            <p style="
                color:#9FB3C8;
                font-size:0.85rem;
            ">
                Highlighted regions indicate
                segments flagged by the detector.
            </p>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <p style="
                color:#9FB3C8;
                font-size:0.85rem;
            ">
                The current Reality Defender integration
                does not provide region-level timestamps
                through this pipeline.
            </p>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # EVIDENCE
    # ========================================================

    st.markdown(
        '<h3 class="dt-display" '
        'style="margin-top:1.5rem;">'
        'Evidence'
        '</h3>',
        unsafe_allow_html=True,
    )

    with st.expander(
        "Evidence details",
        expanded=False,
    ):

        render_evidence_list(
            ar.get(
                "evidence",
                [],
            )
        )


elif not uploaded:

    st.info(
        "Upload an audio file to begin."
    )