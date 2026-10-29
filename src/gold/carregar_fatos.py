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

cursor.execute("TRUNCATE fato_pedidos_itens, fato_pedidos")


cursor.execute("SELECT produto_key, product_id FROM dim_produto")
chaves_produto = pd.DataFrame(cursor.fetchall(), columns=["produto_key", "product_id"])

cursor.execute("SELECT cliente_key, customer_id FROM dim_cliente")
chaves_cliente = pd.DataFrame(cursor.fetchall(), columns=["cliente_key", "customer_id"])

cursor.execute("SELECT vendedor_key, seller_id FROM dim_vendedor")
chaves_vendedor = pd.DataFrame(cursor.fetchall(), columns=["vendedor_key", "seller_id"])

cursor.execute("SELECT data_key, data_completa FROM dim_data")
chaves_data = pd.DataFrame(cursor.fetchall(), columns=["data_key", "data_completa"])
chaves_data["data_completa"] = pd.to_datetime(chaves_data["data_completa"])


orders = pd.read_parquet("data/silver/olist_orders_dataset.parquet")
order_items = pd.read_parquet("data/silver/olist_order_items_dataset.parquet")
order_reviews = pd.read_parquet("data/silver/olist_order_reviews_dataset.parquet")

orders["data_completa"] = orders["order_purchase_timestamp"].dt.normalize()
orders = orders.merge(chaves_data, on="data_completa", how="left")
orders = orders.merge(chaves_cliente, on="customer_id", how="left")


fato_pedidos_itens = order_items.merge(orders[["order_id", "order_status", "cliente_key", "data_key"]], on="order_id", how="left")
fato_pedidos_itens = fato_pedidos_itens.merge(chaves_produto, on="product_id", how="left")
fato_pedidos_itens = fato_pedidos_itens.merge(chaves_vendedor, on="seller_id", how="left")
fato_pedidos_itens = fato_pedidos_itens[
    ["order_id", "order_item_id", "order_status", "produto_key", "cliente_key", "vendedor_key", "data_key", "price", "freight_value"]
]

buffer = io.StringIO()
fato_pedidos_itens.to_csv(buffer, index=False, header=False)
buffer.seek(0)
cursor.copy_expert(
    "COPY fato_pedidos_itens (order_id, order_item_id, order_status, produto_key, cliente_key, vendedor_key, data_key, price, freight_value) FROM STDIN WITH CSV",
    buffer,
)
print(f"fato_pedidos_itens: {len(fato_pedidos_itens)} linhas")


foi_entregue = (orders["order_status"] == "delivered") & orders["order_delivered_customer_date"].notna()
dias_ate_entrega = (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.days
chegou_no_prazo = orders["order_delivered_customer_date"].dt.normalize() <= orders["order_estimated_delivery_date"].dt.normalize()

orders["tempo_entrega_dias"] = dias_ate_entrega.where(foi_entregue).astype("Int64")
orders["entregue_no_prazo"] = chegou_no_prazo.where(foi_entregue).astype("boolean")

order_reviews = order_reviews.sort_values("review_answer_timestamp")
ultima_avaliacao = order_reviews.drop_duplicates(subset="order_id", keep="last")
orders = orders.merge(ultima_avaliacao[["order_id", "review_score"]], on="order_id", how="left")
orders["review_score"] = orders["review_score"].astype("Int64")

pedidos_vendedores = order_items[["order_id", "seller_id"]].drop_duplicates()
fato_pedidos = orders.merge(pedidos_vendedores, on="order_id", how="inner")
fato_pedidos = fato_pedidos.merge(chaves_vendedor, on="seller_id", how="left")
fato_pedidos = fato_pedidos[
    ["order_id", "vendedor_key", "cliente_key", "data_key", "order_status", "tempo_entrega_dias", "entregue_no_prazo", "review_score"]
]

buffer = io.StringIO()
fato_pedidos.to_csv(buffer, index=False, header=False)
buffer.seek(0)
cursor.copy_expert(
    "COPY fato_pedidos (order_id, vendedor_key, cliente_key, data_key, order_status, tempo_entrega_dias, entregue_no_prazo, review_score) FROM STDIN WITH CSV",
    buffer,
)
print(f"fato_pedidos: {len(fato_pedidos)} linhas")


conexao.commit()

cursor.close()
conexao.close()