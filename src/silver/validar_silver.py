import pandas as pd

customers = pd.read_parquet("data/silver/olist_customers_dataset.parquet")
sellers = pd.read_parquet("data/silver/olist_sellers_dataset.parquet")
products = pd.read_parquet("data/silver/olist_products_dataset.parquet")
orders = pd.read_parquet("data/silver/olist_orders_dataset.parquet")
order_items = pd.read_parquet("data/silver/olist_order_items_dataset.parquet")
order_payments = pd.read_parquet("data/silver/olist_order_payments_dataset.parquet")
order_reviews = pd.read_parquet("data/silver/olist_order_reviews_dataset.parquet")
geolocation = pd.read_parquet("data/silver/olist_geolocation_dataset.parquet")

assert customers["customer_id"].is_unique
assert sellers["seller_id"].is_unique
assert products["product_id"].is_unique
assert orders["order_id"].is_unique
assert geolocation["geolocation_zip_code_prefix"].is_unique
assert not order_items.duplicated(subset=["order_id", "order_item_id"]).any()
assert not order_payments.duplicated(subset=["order_id", "payment_sequential"]).any()

assert orders["customer_id"].isin(customers["customer_id"]).all()
assert order_items["order_id"].isin(orders["order_id"]).all()
assert order_items["product_id"].isin(products["product_id"]).all()
assert order_items["seller_id"].isin(sellers["seller_id"]).all()
assert order_payments["order_id"].isin(orders["order_id"]).all()
assert order_reviews["order_id"].isin(orders["order_id"]).all()

print("silver validada")