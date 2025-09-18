import pandas as pd

# Load the 2019 happiness dataset
df = pd.read_csv("happiness.csv")

# Show the first 5 rows
print(df.head())

# Show the column names
print(df.columns)
