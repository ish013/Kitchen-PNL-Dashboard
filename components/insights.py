"""
pages/insights.py
=================
Additional Insights tab (bonus) — patterns found beyond the two core dashboards.

Charts
------
1. City-level GM% vs EBITDA bubble chart
2. Revenue trend by Zone over months
3. Active vs Inactive kitchen comparison table
4. Order Count vs Net Revenue scatter with OLS trendline
5. Correlation matrix heatmap
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

PLOTLY_THEME = "plotly_dark"


def _sec(title):
    st.markdown(f'<div class="sec-hdr">{title}</div>', unsafe_allow_html=True)


def render(df: pd.DataFrame, month_order: list) -> None:

    _sec("Additional Insights from the Data")

    # 1. City bubble chart
    st.markdown("#### City-level Performance (bubble size = total revenue)")
    city_df = (
        df.groupby("CITY")
        .agg(
            Total_Revenue=("NET REVENUE", "sum"),
            Avg_EBITDA=("KITCHEN EBITDA", "mean"),
            Avg_GM=("GM%", "mean"),
            Avg_CM=("CM%", "mean"),
            Stores=("STORE", "nunique"),
        )
        .reset_index()
        .rename(columns={"CITY": "City"})
    )
    fig_city = px.scatter(
        city_df, x="Avg_GM", y="Avg_EBITDA",
        size="Total_Revenue", color="City",
        hover_data=["Stores", "Avg_CM"],
        template=PLOTLY_THEME, size_max=60,
        labels={"Avg_GM": "Avg GM%", "Avg_EBITDA": "Avg EBITDA (Rs)"},
    )
    fig_city.update_layout(margin=dict(t=10, b=10), height=380)
    st.plotly_chart(fig_city, use_container_width=True)

    # 2. Zone revenue trend
    st.markdown("---")
    st.markdown("#### Revenue Trend by Zone")
    zone_trend = (
        df.groupby(["ZONE MAPPING", "MONTH_LABEL"], sort=False)["NET REVENUE"]
        .sum()
        .reset_index()
    )
    zone_trend["MONTH_LABEL"] = pd.Categorical(
        zone_trend["MONTH_LABEL"], categories=month_order, ordered=True
    )
    zone_trend.sort_values("MONTH_LABEL", inplace=True)
    fig_zone = px.line(
        zone_trend, x="MONTH_LABEL", y="NET REVENUE",
        color="ZONE MAPPING", markers=True,
        template=PLOTLY_THEME,
        labels={"MONTH_LABEL": "Month", "NET REVENUE": "Net Revenue (Rs)"},
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_zone.update_layout(
        margin=dict(t=10, b=10), height=360,
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig_zone, use_container_width=True)

    # 3. Active vs Inactive | Order count scatter
    st.markdown("---")
    col_g, col_h = st.columns(2)

    with col_g:
        st.markdown("#### Active vs Inactive — Avg P&L Metrics")
        status_df = (
            df.groupby("STATUS")
            .agg(
                Avg_Revenue=("NET REVENUE", "mean"),
                Avg_EBITDA=("KITCHEN EBITDA", "mean"),
                Avg_GM_pct=("GM%", "mean"),
                Avg_CM_pct=("CM%", "mean"),
            )
            .reset_index()
            .round(2)
        )
        st.dataframe(status_df, use_container_width=True, hide_index=True)

    with col_h:
        st.markdown("#### Order Count vs Net Revenue")
        fig_oc = px.scatter(
            df, x="ORDER COUNT", y="NET REVENUE",
            color="EBITDA CATEGORY", opacity=0.45,
            template=PLOTLY_THEME,
            color_discrete_map={"EBITDA +ve": "#a5d6a7", "EBITDA -ve": "#ef9a9a"},
            labels={"ORDER COUNT": "Order Count", "NET REVENUE": "Net Revenue (Rs)"},
            hover_data=["STORE", "MONTH_LABEL"],
        )
        # manual trendline using numpy - no statsmodels needed
        x = df["ORDER COUNT"].values
        y = df["NET REVENUE"].values
        m, b = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = m * x_line + b
        fig_oc.add_scatter(
            x=x_line, y=y_line,
            mode="lines", name="Trend",
            line=dict(color="white", width=1.5, dash="dash"),
        )
        fig_oc.update_layout(margin=dict(t=10, b=10), height=320)
        st.plotly_chart(fig_oc, use_container_width=True)

    # 4. Correlation heatmap
    st.markdown("---")
    st.markdown("#### Correlation Matrix — Key Numeric Metrics")
    st.caption("Shows which metrics move together — useful for root-cause analysis.")

    num_cols = [
        "ORDER COUNT", "CART SALES", "NET REVENUE",
        "GROSS MARGIN", "KITCHEN EBITDA", "VARIANCE",
        "GM%", "CM%", "EBITDA%", "VARIANCE%",
    ]
    corr = df[num_cols].corr().round(2)
    fig_corr = px.imshow(
        corr, text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        template=PLOTLY_THEME, aspect="auto",
    )
    fig_corr.update_layout(margin=dict(t=10, b=10), height=490)
    st.plotly_chart(fig_corr, use_container_width=True)
