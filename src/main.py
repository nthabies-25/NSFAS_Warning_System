import pandas as pd

df = pd.read_csv("data/students.csv")

print("n\First 5 Records")
print(df.head())

print("n\Dataset Info")
print(df.info())

print("\nSummary Statistics")
print(df.describe())