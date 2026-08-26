"""
DeepTrace — app entry point.

This file is intentionally thin. It is responsible for exactly three things:
  1. Page config
  2. Applying the shared theme (starfield background, fonts, component styles)
  3. Registering pages for navigation

Every page's actual content lives in its own file under pages/. Because
st.navigation always runs app.py first and then swaps in the selected page's
body, calling apply_theme() here is enough for it to persist on every page —
no page needs to import or re-apply it.
"""

import streamlit as st
from assets.theme import apply_theme

st.set_page_config(
    page_title="DeepTrace",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

pages = {
    "DeepTrace": [
        st.Page("pages/home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/image_analysis.py", title="Image", icon="🖼️"),
        st.Page("pages/video_analysis.py", title="Video", icon="🎬"),
        st.Page("pages/audio_analysis.py", title="Audio", icon="🎙️"),
        st.Page("pages/results.py", title="Results", icon="📊"),
        st.Page("pages/dashboard.py", title="Dashboard", icon="📈"),
    ]
}

nav = st.navigation(pages)
nav.run()