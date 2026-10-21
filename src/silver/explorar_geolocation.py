import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_geolocation_dataset.parquet")
print(tabela.head())
print(tabela.isna().sum())
print(tabela.duplicated().sum())
print(tabela["geolocation_zip_code_prefix"].nunique())
print(tabela[["geolocation_lat", "geolocation_lng"]].astype("float64").describe())