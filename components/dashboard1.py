"""
pages/dashboard1.py
===================
Dashboard 1 — Kitchen Level PNL

Renders:
  - Sidebar filters (categorical + range-based)
  - KPI strip
  - Monthly PNL pivot by store
  - Revenue bar chart
  - Margin trend line (GM%, CM%, EBITDA%)
  - EBITDA split donut
  - Top 15 stores bar
  - Revenue cohort dual-axis chart
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.helpers import fmt_inr

PLOTLY_THEME = "plotly_dark"


# ── Sidebar filters ───────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame, month_order: list) -> dict:
    """
    Draw all Dashboard 1 filters in the sidebar.
    Returns a dict of the selected values so the main render function
    can apply them without knowing about sidebar internals.
    """
    with st.sidebar:
        # st.markdown("### ")
        # st.markdown("---")

        sel_months = st.multiselect(
            "Month", options=month_order, default=month_order,
        )
        sel_stores = st.multiselect(
            "Store",
            options=sorted(df["STORE"].unique()),
            default=sorted(df["STORE"].unique()),
        )
        sel_rev_cohort = st.multiselect(
            "Revenue Cohort",
            options=sorted(df["REVENUE COHORT"].unique()),
            default=sorted(df["REVENUE COHORT"].unique()),
        )
        sel_cm_cohort = st.multiselect(
            "CM Cohort",
            options=sorted(df["CM COHORT"].unique()),
            default=sorted(df["CM COHORT"].unique()),
        )
        sel_ebitda_cat = st.multiselect(
            "EBITDA Category",
            options=sorted(df["EBITDA CATEGORY"].unique()),
            default=sorted(df["EBITDA CATEGORY"].unique()),
        )
        sel_ebitda_cohort = st.multiselect(
            "EBITDA Cohort",
            options=sorted(df["EBITDA COHORT"].unique()),
            default=sorted(df["EBITDA COHORT"].unique()),
        )

        st.markdown("---")
        st.markdown("#### Range-based Filters")

        sel_ebitda_range = st.slider(
            "EBITDA Range (Rs)",
            min_value=float(df["KITCHEN EBITDA"].min()),
            max_value=float(df["KITCHEN EBITDA"].max()),
            value=(float(df["KITCHEN EBITDA"].min()), float(df["KITCHEN EBITDA"].max())),
            step=10_000.0, format="%.0f",
        )
        sel_cm_range = st.slider(
            "Contribution Margin Range (Rs)",
            min_value=float(df["CM"].min()),
            max_value=float(df["CM"].max()),
            value=(float(df["CM"].min()), float(df["CM"].max())),
            step=10_000.0, format="%.0f",
        )
        sel_rev_range = st.slider(
            "Net Revenue Range (Rs)",
            min_value=float(df["NET REVENUE"].min()),
            max_value=float(df["NET REVENUE"].max()),
            value=(float(df["NET REVENUE"].min()), float(df["NET REVENUE"].max())),
            step=10_000.0, format="%.0f",
        )

    return dict(
        months=sel_months,
        stores=sel_stores,
        rev_cohort=sel_rev_cohort,
        cm_cohort=sel_cm_cohort,
        ebitda_cat=sel_ebitda_cat,
        ebitda_cohort=sel_ebitda_cohort,
        ebitda_range=sel_ebitda_range,
        cm_range=sel_cm_range,
        rev_range=sel_rev_range,
    )


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    mask = (
        df["MONTH_LABEL"].isin(filters["months"])
        & df["STORE"].isin(filters["stores"])
        & df["REVENUE COHORT"].isin(filters["rev_cohort"])
        & df["CM COHORT"].isin(filters["cm_cohort"])
        & df["EBITDA CATEGORY"].isin(filters["ebitda_cat"])
        & df["EBITDA COHORT"].isin(filters["ebitda_cohort"])
        & df["KITCHEN EBITDA"].between(*filters["ebitda_range"])
        & df["CM"].between(*filters["cm_range"])
        & df["NET REVENUE"].between(*filters["rev_range"])
    )
    return df[mask].copy()


# ── Section helpers ───────────────────────────────────────────────────────────
def _kpi(label, value):
    st.markdown(
        f'<div class="kpi-box">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def _sec(title):
    st.markdown(f'<div class="sec-hdr">{title}</div>', unsafe_allow_html=True)


# ── Main render ───────────────────────────────────────────────────────────────
def render(df_filtered: pd.DataFrame, month_order: list) -> None:

    if df_filtered.empty:
        st.warning("No records match the current filter combination.")
        return

    # KPI strip
    _sec("KITCHEN SNAPSHOT")
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: _kpi("Total Net Revenue",  fmt_inr(df_filtered["NET REVENUE"].sum()))
    with k2: _kpi("Avg GM%",            f"{df_filtered['GM%'].mean():.1f}%")
    with k3: _kpi("Avg CM%",            f"{df_filtered['CM%'].mean():.1f}%")
    with k4: _kpi("Avg EBITDA",         fmt_inr(df_filtered["KITCHEN EBITDA"].mean()))
    with k5: _kpi("Unique Stores",      str(df_filtered["STORE"].nunique()))

    st.markdown("---")

    # Monthly PNL pivot by Store
    _sec("Monthly PNL Pivot by Store")
    st.caption("Scroll right to see all months. Values are monthly averages per store.")
    pivot = (
        df_filtered.pivot_table(
            index="STORE",
            columns="MONTH_LABEL",
            values=["NET REVENUE", "GM%", "CM%", "KITCHEN EBITDA", "EBITDA%"],
            aggfunc="mean",
        )
        .round(2)
    )
    pivot.columns = [f"{m} | {mo}" for m, mo in pivot.columns]
    pivot.reset_index(inplace=True)
    pivot.rename(columns={"STORE": "Store"}, inplace=True)
    st.dataframe(pivot, use_container_width=True, height=380, hide_index=True)

    st.markdown("---")

    # Revenue by month | Margin trends
    col_a, col_b = st.columns(2)

    with col_a:
        _sec("Net Revenue by Month")
        rev_by_month = (
            df_filtered.groupby("MONTH_LABEL", sort=False)["NET REVENUE"]
            .sum()
            .reindex(month_order)
            .dropna()
            .reset_index()
        )
        fig = px.bar(
            rev_by_month,
            x="MONTH_LABEL", y="NET REVENUE",
            color_discrete_sequence=["#f4c542"],
            labels={"MONTH_LABEL": "", "NET REVENUE": "Net Revenue (Rs)"},
            template=PLOTLY_THEME, text_auto=".2s",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(margin=dict(t=10, b=10), height=330)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        _sec("Avg GM% / CM% / EBITDA% by Month")
        margin_trend = (
            df_filtered.groupby("MONTH_LABEL", sort=False)[["GM%", "CM%", "EBITDA%"]]
            .mean()
            .reindex(month_order)
            .dropna()
            .reset_index()
        )
        fig2 = go.Figure()
        for metric, color in zip(["GM%", "CM%", "EBITDA%"], ["#f4c542", "#4fc3f7", "#a5d6a7"]):
            fig2.add_trace(go.Scatter(
                x=margin_trend["MONTH_LABEL"], y=margin_trend[metric],
                mode="lines+markers", name=metric,
                line=dict(color=color, width=2), marker=dict(size=7),
            ))
        fig2.update_layout(
            template=PLOTLY_THEME, height=330, margin=dict(t=10, b=10),
            yaxis_title="Margin %",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # EBITDA donut | Top 15 stores
    col_c, col_d = st.columns(2)

    with col_c:
        _sec("EBITDA +ve vs -ve Split")
        split = df_filtered["EBITDA CATEGORY"].value_counts().reset_index()
        split.columns = ["Category", "Count"]
        fig3 = px.pie(
            split, names="Category", values="Count",
            color_discrete_sequence=["#a5d6a7", "#ef9a9a"],
            hole=0.45, template=PLOTLY_THEME,
        )
        fig3.update_layout(
            margin=dict(t=10, b=10), height=310,
            legend=dict(orientation="h", y=-0.1),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        _sec("Top 15 Stores by Total Net Revenue")
        top15 = (
            df_filtered.groupby("STORE")["NET REVENUE"]
            .sum().nlargest(15).reset_index().sort_values("NET REVENUE")
        )
        fig4 = px.bar(
            top15, x="NET REVENUE", y="STORE", orientation="h",
            color_discrete_sequence=["#f4c542"],
            labels={"NET REVENUE": "Net Revenue (Rs)", "STORE": ""},
            template=PLOTLY_THEME, text_auto=".2s",
        )
        fig4.update_layout(margin=dict(t=10, b=10), height=400)
        st.plotly_chart(fig4, use_container_width=True)

    # Revenue cohort dual-axis
    st.markdown("---")
    _sec("Revenue & EBITDA by Revenue Cohort")
    cohort = (
        df_filtered.groupby("REVENUE COHORT")
        .agg(
            Total_Revenue=("NET REVENUE", "sum"),
            Avg_EBITDA=("KITCHEN EBITDA", "mean"),
        )
        .reset_index()
        .rename(columns={"REVENUE COHORT": "Revenue Cohort"})
    )
    fig5 = make_subplots(specs=[[{"secondary_y": True}]])
    fig5.add_trace(
        go.Bar(x=cohort["Revenue Cohort"], y=cohort["Total_Revenue"],
               name="Total Net Revenue", marker_color="#f4c542"),
        secondary_y=False,
    )
    fig5.add_trace(
        go.Scatter(x=cohort["Revenue Cohort"], y=cohort["Avg_EBITDA"],
                   name="Avg EBITDA", mode="lines+markers",
                   line=dict(color="#4fc3f7", width=3), marker=dict(size=10)),
        secondary_y=True,
    )
    fig5.update_yaxes(title_text="Total Net Revenue (Rs)", secondary_y=False)
    fig5.update_yaxes(title_text="Avg EBITDA (Rs)", secondary_y=True)
    fig5.update_layout(
        template=PLOTLY_THEME, height=370, margin=dict(t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig5, use_container_width=True)
