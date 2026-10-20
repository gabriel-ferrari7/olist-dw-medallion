import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_order_payments_dataset.parquet")
print(tabela.head())
print(tabela.isna().sum())
print(tabela.duplicated(subset=["order_id", "payment_sequential"]).sum())
print(tabela["payment_type"].value_counts())
print(tabela["payment_value"].astype("float64").describe())
print((tabela["payment_value"].astype("float64") == 0).sum())