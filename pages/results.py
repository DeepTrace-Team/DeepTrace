"""Results display — Simple View / Forensic View. Person 2 owns this file."""

import streamlit as st
from assets.components import render_assessment_card, render_evidence_list, render_metadata_findings

result = st.session_state.get("last_result")

st.markdown('<div class="dt-eyebrow">Results</div>', unsafe_allow_html=True)

if not result:
    st.markdown(
        '<div class="dt-card">No analysis yet. Upload media on the Image, '
        'Video, or Audio page to see results here.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown('<h2 class="dt-display" style="margin-top:0;">Assessment</h2>', unsafe_allow_html=True)

    view = st.radio("View", ["Simple View", "Forensic View"], horizontal=True, label_visibility="collapsed")

    render_assessment_card(result["assessment"])

    if view == "Forensic View":
        st.markdown('<h3 class="dt-display" style="margin-top:1.5rem;">Evidence</h3>', unsafe_allow_html=True)
        render_evidence_list(result.get("evidence", []))

        st.markdown('<h3 class="dt-display" style="margin-top:1.5rem;">Metadata</h3>', unsafe_allow_html=True)
        render_metadata_findings(result.get("metadata", {}))

        file_info = result.get("file_info", {})
        if file_info:
            st.markdown('<h3 class="dt-display" style="margin-top:1.5rem;">File Info</h3>', unsafe_allow_html=True)
            info_cols = st.columns(len(file_info))
            for col, (key, value) in zip(info_cols, file_info.items()):
                with col:
                    st.markdown(
                        f'<div class="dt-card"><div class="dt-eyebrow">{key.replace("_"," ").title()}</div>'
                        f'<p class="dt-mono" style="margin:0.3rem 0 0 0;">{value}</p></div>',
                        unsafe_allow_html=True,
                    )
    else:
        n_evidence = len(result.get("evidence", []))
        st.markdown(
            f'<p style="color:#9FB3C8;">Backed by {n_evidence} evidence '
            f'{"signal" if n_evidence == 1 else "signals"}. Switch to Forensic View for the full breakdown.</p>',
            unsafe_allow_html=True,
        )
