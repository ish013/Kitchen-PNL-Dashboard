"""
assets/style.py
===============
All custom CSS for the dashboard.
Injected once at startup via inject_css() in app.py.
Keeping styles here avoids cluttering the main app file.
"""

import streamlit as st
CSS = """
<style>
    .kpi-box {
        background: #ffffff;
        border-left: 4px solid #f4c542;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .kpi-label { font-size: 12px; color: #666; margin-bottom: 4px; }
    .kpi-value { font-size: 24px; font-weight: 700; color: #1a1a1a; }

    .sec-hdr {
        font-size: 17px;
        font-weight: 700;
        color: #d4a017;
        border-bottom: 2px solid #f4c542;
        padding-bottom: 3px;
        margin-bottom: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #f0f0f0;
        border-radius: 6px 6px 0 0;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #f4c542 !important;
        color: #1a1a1a !important;
        font-weight: 700;
    }
</style>
"""


def inject_css() -> None:
    """Call this once at the top of app.py to apply styles globally."""
    st.markdown(CSS, unsafe_allow_html=True)
