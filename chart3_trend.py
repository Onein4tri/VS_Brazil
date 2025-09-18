import pandas as pd
import altair as alt
from pathlib import Path

# Point to your CSVs (adjust if your filenames differ)
files = {
    2015: "2015.csv",
    2017: "2017.csv",
    2019: "2019.csv",
}

# Possible column names per dataset (Kaggle years differ)
COUNTRY_CANDIDATES = [
    "Country or region", "Country", "Country name", "Country Name"
]
SCORE_CANDIDATES = [
    "Score", "Happiness Score", "Happiness.Score", "Life Ladder"
]

frames = []

def pick_col(df, candidates, kind):
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"No expected {kind} column found. Columns: {list(df.columns)}")

for year, fname in files.items():
    path = Path(fname)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {fname} (put it in the same folder)")

    df = pd.read_csv(path)

    country_col = pick_col(df, COUNTRY_CANDIDATES, "country")
    score_col   = pick_col(df, SCORE_CANDIDATES, "score")

    d = df[[country_col, score_col]].copy()
    d.columns = ["Country", "Score"]
    d["Year"] = year
    frames.append(d)

data = pd.concat(frames, ignore_index=True)

# Pick just 3 countries for a clean trend
countries = ["Brazil", "Finland", "India"]
d3 = data[data["Country"].isin(countries)].copy()

# Sort years for neat lines
d3 = d3.sort_values(["Country", "Year"])

# Line chart
chart = (
    alt.Chart(d3)
    .mark_line(point=True)
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Score:Q", title="Happiness Score (0–10)"),
        color="Country:N",
        tooltip=["Country", "Year", "Score"],
    )
    .properties(title="Happiness Trends Over Time (2015–2019)", width=640, height=420)
)

chart.save("chart3_trend.html")
print("Saved: chart3_trend.html — double-click to open.")
