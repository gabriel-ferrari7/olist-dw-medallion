import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_orders_dataset.parquet")

colunas_data = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for coluna in colunas_data:
    tabela[coluna] = pd.to_datetime(tabela[coluna], format="%Y-%m-%d %H:%M:%S")

tabela.to_parquet("data/silver/olist_orders_dataset.parquet", index=False)

print(tabela.dtypes)