import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_order_reviews_dataset.parquet")

tabela["review_score"] = tabela["review_score"].astype("int64")
tabela["review_creation_date"] = pd.to_datetime(tabela["review_creation_date"], format="%Y-%m-%d %H:%M:%S")
tabela["review_answer_timestamp"] = pd.to_datetime(tabela["review_answer_timestamp"], format="%Y-%m-%d %H:%M:%S")

tabela.to_parquet("data/silver/olist_order_reviews_dataset.parquet", index=False)

print(tabela.dtypes)