import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_products_dataset.parquet")
traducao = pd.read_parquet("data/bronze/product_category_name_translation.parquet")

print(tabela.head())
print(tabela.isna().sum())
print(tabela["product_id"].duplicated().sum())
print(tabela["product_category_name"].nunique())

sem_traducao = set(tabela["product_category_name"].dropna()) - set(traducao["product_category_name"])
print(sem_traducao)