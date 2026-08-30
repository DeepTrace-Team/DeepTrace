"""
Image upload + analysis UI.
 
Runs the real DeepTrace image analysis pipeline
(pipelines.image_pipeline.analyze_image).
"""
 
import tempfile
from pathlib import Path
 
import streamlit as st
 
from pipelines.image_pipeline import analyze_image
from utils.history_manager import save_analysis
 
 
# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------
 
st.markdown(
    '<div class="dt-eyebrow">Image Analysis</div>',
    unsafe_allow_html=True,
)
 
st.markdown(
    '<h2 class="dt-display">Upload an image</h2>',
    unsafe_allow_html=True,
)
 
 
# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
 
uploaded = st.file_uploader(
    "Image file",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed",
)
 
 
# --------------------------------------------------
# IMAGE PREVIEW + ANALYSIS
# --------------------------------------------------
 
if uploaded:
 
    col_preview, col_action = st.columns([2, 1])
 
    with col_preview:
 
        st.image(
            uploaded,
            use_container_width=True,
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
            f"**Size:** {uploaded.size / 1024:.1f} KB"
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
 
        image_result = None
        temp_path: Path | None = None
 
        with st.status(
            "Analyzing...",
            expanded=True,
        ) as status:
 
            try:
 
                st.write("Saving upload")
 
                suffix = Path(uploaded.name).suffix.lower() or ".jpg"
 
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:
 
                    temp_file.write(uploaded.getvalue())
                    temp_path = Path(temp_file.name)
 
                st.write("Preprocessing image")
                st.write("Analyzing metadata")
                st.write("Running Reality Defender detection")
                st.write("Collecting evidence")
                st.write("Calculating trust score")
 
                # ------------------------------------------------
                # REAL PIPELINE CALL
                # ------------------------------------------------
 
                analysis_result = analyze_image(temp_path)
 
                image_result = analysis_result.to_dict()
 
                # Overlay the true upload info (the pipeline only
                # sees a temp file, not the original filename).
                image_result["file_info"] = {
                    **image_result.get("file_info", {}),
                    "filename": uploaded.name,
                    "file_type": uploaded.type,
                    "size": f"{uploaded.size / 1024:.1f} KB",
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
                    f"Image analysis failed: {error}"
                )
 
            finally:
 
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)
 
 
        if image_result is not None:
 
            # --------------------------------------------------
            # SAVE IMAGE-SPECIFIC RESULT
            # --------------------------------------------------
 
            st.session_state[
                "last_result"
            ] = image_result
 
 
            # --------------------------------------------------
            # SAVE UNIVERSAL RESULT
            # --------------------------------------------------
 
            st.session_state[
                "current_result"
            ] = {
 
                **image_result,
 
                "modality":
                    "image",
 
            }
 
 
            # --------------------------------------------------
            # SAVE TO PERSISTENT HISTORY
            # --------------------------------------------------
 
            save_analysis(
                image_result,
                "image",
            )
 
 
            # --------------------------------------------------
            # GO TO RESULTS PAGE
            # --------------------------------------------------
 
            st.switch_page(
                "pages/results.py"
            )
 
 
else:
 
    st.info(
        "Upload an image to begin."
    )