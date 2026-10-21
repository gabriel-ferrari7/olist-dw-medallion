import pandas as pd

tabela = pd.read_parquet("data/silver/olist_order_items_dataset.parquet")

vendedores_por_pedido = tabela.groupby("order_id")["seller_id"].nunique()

print(len(vendedores_por_pedido))
print((vendedores_por_pedido > 1).sum())
print(vendedores_por_pedido.value_counts().sort_index())