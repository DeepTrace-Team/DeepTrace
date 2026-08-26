"""
DeepTrace shared visual theme.

Call apply_theme() ONCE, from app.py, before st.navigation runs. Because app.py
always runs first and st.navigation just swaps in the selected page's body,
this persists on every page without any page needing to re-apply it.

Two separate injections are used on purpose:
  1. st.markdown(...)      -> global fonts/typography/.dt-card styles that must
                               apply to the MAIN document (headings, widgets,
                               anything pages render via st.markdown).
  2. components.html(...)  -> the animated space background. This has to be a
                               components.html iframe (not st.markdown) because
                               st.markdown injects HTML via innerHTML, and
                               browsers never execute <script> tags set that
                               way — so the mouse-parallax JS needs a real
                               iframe document to run in. The iframe resizes
                               itself to a fixed fullscreen overlay behind
                               everything via window.frameElement.
"""

import random
import streamlit as st
import streamlit.components.v1 as components

STAR_FIELD_SIZE = 2000  # px, square tile that seamlessly loops vertically


def _generate_star_shadows(count: int, color: str) -> str:
    """Return a CSS box-shadow value plotting `count` random dots of `color`."""
    points = []
    for _ in range(count):
        x = random.randint(0, STAR_FIELD_SIZE)
        y = random.randint(0, STAR_FIELD_SIZE)
        points.append(f"{x}px {y}px {color}")
    return ", ".join(points)


def _get_star_layers() -> tuple[str, str, str]:
    if "_dt_star_layers" not in st.session_state:
        small = _generate_star_shadows(240, "rgba(255,255,255,0.75)")
        medium = _generate_star_shadows(100, "rgba(180,220,255,0.9)")
        large = _generate_star_shadows(40, "rgba(120,235,220,0.95)")
        st.session_state["_dt_star_layers"] = (small, medium, large)
    return st.session_state["_dt_star_layers"]


def apply_theme() -> None:
    """Inject global typography/component styles, then the mouse-reactive starfield."""
    _apply_typography_and_components()
    _apply_starfield()


def _apply_typography_and_components() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: transparent !important;
            font-size: 17px;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stSidebar"] {
            background: rgba(7, 9, 18, 0.72) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(79, 209, 197, 0.12);
        }

        body, p, li, label, span, div { font-family: 'Inter', sans-serif; }
        p, li { line-height: 1.7 !important; font-size: 1.05rem !important; }

        h1, h2, h3, h4, .dt-display {
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: -0.01em;
        }
        h1 { font-size: 2.6rem !important; font-weight: 700 !important; }
        h2 { font-size: 1.9rem !important; font-weight: 600 !important; }
        h3 { font-size: 1.35rem !important; font-weight: 600 !important; }

        code, .dt-mono { font-family: 'JetBrains Mono', monospace !important; }

        .dt-eyebrow {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #4FD1C5;
        }

        .dt-hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 800;
            font-size: 4rem;
            line-height: 1.05;
            margin: 0.3rem 0 0.6rem 0;
            background: linear-gradient(90deg, #E6EDF3 40%, #4FD1C5 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .dt-hero-tagline {
            font-size: 1.35rem !important;
            color: #9FB3C8;
            max-width: 640px;
            line-height: 1.5 !important;
        }

        .dt-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(79, 209, 197, 0.15);
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            backdrop-filter: blur(6px);
        }
        .dt-risk-high   { color: #F87171; }
        .dt-risk-medium { color: #FBBF24; }
        .dt-risk-low    { color: #34D399; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _apply_starfield() -> None:
    small, medium, large = _get_star_layers()

    html = f"""
    <style>
    html, body {{ margin:0; padding:0; background: transparent; overflow: hidden; }}
    #dt-space-bg {{
        position: absolute;
        inset: -120px;
        overflow: hidden;
        background:
            radial-gradient(ellipse 900px 600px at 15% 8%, rgba(79,209,197,0.10), transparent 55%),
            radial-gradient(ellipse 900px 700px at 85% 85%, rgba(124,92,252,0.10), transparent 55%),
            linear-gradient(180deg, #05060a 0%, #070912 55%, #05060a 100%);
    }}
    .dt-parallax-layer {{
        position: absolute;
        inset: -160px;
        transition: transform 0.25s ease-out;
        will-change: transform;
    }}
    .dt-star-layer {{
        position: absolute;
        top: 0; left: 0;
        width: 1px; height: 1px;
        background: transparent;
    }}
    #dt-stars-small  {{ box-shadow: {small};  animation: dtDrift 160s linear infinite; }}
    #dt-stars-small::after  {{ content:""; position:absolute; top:{STAR_FIELD_SIZE}px; left:0;
        width:1px; height:1px; box-shadow: {small}; }}
    #dt-stars-medium {{ box-shadow: {medium}; animation: dtDrift 100s linear infinite; }}
    #dt-stars-medium::after {{ content:""; position:absolute; top:{STAR_FIELD_SIZE}px; left:0;
        width:1px; height:1px; box-shadow: {medium}; }}
    #dt-stars-large  {{ box-shadow: {large};  animation: dtDrift 60s linear infinite, dtTwinkle 4.5s ease-in-out infinite; }}
    #dt-stars-large::after  {{ content:""; position:absolute; top:{STAR_FIELD_SIZE}px; left:0;
        width:1px; height:1px; box-shadow: {large}; }}

    @keyframes dtDrift {{
        from {{ transform: translateY(0); }}
        to   {{ transform: translateY(-{STAR_FIELD_SIZE}px); }}
    }}
    @keyframes dtTwinkle {{
        0%, 100% {{ opacity: 1; }}
        50%      {{ opacity: 0.45; }}
    }}
    </style>

    <div id="dt-space-bg">
        <div class="dt-parallax-layer" id="dt-parallax-small">
            <div class="dt-star-layer" id="dt-stars-small"></div>
        </div>
        <div class="dt-parallax-layer" id="dt-parallax-medium">
            <div class="dt-star-layer" id="dt-stars-medium"></div>
        </div>
        <div class="dt-parallax-layer" id="dt-parallax-large">
            <div class="dt-star-layer" id="dt-stars-large"></div>
        </div>
    </div>

    <script>
    (function() {{
        // Same-origin srcdoc iframe: resize ourselves into a fixed fullscreen
        // overlay sitting behind everything, then listen for mouse movement
        // on the TOP document (not just this iframe) so stars react no
        // matter where the cursor is over the app.
        try {{
            var frame = window.frameElement;
            frame.style.cssText =
                "position:fixed; inset:0; width:100vw; height:100vh; " +
                "border:none; z-index:-2; pointer-events:none;";
        }} catch (e) {{}}

        var small = document.getElementById('dt-parallax-small');
        var medium = document.getElementById('dt-parallax-medium');
        var large = document.getElementById('dt-parallax-large');

        function onMove(e) {{
            var w = window.top.innerWidth || window.innerWidth;
            var h = window.top.innerHeight || window.innerHeight;
            var dx = (e.clientX / w - 0.5); // -0.5 .. 0.5
            var dy = (e.clientY / h - 0.5);

            small.style.transform  = "translate(" + (dx * -10) + "px," + (dy * -10) + "px)";
            medium.style.transform = "translate(" + (dx * -22) + "px," + (dy * -22) + "px)";
            large.style.transform  = "translate(" + (dx * -38) + "px," + (dy * -38) + "px)";
        }}

        try {{
            window.top.document.addEventListener('mousemove', onMove);
        }} catch (e) {{
            document.addEventListener('mousemove', onMove);
        }}
    }})();
    </script>
    """

    components.html(html, height=0)


def scan_beam(height_px: int = 220) -> None:
    """
    Optional signature element: a slow horizontal 'trace' beam.
    Use sparingly (e.g. once, on the home hero) — not on every page.
    """
    st.markdown(
        f"""
        <style>
        .dt-scan-wrap {{
            position: relative;
            height: {height_px}px;
            overflow: hidden;
            border-radius: 14px;
            margin-bottom: 1rem;
        }}
        .dt-scan-beam {{
            position: absolute;
            left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #4FD1C5, transparent);
            box-shadow: 0 0 12px 2px rgba(79,209,197,0.6);
            animation: dtScan 3.2s ease-in-out infinite;
        }}
        @keyframes dtScan {{
            0%   {{ top: 0%; opacity: 0; }}
            10%  {{ opacity: 1; }}
            90%  {{ opacity: 1; }}
            100% {{ top: 100%; opacity: 0; }}
        }}
        </style>
        <div class="dt-scan-wrap"><div class="dt-scan-beam"></div></div>
        """,
        unsafe_allow_html=True,
    )
