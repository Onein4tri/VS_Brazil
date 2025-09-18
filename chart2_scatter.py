import pandas as pd
import altair as alt

# Load dataset
df = pd.read_csv("happiness.csv")

# Same 10 countries
countries = [
    "Finland", "Canada", "New Zealand", "Singapore", "India",
    "Qatar", "Brazil", "Guatemala", "South Africa", "Sweden"
]

# Filter
d = df[df["Country or region"].isin(countries)].copy()

# Scatter plot
chart = (
    alt.Chart(d)
    .mark_circle(size=120, opacity=0.8)
    .encode(
        x=alt.X("GDP per capita:Q", title="GDP per capita"),
        y=alt.Y("Score:Q", title="Happiness Score (0–10)"),
        color=alt.Color("Country or region:N", legend=None),
        tooltip=["Country or region", "Score", "GDP per capita"]
    )
    .properties(title="GDP vs Happiness (2019) — Selected Countries", width=600, height=400)
)

chart.save("chart2_scatter.html")
print("Saved: chart2_scatter.html (double-click to open)")
