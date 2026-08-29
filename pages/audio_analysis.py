"""
Audio upload UI.

Uses mock data until the real audio_pipeline.py is connected.
"""

import streamlit as st

from utils.history_manager import save_analysis

from assets.components import (
    render_assessment_card,
    render_evidence_list,
    render_waveform,
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    '<div class="dt-eyebrow">Audio Analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h2 class="dt-display">Upload audio</h2>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded = st.file_uploader(
    "Audio file",
    type=["mp3", "wav", "m4a"],
    label_visibility="collapsed",
)


# --------------------------------------------------
# AUDIO PREVIEW + ANALYSIS
# --------------------------------------------------

if uploaded:

    col_preview, col_action = st.columns([2, 1])

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


    # --------------------------------------------------
    # RUN ANALYSIS
    # --------------------------------------------------

    if analyze:

        with st.status(
            "Analyzing...",
            expanded=True,
        ) as status:

            st.write("Validating audio")
            st.write("Preprocessing")
            st.write(
                "Running synthetic speech / spoof detection"
            )
            st.write("Collecting evidence")
            st.write("Calculating trust score")

            status.update(
                label="Analysis complete",
                state="complete",
            )


        # --------------------------------------------------
        # MOCK RESULT
        #
        # Replace later with:
        #
        # audio_result = analyze_audio(uploaded)
        # --------------------------------------------------

        audio_result = {

            "file_info": {

                "filename":
                    uploaded.name,

                "file_type":
                    uploaded.type,

                "size":
                    f"{uploaded.size / 1024:.1f} KB",

            },

            "assessment": {

                "classification":
                    "Likely Voice Clone",

                "confidence":
                    88.0,

                "trust_score":
                    22,

                "risk_level":
                    "HIGH",

            },

            "suspicious_ranges": [

                (14, 27),

                (40, 46),

            ],

            "evidence": [

                {

                    "source":
                        "Spoof Detector",

                    "score":
                        0.88,

                    "explanation": (
                        "Spectral characteristics consistent "
                        "with neural voice synthesis."
                    ),

                },

                {

                    "source":
                        "Prosody Analysis",

                    "score":
                        0.57,

                    "explanation": (
                        "Unnaturally uniform pacing across "
                        "sentence boundaries."
                    ),

                },

            ],

        }


        # --------------------------------------------------
        # SAVE AUDIO-SPECIFIC RESULT
        # --------------------------------------------------

        st.session_state[
            "audio_result"
        ] = audio_result


        # --------------------------------------------------
        # SAVE UNIVERSAL RESULT
        # --------------------------------------------------

        st.session_state[
            "current_result"
        ] = {

            **audio_result,

            "modality":
                "audio",

        }


        # --------------------------------------------------
        # SAVE TO PERSISTENT HISTORY
        # --------------------------------------------------

        save_analysis(
            audio_result,
            "audio",
        )


        # --------------------------------------------------
        # GO TO RESULTS PAGE
        # --------------------------------------------------

        st.switch_page(
            "pages/results.py"
        )


# --------------------------------------------------
# SHOW RESULT ON AUDIO PAGE
# --------------------------------------------------

if "audio_result" in st.session_state:

    ar = st.session_state[
        "audio_result"
    ]

    st.markdown(
        '<h3 class="dt-display" '
        'style="margin-top:1.5rem;">'
        'Waveform'
        '</h3>',
        unsafe_allow_html=True,
    )

    render_waveform(
        bar_count=60,
        highlight_ranges=ar["suspicious_ranges"],
        seed_key="audio_waveform",
    )

    st.markdown(
        """
        <p style="color:#9FB3C8;
                  font-size:0.85rem;">
            Highlighted regions indicate segments
            flagged as likely synthetic.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h3 class="dt-display" '
        'style="margin-top:1.5rem;">'
        'Assessment'
        '</h3>',
        unsafe_allow_html=True,
    )

    render_assessment_card(
        ar["assessment"]
    )

    with st.expander(
        "Evidence details"
    ):

        render_evidence_list(
            ar["evidence"]
        )


elif not uploaded:

    st.info(
        "Upload an audio file to begin."
    )