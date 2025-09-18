import pandas as pd
import altair as alt

# Load your 2019 file
df = pd.read_csv("happiness.csv")

# Exact countries to include (case and spelling must match your CSV)
countries = [
    "Finland", "Canada", "New Zealand", "Singapore", "India",
    "Qatar", "Brazil", "Guatemala", "South Africa", "Sweden"
]

# Filter to just those countries
d = df[df["Country or region"].isin(countries)].copy()

# Optional: sort by score descending so the bars look nice
d = d.sort_values("Score", ascending=False)

# Bar chart
chart = (
    alt.Chart(d)
    .mark_bar()
    .encode(
        y=alt.Y("Country or region:N", sort="-x", title="Country"),
        x=alt.X("Score:Q", title="Happiness Score (0–10)"),
        tooltip=["Country or region", "Score", "GDP per capita"]
    )
    .properties(title="Selected Countries — Happiness Score (2019)", width=650, height=28*len(d))
)

chart.save("chart1_selected.html")
print("Saved: chart1_selected.html (double-click to open)")
