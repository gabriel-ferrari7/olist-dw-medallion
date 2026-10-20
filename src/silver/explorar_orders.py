import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

tabela = pd.read_parquet("data/bronze/olist_orders_dataset.parquet")
print(tabela.head())
print(tabela.isna().sum())
print(tabela["order_id"].duplicated().sum())
print(tabela["order_status"].value_counts())

entregues_sem_data = (tabela["order_status"] == "delivered") & (tabela["order_delivered_customer_date"].isna())
print(entregues_sem_data.sum())