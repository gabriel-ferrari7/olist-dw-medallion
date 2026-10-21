import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

tabela = pd.read_parquet("data/bronze/olist_order_items_dataset.parquet")
print(tabela.head())
print(tabela.isna().sum())
print(tabela.duplicated(subset=["order_id", "order_item_id"]).sum())
print(tabela[["price", "freight_value"]].astype("float64").describe())
print((tabela["freight_value"].astype("float64") == 0).sum())