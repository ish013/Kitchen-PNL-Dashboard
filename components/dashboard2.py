"""
pages/dashboard2.py
===================
Dashboard 2 — Variance Level PNL

Sub-Dashboard 2a : Avg Variance % by Revenue Category × Month (pivot + heatmap)
Sub-Dashboard 2b : Store Count by Revenue Range × Month (pivot + grouped bar)
                 + Variance category donut + trend line
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.helpers import fmt_inr, make_pivot_fmt

PLOTLY_THEME = "plotly_dark"

VAR_ALL_CATS = [
    "(a) Var < 2%",
    "(b) Var 2% to 3%",
    "(c) Var 3% to 5%",
    "(d) Var > 5%",
]


def _sec(title):
    st.markdown(f'<div class="sec-hdr">{title}</div>', unsafe_allow_html=True)

def _kpi(label, value):
    st.markdown(
        f'<div class="kpi-box">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render(df: pd.DataFrame, month_order: list) -> None:

    _sec("Variance Level PNL")
    st.caption(
        "Variance = food material wastage.  "
        "Variance % = Variance / Ideal Food Cost x 100"
    )

    # Top-level variance filter
    sel_var_cats = st.multiselect(
        "Variance Category Filter",
        options=VAR_ALL_CATS,
        default=VAR_ALL_CATS,
        key="d2_var",
    )

    d2 = df[df["VAR_CATEGORY"].isin(sel_var_cats)].copy()

    if d2.empty:
        st.warning("No data for the selected variance categories.")
        return

    # Summary KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: _kpi("Records in Filter",  f"{len(d2):,}")
    with k2: _kpi("Unique Stores",       str(d2["STORE"].nunique()))
    with k3: _kpi("Avg Variance %",      f"{d2['VARIANCE%'].mean():.2f}%")
    with k4: _kpi("Avg Net Revenue",     fmt_inr(d2["NET REVENUE"].mean()))

    st.markdown("---")

    avail_months = [m for m in month_order if m in d2["MONTH_LABEL"].values]

    # ── Sub-Dashboard 2a ──────────────────────────────────────────────────────
    _sec("Sub-Dashboard 2a — Avg Variance % by Revenue Category & Month")
    st.caption(
        "Each cell = average variance % for kitchens in that revenue category for that month."
    )

    pivot_2a = (
        d2.pivot_table(
            index="REV_BUCKET",
            columns="MONTH_LABEL",
            values="VARIANCE%",
            aggfunc="mean",
            margins=True,
            margins_name="Grand Total",
        )
        .reindex(columns=avail_months + ["Grand Total"])
        .round(2)
    )
    pivot_2a.index.name = "Revenue Category"

    st.dataframe(make_pivot_fmt(pivot_2a, suffix="%"), use_container_width=True)

    # Heatmap of 2a
    st.markdown("##### Heatmap — Avg Variance %")
    heat = (
        pivot_2a
        .drop(index="Grand Total", errors="ignore")
        .drop(columns="Grand Total", errors="ignore")
    )
    fig_heat = px.imshow(
        heat, text_auto=".2f",
        color_continuous_scale="YlOrRd",
        labels=dict(color="Avg Var%"),
        template=PLOTLY_THEME, aspect="auto",
    )
    fig_heat.update_layout(height=300, margin=dict(t=20, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # ── Sub-Dashboard 2b ──────────────────────────────────────────────────────
    _sec("Sub-Dashboard 2b — Store Count by Revenue Range & Month")
    st.caption(
        "Count of unique kitchen stores in each revenue range per month, "
        "filtered by the variance category selected above."
    )

    pivot_2b = (
        d2.pivot_table(
            index="REV_BUCKET",
            columns="MONTH_LABEL",
            values="STORE",
            aggfunc=pd.Series.nunique,
            margins=True,
            margins_name="Grand Total",
        )
        .reindex(columns=avail_months + ["Grand Total"])
        .fillna(0)
        .astype(int)
    )
    pivot_2b.index.name = "Revenue Category"
    st.dataframe(pivot_2b, use_container_width=True)

    # Grouped bar
    st.markdown("##### Store Count — Grouped Bar by Month")
    sc_long = (
        d2.groupby(["MONTH_LABEL", "REV_BUCKET"], observed=True)["STORE"]
        .nunique()
        .reset_index()
        .rename(columns={
            "STORE": "Store Count",
            "MONTH_LABEL": "Month",
            "REV_BUCKET": "Revenue Bucket",
        })
    )
    sc_long["Month"] = pd.Categorical(sc_long["Month"], categories=month_order, ordered=True)
    sc_long.sort_values("Month", inplace=True)

    fig_sc = px.bar(
        sc_long, x="Month", y="Store Count", color="Revenue Bucket",
        barmode="group", template=PLOTLY_THEME,
        color_discrete_sequence=px.colors.qualitative.Safe,
        text_auto=True,
    )
    fig_sc.update_layout(
        height=400, margin=dict(t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("---")

    # Variance distribution + trend
    col_e, col_f = st.columns([1, 2])

    with col_e:
        _sec("Variance Category Split")
        v_dist = d2["VAR_CATEGORY"].value_counts().reset_index()
        v_dist.columns = ["Variance Category", "Count"]
        fig_vd = px.pie(
            v_dist, names="Variance Category", values="Count",
            hole=0.45, template=PLOTLY_THEME,
            color_discrete_sequence=["#4fc3f7", "#a5d6a7", "#f4c542", "#ef9a9a"],
        )
        fig_vd.update_layout(
            margin=dict(t=10, b=10), height=300,
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig_vd, use_container_width=True)

    with col_f:
        _sec("Avg Variance % Trend by Revenue Cohort")
        vtrend = (
            d2.groupby(["MONTH_LABEL", "REVENUE COHORT"], observed=True)["VARIANCE%"]
            .mean()
            .reset_index()
        )
        vtrend["MONTH_LABEL"] = pd.Categorical(
            vtrend["MONTH_LABEL"], categories=month_order, ordered=True
        )
        vtrend.sort_values("MONTH_LABEL", inplace=True)
        fig_vt = px.line(
            vtrend, x="MONTH_LABEL", y="VARIANCE%", color="REVENUE COHORT",
            markers=True, template=PLOTLY_THEME,
            labels={"MONTH_LABEL": "Month", "VARIANCE%": "Avg Variance %"},
            color_discrete_sequence=["#f4c542", "#4fc3f7", "#a5d6a7"],
        )
        fig_vt.update_layout(
            margin=dict(t=10, b=10), height=300,
            legend=dict(orientation="h", y=1.15),
        )
        st.plotly_chart(fig_vt, use_container_width=True)
