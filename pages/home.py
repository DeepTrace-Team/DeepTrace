import streamlit as st
from assets.theme import scan_beam

st.markdown('<div class="dt-eyebrow">Digital Media Forensics</div>', unsafe_allow_html=True)
st.markdown('<h1 class="dt-hero-title">DEEPTRACE</h1>', unsafe_allow_html=True)
st.markdown(
    "<p class='dt-hero-tagline'>Don't just detect the fake. Trace the evidence.</p>",
    unsafe_allow_html=True,
)

scan_beam(height_px=140)

st.markdown(
    "<p style='max-width:680px; color:#C4D0DC;'>"
    "DeepTrace analyzes images, video, and audio for signs of AI generation or "
    "manipulation, and shows its work: every classification is backed by evidence "
    "— detector scores, metadata findings, and artifact analysis — combined into "
    "a single, explainable trust score."
    "</p>",
    unsafe_allow_html=True,
)

st.write("")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '<div class="dt-card"><div class="dt-eyebrow">Image</div>'
        '<p style="margin:0.4rem 0 1rem 0;">Check a photo for AI generation, '
        'face swaps, or edits.</p></div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/image_analysis.py", label="Analyze an image →")

with col2:
    st.markdown(
        '<div class="dt-card"><div class="dt-eyebrow">Video</div>'
        '<p style="margin:0.4rem 0 1rem 0;">Scan frame-by-frame for '
        'suspicious segments and manipulation.</p></div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/video_analysis.py", label="Analyze a video →")

with col3:
    st.markdown(
        '<div class="dt-card"><div class="dt-eyebrow">Audio</div>'
        '<p style="margin:0.4rem 0 1rem 0;">Detect voice cloning and '
        'synthetic speech.</p></div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/audio_analysis.py", label="Analyze audio →")
