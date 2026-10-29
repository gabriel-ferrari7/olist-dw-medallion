import io
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conexao = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cursor = conexao.cursor()

cursor.execute("TRUNCATE dim_produto, dim_cliente, dim_vendedor, dim_data RESTART IDENTITY CASCADE")


sellers = pd.read_parquet("data/silver/olist_sellers_dataset.parquet")

dim_vendedor = sellers[["seller_id"]]

buffer = io.StringIO()
dim_vendedor.to_csv(buffer, index=False, header=False)
buffer.seek(0)
cursor.copy_expert("COPY dim_vendedor (seller_id) FROM STDIN WITH CSV", buffer)
print(f"dim_vendedor: {len(dim_vendedor)} linhas")


products = pd.read_parquet("data/silver/olist_products_dataset.parquet")
translation = pd.read_parquet("data/silver/product_category_name_translation.parquet")

dim_produto = products.merge(translation, on="product_category_name", how="left")
dim_produto["product_category_name"] = dim_produto["product_category_name"].fillna("sem_categoria")
dim_produto["product_category_name_english"] = dim_produto["product_category_name_english"].fillna(dim_produto["product_category_name"])
dim_produto = dim_produto[["product_id", "product_category_name", "product_category_name_english"]]

buffer = io.StringIO()
dim_produto.to_csv(buffer, index=False, header=False)
buffer.seek(0)
cursor.copy_expert("COPY dim_produto (product_id, product_category_name, product_category_name_english) FROM STDIN WITH CSV", buffer)
print(f"dim_produto: {len(dim_produto)} linhas")


customers = pd.read_parquet("data/silver/olist_customers_dataset.parquet")
geolocation = pd.read_parquet("data/silver/olist_geolocation_dataset.parquet")

geolocation = geolocation.rename(columns={"geolocation_zip_code_prefix": "customer_zip_code_prefix"})
dim_cliente = customers.merge(geolocation, on="customer_zip_code_prefix", how="left")
dim_cliente = dim_cliente[["customer_id", "customer_zip_code_prefix", "customer_city", "customer_state", "geolocation_lat", "geolocation_lng"]]

buffer = io.StringIO()
dim_cliente.to_csv(buffer, index=False, header=False)
buffer.seek(0)
cursor.copy_expert("COPY dim_cliente (customer_id, customer_zip_code_prefix, customer_city, customer_state, geolocation_lat, geolocation_lng) FROM STDIN WITH CSV", buffer)
print(f"dim_cliente: {len(dim_cliente)} linhas")


orders = pd.read_parquet("data/silver/olist_orders_dataset.parquet")

primeira_data = orders["order_purchase_timestamp"].min().normalize()
ultima_data = orders["order_purchase_timestamp"].max().normalize()

dim_data = pd.DataFrame({"data_completa": pd.date_range(primeira_data, ultima_data)})
dim_data["dia"] = dim_data["data_completa"].dt.day
dim_data["mes"] = dim_data["data_completa"].dt.month
dim_data["ano"] = dim_data["data_completa"].dt.year

dias_da_semana = {0: "segunda", 1: "terca", 2: "quarta", 3: "quinta", 4: "sexta", 5: "sabado", 6: "domingo"}
dim_data["dia_semana"] = dim_data["data_completa"].dt.dayofweek.map(dias_da_semana)

buffer = io.StringIO()
dim_data.to_csv(buffer, index=False, header=False)
buffer.seek(0)
cursor.copy_expert("COPY dim_data (data_completa, dia, mes, ano, dia_semana) FROM STDIN WITH CSV", buffer)
print(f"dim_data: {len(dim_data)} linhas")


conexao.commit()

cursor.close()
conexao.close()