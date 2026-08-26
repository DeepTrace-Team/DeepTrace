"""Image upload + analysis UI. Person 2 owns this file.
Uses mock_result until Person 1's analyze_image() is ready to wire in (see PHASE 7)."""

import streamlit as st

st.markdown('<div class="dt-eyebrow">Image Analysis</div>', unsafe_allow_html=True)
st.markdown('<h2 class="dt-display">Upload an image</h2>', unsafe_allow_html=True)

uploaded = st.file_uploader("Image file", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")

if uploaded:
    col_preview, col_action = st.columns([2, 1])
    with col_preview:
        st.image(uploaded, use_container_width=True)
    with col_action:
        st.markdown('<div class="dt-card">', unsafe_allow_html=True)
        st.write(f"**File:** {uploaded.name}")
        st.write(f"**Size:** {uploaded.size / 1024:.1f} KB")
        analyze = st.button("Run analysis", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if analyze:
        with st.status("Analyzing...", expanded=True) as status:
            st.write("Validating media")
            st.write("Preprocessing image")
            st.write("Running AI analysis")
            st.write("Collecting evidence")
            st.write("Calculating trust score")
            status.update(label="Analysis complete", state="complete")

        # TODO(Person 1 integration): replace with
        # result = analyze_image(uploaded)
        mock_result = {
            "status": "success",
            "file_info": {
                "filename": uploaded.name,
                "file_type": uploaded.type,
                "size": f"{uploaded.size / 1024:.1f} KB",
            },
            "assessment": {
                "classification": "Likely AI Generated",
                "confidence": 91.5,
                "trust_score": 18,
                "risk_level": "HIGH",
            },
            "evidence": [
                {
                    "source": "AI Detector",
                    "score": 0.91,
                    "explanation": "Synthetic generation patterns detected in high-frequency texture regions.",
                },
                {
                    "source": "Metadata Analysis",
                    "score": 0.62,
                    "explanation": "EXIF data is missing entirely, which is atypical for camera-captured images.",
                },
                {
                    "source": "Artifact Analysis",
                    "score": 0.78,
                    "explanation": "Inconsistent texture patterns detected around edge boundaries.",
                },
            ],
            "metadata": {
                "available": False,
                "findings": ["No EXIF data present", "No camera make/model recorded"],
            },
        }
        st.session_state["last_result"] = mock_result
        st.switch_page("pages/results.py")
else:
    st.info("Upload an image to begin.")

