"""History / stats dashboard. Person 2 owns this file (PHASE 17)."""

import streamlit as st

st.markdown('<div class="dt-eyebrow">Dashboard</div>', unsafe_allow_html=True)
st.markdown('<h2 class="dt-display">Overview</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
for col, label, value in zip([col1, col2, col3],
                              ["Total analyses", "High risk flagged", "Avg. trust score"],
                              ["0", "0", "—"]):
    with col:
        st.markdown(f'<div class="dt-card"><div class="dt-eyebrow">{label}</div>'
                    f'<h2 class="dt-display" style="margin:0.3rem 0 0 0;">{value}</h2></div>',
                    unsafe_allow_html=True)

st.markdown('<p style="color:#9FB3C8; margin-top:1rem;">Recent analyses and trend '
            'charts will appear here once results start persisting.</p>',
            unsafe_allow_html=True)
