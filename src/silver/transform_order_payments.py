import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_order_payments_dataset.parquet")

tabela["payment_sequential"] = tabela["payment_sequential"].astype("int64")
tabela["payment_installments"] = tabela["payment_installments"].astype("int64")
tabela["payment_value"] = tabela["payment_value"].astype("float64")

tabela.to_parquet("data/silver/olist_order_payments_dataset.parquet", index=False)

print(tabela.dtypes)