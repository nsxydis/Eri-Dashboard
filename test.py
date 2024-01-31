import polars as pl
import os

file = f"{os.getcwd()}\\data\\modified codebook for dashboard.xlsx"
df = pl.read_excel(file)
print(df)