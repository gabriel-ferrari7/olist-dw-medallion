import pandas as pd

tabela = pd.read_parquet("data/bronze/product_category_name_translation.parquet")

tabela.to_parquet("data/silver/product_category_name_translation.parquet", index=False)

print(tabela.head())