"""Video upload + timeline UI. Person 2 owns this file. Mock data until Person 1's
video_pipeline.py lands (see PHASE 11/12)."""

import streamlit as st
from assets.components import render_assessment_card, render_evidence_list, render_timeline

st.markdown('<div class="dt-eyebrow">Video Analysis</div>', unsafe_allow_html=True)
st.markdown('<h2 class="dt-display">Upload a video</h2>', unsafe_allow_html=True)

uploaded = st.file_uploader("Video file", type=["mp4", "mov", "webm"], label_visibility="collapsed")

if uploaded:
    col_preview, col_action = st.columns([2, 1])
    with col_preview:
        st.video(uploaded)
    with col_action:
        st.markdown('<div class="dt-card">', unsafe_allow_html=True)
        st.write(f"**File:** {uploaded.name}")
        st.write(f"**Size:** {uploaded.size / 1024 / 1024:.1f} MB")
        analyze = st.button("Run analysis", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if analyze:
        with st.status("Analyzing...", expanded=True) as status:
            st.write("Extracting frames")
            st.write("Analyzing sampled frames")
            st.write("Calculating frame scores")
            st.write("Building suspicion timeline")
            st.write("Compiling video-level assessment")
            status.update(label="Analysis complete", state="complete")

        # TODO(Person 1 integration): replace with result = analyze_video(uploaded)
        st.session_state["video_result"] = {
            "assessment": {
                "classification": "Manipulated Segments Detected",
                "confidence": 84.0,
                "trust_score": 27,
                "risk_level": "HIGH",
            },
            "frame_scores": [12, 14, 18, 15, 20, 22, 61, 74, 88, 79, 55, 24, 20, 18,
                              19, 60, 82, 91, 85, 58, 21, 17, 15, 14, 16, 13, 12, 11],
            "suspicious_segments": [
                {"start_pct": 22, "end_pct": 36, "severity": "HIGH"},
                {"start_pct": 55, "end_pct": 68, "severity": "MEDIUM"},
            ],
            "evidence": [
                {
                    "source": "Frame-Level Detector",
                    "score": 0.88,
                    "explanation": "Sustained synthetic-generation signal across frames 0:07–0:11.",
                },
                {
                    "source": "Temporal Consistency",
                    "score": 0.66,
                    "explanation": "Flickering artifacts around facial region between segments.",
                },
            ],
        }

if "video_result" in st.session_state:
    vr = st.session_state["video_result"]

    st.markdown('<h3 class="dt-display" style="margin-top:1.5rem;">Suspicion Timeline</h3>',
                unsafe_allow_html=True)
    render_timeline(vr["suspicious_segments"], duration_label="00:00 – 00:45")
    st.line_chart(vr["frame_scores"], height=160)
    st.markdown(
        '<p style="color:#9FB3C8; font-size:0.85rem; margin-top:-0.5rem;">'
        'Per-frame suspicion score (sampled) — spikes indicate likely manipulation.</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<h3 class="dt-display" style="margin-top:1.5rem;">Assessment</h3>', unsafe_allow_html=True)
    render_assessment_card(vr["assessment"])

    with st.expander("Evidence details"):
        render_evidence_list(vr["evidence"])

elif not uploaded:
    st.info("Upload a video to begin.")
