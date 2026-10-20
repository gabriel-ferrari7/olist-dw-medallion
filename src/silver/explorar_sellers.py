import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_sellers_dataset.parquet")
print(tabela.head())
print(tabela["seller_id"].duplicated().sum())
print(tabela["seller_zip_code_prefix"].str.len().value_counts())
print(tabela["seller_state"].value_counts())