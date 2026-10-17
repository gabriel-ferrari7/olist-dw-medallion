import pandas as pd

tabelas = [
    "olist_customers_dataset",
    "olist_geolocation_dataset",
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
    "olist_order_reviews_dataset",
    "olist_orders_dataset",
    "olist_products_dataset",
    "olist_sellers_dataset",
    "product_category_name_translation",
]

for tabela in tabelas:
    df = pd.read_csv(f"data/raw/{tabela}.csv", dtype=str)
    df.to_parquet(f"data/bronze/{tabela}.parquet", index=False)
    print(f"{tabela}: {len(df)} linhas")