"""
app.py
======
Kitchen PNL Dashboard — entry point.

This file is intentionally thin.  It only:
  1. Configures the Streamlit page.
  2. Injects global CSS.
  3. Loads / caches data.
  4. Delegates rendering to the three page modules.

Python  : 3.10+
Packages: see requirements.txt

Run:
    streamlit run app.py
"""

# ── Cell 1 : imports ──────────────────────────────────────────────────────────
import sys, os
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# import streamlit as st
import streamlit as st

from assets.style import inject_css
from utils.data_loader import get_month_order, load_and_prepare
from components import dashboard1, dashboard2, insights

# ── Cell 2 : page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kitchen PNL Dashboard",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cell 3 : global styles ────────────────────────────────────────────────────
inject_css()

# ── Cell 4 : load data ────────────────────────────────────────────────────────
#   @st.cache_data with ttl=300 means the xlsx is re-read from disk at most
#   once every 5 minutes.  This is enough for near-real-time use cases where
#   a cron job / pipeline overwrites the file periodically.
#   For a live database source, swap load_and_prepare() with a SQL query
#   wrapped in the same decorator.
DATA_PATH = "D:\Kitechen_Pnl\data\Kittchen PNL Data.xlsx"


@st.cache_data(ttl=300, show_spinner="Loading data ...")
def get_data(path: str):
    return load_and_prepare(path)


try:
    df = get_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"**{DATA_PATH}** not found.  "
        "Place the Excel file in the `data/` folder and refresh."
    )
    st.stop()

MONTH_ORDER = get_month_order(df)

# ── Cell 5 : app header ───────────────────────────────────────────────────────
st.markdown("## Kitchen PNL Dashboard")
st.caption("Cloud Kitchen – Profit & Loss Analysis  |  Data: Oct 2023 – Mar 2024")

# ── Cell 6 : tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "Dashboard 1 — Kitchen Level PNL",
    "Dashboard 2 — Variance Analysis",
    "Additional Insights",
])

with tab1:
    filters = dashboard1.render_sidebar(df, MONTH_ORDER)
    d1_filtered = dashboard1.apply_filters(df, filters)
    dashboard1.render(d1_filtered, MONTH_ORDER)

with tab2:
    dashboard2.render(df, MONTH_ORDER)

with tab3:
    insights.render(df, MONTH_ORDER)

# ── Cell 7 : footer ───────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Built with Streamlit + Plotly  |  "
    "Cache TTL = 5 min  |  "
    "Python 3.10+  |  pandas 2.x  |  plotly 5.x  |  openpyxl 3.x"
)
