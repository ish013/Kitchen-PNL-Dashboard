"""
utils/data_loader.py
====================
All data loading and feature-engineering logic lives here.
The Streamlit app imports load_and_prepare() and nothing else.

Keeping this separate means:
  - Easy to unit-test without running Streamlit.
  - If the data source changes (e.g. from xlsx to a database),
    only this file needs updating.
"""

import numpy as np
import pandas as pd


# ── Public constants ──────────────────────────────────────────────────────────
# Variance bucket definitions (per assignment)
VAR_BINS   = [-np.inf, 2, 3, 5, np.inf]
VAR_LABELS = [
    "(a) Var < 2%",
    "(b) Var 2% to 3%",
    "(c) Var 3% to 5%",
    "(d) Var > 5%",
]

# Revenue bucket definitions for Variance dashboard (per assignment screenshot)
REV_BINS   = [-np.inf, 1_500_000, 2_500_000, 3_500_000, 4_500_000, np.inf]
REV_LABELS = [
    "(a) Below INR 15 lacs",
    "(b) INR 15 to 25 lacs",
    "(c) INR 25 to 35 lacs",
    "(d) INR 35 to 45 lacs",
    "(e) Above INR 45 lacs",
]


def load_and_prepare(path: str) -> pd.DataFrame:
    """
    Read the Kitchen PNL Excel file and return a fully enriched DataFrame.

    Derived columns added
    ---------------------
    MONTH_DT     : datetime — used for sorting
    MONTH_LABEL  : str      — "Oct 2023" display label
    GM%          : float    — Gross Margin %
    CM           : float    — Contribution Margin (Gross Margin - Variance)
    CM%          : float    — Contribution Margin %
    EBITDA%      : float    — Kitchen EBITDA %
    VARIANCE%    : float    — Variance as % of Ideal Food Cost
    VAR_CATEGORY : category — bucketed variance label  (a/b/c/d)
    REV_BUCKET   : category — bucketed revenue label   (a/b/c/d/e)
    """
    df = pd.read_excel(path, engine="openpyxl")

    # ── Month columns ─────────────────────────────────────────────────────────
    df["MONTH_DT"]    = pd.to_datetime(df["MONTH"], format="%b-%Y")
    df["MONTH_LABEL"] = df["MONTH_DT"].dt.strftime("%b %Y")

    # ── P&L derived metrics ───────────────────────────────────────────────────
    df["GM%"]     = (df["GROSS MARGIN"]   / df["NET REVENUE"] * 100).round(2)
    df["CM"]      = df["GROSS MARGIN"] - df["VARIANCE"]
    df["CM%"]     = (df["CM"]             / df["NET REVENUE"] * 100).round(2)
    df["EBITDA%"] = (df["KITCHEN EBITDA"] / df["NET REVENUE"] * 100).round(2)

    # Variance % of Ideal Food Cost — gives 0.4–4.7% range, maps to
    # the <2 / 2–3 / 3–5 / >5% buckets from the assignment.
    df["VARIANCE%"] = (df["VARIANCE"] / df["IDEAL FOOD COST"] * 100).round(4)

    # ── Categorical buckets ───────────────────────────────────────────────────
    df["VAR_CATEGORY"] = pd.cut(df["VARIANCE%"], bins=VAR_BINS, labels=VAR_LABELS)
    df["REV_BUCKET"]   = pd.cut(df["NET REVENUE"], bins=REV_BINS, labels=REV_LABELS)

    return df


def get_month_order(df: pd.DataFrame) -> list[str]:
    """Return months sorted chronologically as display labels."""
    return (
        df[["MONTH_DT", "MONTH_LABEL"]]
        .drop_duplicates()
        .sort_values("MONTH_DT")["MONTH_LABEL"]
        .tolist()
    )
