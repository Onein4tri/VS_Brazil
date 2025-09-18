import pandas as pd
import altair as alt

# Load 2019 dataset
df = pd.read_csv("happiness.csv")

# Select top 10 happiest countries
top10 = df.nlargest(10, "Score")

# Create a bar chart
chart = (
    alt.Chart(top10)
    .mark_bar()
    .encode(
        y=alt.Y("Country or region:N", sort="-x", title="Country"),
        x=alt.X("Score:Q", title="Happiness Score (0–10)"),
        tooltip=["Country or region", "Score"]
    )
    .properties(title="Top 10 Happiest Countries (2019)", width=600, height=400)
)

# Save chart as HTML file
chart.save("chart1.html")
print("Saved chart1.html – open it in your browser.")
