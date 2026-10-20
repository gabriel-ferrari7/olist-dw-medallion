import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_products_dataset.parquet")

colunas_numericas = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]

for coluna in colunas_numericas:
    tabela[coluna] = tabela[coluna].astype("float64")

tabela.to_parquet("data/silver/olist_products_dataset.parquet", index=False)

print(tabela.dtypes)