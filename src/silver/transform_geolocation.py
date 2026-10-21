import pandas as pd

tabela = pd.read_parquet("data/bronze/olist_geolocation_dataset.parquet")

tabela["geolocation_lat"] = tabela["geolocation_lat"].astype("float64")
tabela["geolocation_lng"] = tabela["geolocation_lng"].astype("float64")

tabela = tabela.groupby("geolocation_zip_code_prefix").agg(
    geolocation_lat=("geolocation_lat", "mean"),
    geolocation_lng=("geolocation_lng", "mean"),
    geolocation_city=("geolocation_city", "first"),
    geolocation_state=("geolocation_state", "first"),
).reset_index()

tabela.to_parquet("data/silver/olist_geolocation_dataset.parquet", index=False)

print(len(tabela))
print(tabela.dtypes)