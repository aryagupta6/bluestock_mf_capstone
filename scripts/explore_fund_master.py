import pandas as pd

df = pd.read_csv("data/raw/01_fund_master.csv")

print("\nColumns:")
print(df.columns.tolist())

print("\nShape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nUnique Fund Houses:")
print(df["fund_house"].nunique())

print("\nUnique Categories:")
print(df["category"].nunique())

print("\nUnique Sub Categories:")
print(df["sub_category"].nunique())

print("\nUnique Risk Categories:")
print(df["risk_category"].nunique())

print("\nRisk Categories:")
print(df["risk_category"].unique())