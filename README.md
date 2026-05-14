# Kitchen PNL Dashboard

Streamlit + Plotly dashboard for the Cloud Kitchen Profit & Loss case study.

---

## Project structure

```
kitchen_pnl_project/
│
├── app.py                  ← Entry point  (streamlit run app.py)
├── requirements.txt        ← Python dependencies
├── README.md
│
├── data/
│   └── Kittchen_PNL_Data.xlsx   ← Source data (place here)
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py      ← load_and_prepare(), get_month_order()
│   └── helpers.py          ← fmt_inr(), make_pivot_fmt()
│
├── pages/
│   ├── __init__.py
│   ├── dashboard1.py       ← Kitchen Level PNL (D1)
│   ├── dashboard2.py       ← Variance Analysis  (D2)
│   └── insights.py         ← Bonus insights tab
│
└── assets/
    └── style.py            ← Global CSS injected at startup
```

---

## Setup

```bash
# 1. Clone / unzip the project
cd kitchen_pnl_project

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place the data file
#    Make sure Kittchen_PNL_Data.xlsx is inside the data/ folder.

# 5. Run the app
streamlit run app.py
```

The dashboard opens at http://localhost:8501

---

## What each dashboard does

### Dashboard 1 — Kitchen Level PNL
Sidebar filters: Month, Store, Revenue Cohort, CM Cohort, EBITDA Category,
EBITDA Cohort, plus range sliders for EBITDA / CM / Net Revenue.

Visuals:
- KPI strip (Revenue, GM%, CM%, Avg EBITDA, Store count)
- Monthly PNL pivot by Store (all metrics across months)
- Net Revenue bar chart by month
- Margin trend line (GM%, CM%, EBITDA%)
- EBITDA +ve vs -ve donut chart
- Top 15 stores by revenue
- Revenue cohort dual-axis chart

### Dashboard 2 — Variance Analysis
Top-level filter: Variance category (a/b/c/d).

Sub-Dashboard 2a — Average Variance % by Revenue Category & Month
- Pivot table with Grand Total row + heatmap

Sub-Dashboard 2b — Store Count by Revenue Range & Month
- Store count pivot table + grouped bar chart
- Variance category donut + variance trend by revenue cohort

### Additional Insights 
- City-level GM% vs EBITDA bubble chart
- Revenue trend by Zone
- Active vs Inactive kitchen comparison
- Order Count vs Revenue scatter with OLS trendline
- Full correlation heatmap

---

## Performance notes

- `@st.cache_data(ttl=300)` — data is loaded once and cached for 5 minutes.
  For real-time pipelines that overwrite the xlsx, this means at most a
  5-minute lag before the dashboard reflects new data.
- To force an immediate refresh: open the app menu (top-right) → Clear cache.
- For a database source, replace `load_and_prepare()` in `utils/data_loader.py`
  with a SQL query; the caching decorator stays the same.

---

## Derived columns (computed in data_loader.py)

| Column       | Formula                                        |
|--------------|------------------------------------------------|
| GM%          | Gross Margin / Net Revenue * 100               |
| CM           | Gross Margin - Variance                        |
| CM%          | CM / Net Revenue * 100                         |
| EBITDA%      | Kitchen EBITDA / Net Revenue * 100             |
| VARIANCE%    | Variance / Ideal Food Cost * 100               |
| VAR_CATEGORY | Bucketed from VARIANCE% (<2, 2-3, 3-5, >5%)   |
| REV_BUCKET   | Bucketed Net Revenue (<15L, 15-25L, ..., >45L) |

---

## Python & package versions

| Package    | Version used |
|------------|-------------|
| Python     | 3.10 / 3.11 |
| streamlit  | >= 1.35     |
| pandas     | >= 2.0      |
| numpy      | >= 1.26     |
| plotly     | >= 5.20     |
| openpyxl   | >= 3.1      |
