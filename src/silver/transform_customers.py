import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_customers_dataset.parquet")

tabela["customer_zip_code_prefix"] = tabela["customer_zip_code_prefix"].str.zfill(5)

tabela.to_parquet("data/silver/olist_customers_dataset.parquet", index=False)

print(tabela.head())