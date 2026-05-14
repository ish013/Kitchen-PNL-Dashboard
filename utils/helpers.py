"""
utils/helpers.py
================
Small reusable helpers shared across all dashboard pages.
No Streamlit imports here so these can be tested independently.
"""

import pandas as pd


def fmt_inr(val: float) -> str:
    """
    Return a human-readable Indian Rupee string.

    Examples
    --------
    fmt_inr(15_000_000)  ->  "Rs 1.50 Cr"
    fmt_inr(450_000)     ->  "Rs 4.50 L"
    fmt_inr(9_500)       ->  "Rs 9,500"
    """
    if pd.isna(val):
        return "N/A"
    if abs(val) >= 1e7:
        return f"Rs {val / 1e7:,.2f} Cr"
    if abs(val) >= 1e5:
        return f"Rs {val / 1e5:,.2f} L"
    return f"Rs {val:,.0f}"


def make_pivot_fmt(pivot: pd.DataFrame, suffix: str = "%", decimals: int = 2) -> pd.DataFrame:
    """
    Format every numeric cell in a pivot table with a suffix string.
    NaN cells become 'N/A'.
    """
    return pivot.applymap(
        lambda x: f"{x:.{decimals}f}{suffix}" if pd.notna(x) else "N/A"
    )
