import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_customers_dataset.parquet")
print(tabela.head())
print(tabela["customer_id"].duplicated().sum())
print(tabela["customer_unique_id"].duplicated().sum())
print(tabela["customer_zip_code_prefix"].str.len().value_counts())