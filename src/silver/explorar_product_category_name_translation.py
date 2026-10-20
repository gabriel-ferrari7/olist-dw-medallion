import pandas as pd

tabela = pd.read_parquet("data/bronze/product_category_name_translation.parquet")
print(tabela.head())
print(tabela["product_category_name"].duplicated().sum())