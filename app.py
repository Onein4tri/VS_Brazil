# app.py — World Happiness (Kaggle) • Altair + Streamlit
# required: 2019.csv (or happiness.csv)
# optional: 2015.csv, 2017.csv (for Trends)
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from pathlib import Path

st.set_page_config(page_title="World Happiness", layout="wide")
alt.data_transformers.disable_max_rows()

# ---------- helpers ----------
def std_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: c.strip() for c in df.columns})
    ren = {
        "Country or region": "country", "Country": "country", "Country name": "country",
        "Score": "score", "Happiness Score": "score", "Happiness.Score": "score", "Life Ladder": "score",
        "year": "year", "Year": "year",
    }
    for k, v in ren.items():
        if k in df.columns: df = df.rename(columns={k: v})

    gdp_candidates = [
        "GDP per capita", "Economy (GDP per Capita)", "Economy..GDP.per.Capita.",
        "Log GDP per capita", "Explained by: Log GDP per capita",
    ]
    gdp_col = next((c for c in gdp_candidates if c in df.columns), None)
    if gdp_col is not None:
        if gdp_col.lower().startswith("log") or gdp_col == "Explained by: Log GDP per capita":
            df = df.rename(columns={gdp_col: "log_gdp_per_capita"})
        else:
            df = df.rename(columns={gdp_col: "gdp_per_capita"})
    if "gdp_per_capita" not in df.columns and "log_gdp_per_capita" in df.columns:
        df["gdp_per_capita"] = np.exp(pd.to_numeric(df["log_gdp_per_capita"], errors="coerce"))
    for c in ["score","gdp_per_capita","year"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "", regex=False), errors="coerce")
    return df

def load_one(name: str, year_if_missing: int | None = None) -> pd.DataFrame | None:
    p = Path(name)
    if not p.exists(): return None
    df = std_cols(pd.read_csv(p))
    if "country" not in df.columns or "score" not in df.columns: return None
    if "year" not in df.columns and year_if_missing is not None: df["year"] = year_if_missing
    keep = ["country","score"] + (["gdp_per_capita"] if "gdp_per_capita" in df.columns else []) + (["year"] if "year" in df.columns else [])
    return df[keep].copy()

@st.cache_data(show_spinner=False)
def load_data():
    d2019 = load_one("happiness.csv")
    if d2019 is None:
        d2019 = load_one("2019.csv", 2019)
    if d2019 is None:
        raise FileNotFoundError("Put 2019.csv (or happiness.csv) in this folder.")
    if "year" not in d2019.columns:
        d2019 = d2019.assign(year=2019)
    d2015 = load_one("2015.csv", 2015)
    d2017 = load_one("2017.csv", 2017)
    dall = pd.concat([x for x in [d2015, d2017, d2019] if x is not None], ignore_index=True)
    return d2019, dall

# ---------- load ----------
d2019, dall = load_data()

st.title("World Happiness")

# ---------- sidebar ----------
default10 = ["Finland","Canada","New Zealand","Singapore","India","Qatar","Brazil","Guatemala","South Africa","Sweden"]
countries_2019 = sorted(d2019["country"].unique())
picked = st.sidebar.multiselect("Countries (2019 view):", countries_2019, [c for c in default10 if c in countries_2019])
# if user cleared them all, force a safe default so charts never go blank
if not picked:
    picked = [c for c in default10 if c in countries_2019][:10]

mode = st.sidebar.radio("Ranking", ["Top N","Bottom N"], horizontal=True)
N = st.sidebar.slider("N countries", 5, 25, 10)
log_x = st.sidebar.checkbox("Log scale for GDP (scatter)", True)
show_trend = st.sidebar.checkbox("Show trendline (scatter)", True)
trend_choices = st.sidebar.multiselect(
    "Countries for trend (1–3):",
    sorted(dall["country"].dropna().unique()),
    [c for c in ["Brazil","Finland","India"] if c in dall["country"].unique()],
    max_selections=3
)
debug_cols = st.sidebar.checkbox("Show raw 2019 columns (debug)")

if debug_cols:
    src = "happiness.csv" if Path("happiness.csv").exists() else "2019.csv"
    st.sidebar.write(list(pd.read_csv(src).columns))

# ---------- tabs ----------
tab1, tab2, tab3 = st.tabs(["🏆 Rankings (2019)", "💵 GDP vs Happiness (2019)", "📈 Trends (2015–2019)"])

# ---------- tab 1 ----------
with tab1:
    st.subheader("Happiness rankings — selected countries (2019)")
    d = d2019[d2019["country"].isin(picked)].dropna(subset=["score"])
    d = d.sort_values("score", ascending=(mode=="Bottom N")).head(N)
    chart = (
        alt.Chart(d)
        .mark_bar()
        .encode(
            y=alt.Y("country:N", sort="-x", title=None),
            x=alt.X("score:Q", title="Happiness score (0–10)"),
            tooltip=["country", alt.Tooltip("score:Q", title="Score")]
        )
        .properties(height=28*max(len(d),1), width=720)
    )
    st.altair_chart(chart, use_container_width=True)

# ---------- tab 2 ----------
# ---------- tab 2 ----------
with tab2:
    st.subheader("GDP per capita vs. happiness (2019)")

    # 0) make sure we always have some countries to show
    if not picked:
        picked = ["Finland", "Canada", "Singapore", "Brazil"]

    # 1) detect a usable GDP column (prefer standardized, else raw Kaggle names)
    gdp_candidates = [
        "gdp_per_capita",                 # standardized (from std_cols)
        "GDP per capita",                 # your 2019 CSV header
        "Economy (GDP per Capita)",       # 2016/2017 style
        "Economy..GDP.per.Capita.",       # older variant
        "Log GDP per capita",             # log form (we'll exp)
        "Explained by: Log GDP per capita"
    ]
    gdp_col = next((c for c in gdp_candidates if c in d2019.columns), None)

    if gdp_col is None:
        st.info("I can’t find a GDP column in your 2019 file. Turn on the sidebar debug to see raw headers.")
    else:
        # 2) build a working dataframe with unified column names
        d2 = d2019[d2019["country"].isin(picked)].copy()

        # if the column we found is a log column, convert to level
        if gdp_col.lower().startswith("log") or gdp_col == "Explained by: Log GDP per capita":
            d2["gdp_plot"] = np.exp(pd.to_numeric(d2[gdp_col], errors="coerce"))
        else:
            # coerce to numeric (strip commas just in case)
            d2["gdp_plot"] = pd.to_numeric(
                d2[gdp_col].astype(str).str.replace(",", "", regex=False), errors="coerce"
            )

        # keep only rows with both score and GDP
        d2 = d2.dropna(subset=["score", "gdp_plot"])

        if d2.empty:
            st.info(
                "No plottable rows for the selected countries.\n\n"
                "Try countries like Finland, Canada, Singapore, Brazil."
            )
            # quick peek to confirm columns/values
            st.caption("Preview of 2019 after detection:")
            show_cols = ["country", "score", gdp_col]
            st.dataframe(d2019[show_cols].head(12))
        else:
            base = (
                alt.Chart(d2)
                .mark_circle(size=140, opacity=0.8)
                .encode(
                    x=alt.X(
                        "gdp_plot:Q",
                        title=f"{gdp_col} (derived)" if gdp_col != "gdp_per_capita" else "GDP per capita",
                        scale=alt.Scale(type="log") if log_x else alt.Scale(type="linear"),
                        axis=alt.Axis(format="~s"),
                    ),
                    y=alt.Y("score:Q", title="Happiness score (0–10)"),
                    color=alt.Color("country:N", legend=None),
                    tooltip=[
                        "country",
                        alt.Tooltip("score:Q", title="Score"),
                        alt.Tooltip("gdp_plot:Q", title="GDP per capita", format=",.0f"),
                    ],
                )
                .properties(height=480, width=720)
            )

            chart2 = base
            if show_trend and len(d2) >= 2:
                chart2 = base + alt.Chart(d2).transform_regression("gdp_plot", "score").mark_line(color="white")

            st.altair_chart(chart2, use_container_width=True)


# ---------- tab 3 ----------
with tab3:
    st.subheader("Happiness over time")
    if "year" not in dall.columns or dall["year"].nunique() < 2:
        st.info("Add 2015.csv and/or 2017.csv to enable trends.")
    elif not trend_choices:
        st.info("Pick 1–3 countries in the sidebar.")
    else:
        d3 = (dall[dall["country"].isin(trend_choices)]
              .dropna(subset=["score","year"])
              .sort_values(["country","year"]))
        chart3 = (
            alt.Chart(d3)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("score:Q", title="Happiness score (0–10)"),
                color="country:N",
                tooltip=["country","year","score"]
            )
            .properties(height=480, width=720)
        )
        st.altair_chart(chart3, use_container_width=True)

st.caption("Data: World Happiness Report (Kaggle, 2015–2019).")
