import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_order_items_dataset.parquet")

tabela["order_item_id"] = tabela["order_item_id"].astype("int64")
tabela["shipping_limit_date"] = pd.to_datetime(tabela["shipping_limit_date"], format="%Y-%m-%d %H:%M:%S")
tabela["price"] = tabela["price"].astype("float64")
tabela["freight_value"] = tabela["freight_value"].astype("float64")

tabela.to_parquet("data/silver/olist_order_items_dataset.parquet", index=False)

print(tabela.dtypes)