"""
DeepTrace Video Analysis Page.

Uploads a video, validates the 200 MB application limit,
runs the Hive V3 video detector, saves the normalized result,
and redirects to the Results page.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from pipelines.video_pipeline import analyze_video
from utils.history_manager import save_analysis


# ============================================================
# CONFIGURATION
# ============================================================

MAX_VIDEO_SIZE_MB = 200
MAX_VIDEO_SIZE_BYTES = (
    MAX_VIDEO_SIZE_MB * 1024 * 1024
)


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    '<div class="dt-eyebrow">Video Analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<h2 class="dt-display">'
    'Upload video'
    '</h2>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="
        color:#9FB3C8;
        margin-top:-0.5rem;
    ">
        Analyze videos for potential AI generation,
        deepfake manipulation, and visual inconsistencies.
        Maximum file size: 200 MB.
    </p>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILE UPLOADER
# ============================================================

uploaded = st.file_uploader(
    "Video file",
    type=[
        "mp4",
        "mov",
        "avi",
        "mkv",
        "webm",
        "m4v",
    ],
    label_visibility="collapsed",
)


# ============================================================
# NO FILE
# ============================================================

if not uploaded:

    st.info(
        "Upload a video to begin."
    )

    st.stop()


# ============================================================
# SIZE CHECK
# ============================================================

if uploaded.size > MAX_VIDEO_SIZE_BYTES:

    actual_size_mb = (
        uploaded.size
        / (1024 * 1024)
    )

    st.error(
        f"Video is {actual_size_mb:.1f} MB. "
        f"DeepTrace supports videos up to "
        f"{MAX_VIDEO_SIZE_MB} MB."
    )

    st.stop()


# ============================================================
# VIDEO PREVIEW
# ============================================================

col_preview, col_info = st.columns(
    [2, 1]
)


with col_preview:

    st.video(
        uploaded
    )


with col_info:

    st.markdown(
        """
        <div class="dt-card">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        **File**

        {uploaded.name}

        **Size**

        {uploaded.size / (1024 * 1024):.2f} MB

        **Limit**

        {MAX_VIDEO_SIZE_MB} MB
        """,
    )

    analyze = st.button(
        "Run analysis",
        type="primary",
        use_container_width=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze:

    video_result = None
    temp_path: Path | None = None

    with st.status(
        "Analyzing video...",
        expanded=True,
    ) as status:

        try:

            # ------------------------------------------------
            # SAVE TEMPORARY VIDEO
            # ------------------------------------------------

            st.write(
                "Saving uploaded video..."
            )

            suffix = (
                Path(
                    uploaded.name
                ).suffix.lower()
                or ".mp4"
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

            # ------------------------------------------------
            # PIPELINE
            # ------------------------------------------------

            st.write(
                "Validating video..."
            )

            st.write(
                "Running Hive V3 visual analysis..."
            )

            st.write(
                "Evaluating manipulation evidence..."
            )

            st.write(
                "Calculating DeepTrace assessment..."
            )

            analysis_result = analyze_video(
                temp_path
            )

            video_result = (
                analysis_result.to_dict()
            )

            # ------------------------------------------------
            # RESTORE ORIGINAL UPLOAD INFO
            # ------------------------------------------------

            video_result["file_info"] = {

                **video_result.get(
                    "file_info",
                    {},
                ),

                "filename":
                    uploaded.name,

                "file_type":
                    uploaded.type,

                "size":
                    f"{uploaded.size / (1024 * 1024):.2f} MB",
            }

            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            st.session_state[
                "video_result"
            ] = video_result

            st.session_state[
                "current_result"
            ] = {

                **video_result,

                "modality":
                    "video",
            }

            # ------------------------------------------------
            # HISTORY
            # ------------------------------------------------

            save_analysis(
                video_result,
                "video",
            )

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
                f"Video analysis failed: {error}"
            )

        finally:

            if temp_path is not None:

                try:

                    temp_path.unlink(
                        missing_ok=True
                    )

                except Exception:
                    pass


    # ========================================================
    # REDIRECT TO RESULTS
    # ========================================================

    if video_result is not None:

        st.switch_page(
            "pages/results.py"
        )


# ============================================================
# SHOW RESULT IF AVAILABLE
# ============================================================

if "video_result" in st.session_state:

    vr = st.session_state[
        "video_result"
    ]

    if isinstance(
        vr,
        dict,
    ):

        assessment = vr.get(
            "assessment",
            {},
        )

        if isinstance(
            assessment,
            dict,
        ):

            st.markdown(
                '<h3 class="dt-display" '
                'style="margin-top:1.5rem;">'
                'Latest Assessment'
                '</h3>',
                unsafe_allow_html=True,
            )

            from assets.components import (
                render_assessment_card,
            )

            render_assessment_card(
                assessment
            )