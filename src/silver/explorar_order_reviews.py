import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

tabela = pd.read_parquet("data/bronze/olist_order_reviews_dataset.parquet")
print(tabela.head())
print(tabela.isna().sum())
print(tabela["review_id"].duplicated().sum())
print(tabela["order_id"].duplicated().sum())
print(tabela["review_score"].value_counts().sort_index())

repetidos = tabela[tabela["review_id"].duplicated(keep=False)]
print(repetidos.sort_values("review_id")[["review_id", "order_id", "review_score", "review_creation_date"]].head(6))