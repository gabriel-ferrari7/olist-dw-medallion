import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_sellers_dataset.parquet")

tabela["seller_zip_code_prefix"] = tabela["seller_zip_code_prefix"].str.zfill(5)

tabela.to_parquet("data/silver/olist_sellers_dataset.parquet", index=False)

print(tabela.head())