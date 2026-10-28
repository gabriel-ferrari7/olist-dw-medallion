
DROP TABLE IF EXISTS fato_pedidos;
DROP TABLE IF EXISTS fato_pedidos_itens;
DROP TABLE IF EXISTS dim_data;
DROP TABLE IF EXISTS dim_cliente;
DROP TABLE IF EXISTS dim_produto;
DROP TABLE IF EXISTS dim_vendedor;

CREATE TABLE dim_vendedor (
    vendedor_key SERIAL PRIMARY KEY,
    seller_id VARCHAR(32) NOT NULL UNIQUE
);

CREATE TABLE dim_produto (
    produto_key SERIAL PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL UNIQUE,
    product_category_name VARCHAR(100) NOT NULL,
    product_category_name_english VARCHAR(100) NOT NULL
);

CREATE TABLE dim_cliente (
    cliente_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL UNIQUE,
    customer_zip_code_prefix VARCHAR(5) NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state VARCHAR(2) NOT NULL,
    geolocation_lat DECIMAL(9, 6),
    geolocation_lng DECIMAL(9, 6)
);

CREATE TABLE dim_data (
    data_key SERIAL PRIMARY KEY,
    data_completa DATE NOT NULL UNIQUE,
    dia INT NOT NULL,
    mes INT NOT NULL,
    ano INT NOT NULL,
    dia_semana VARCHAR(10) NOT NULL
);

CREATE TABLE fato_pedidos_itens (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INT NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    produto_key INT NOT NULL REFERENCES dim_produto (produto_key),
    cliente_key INT NOT NULL REFERENCES dim_cliente (cliente_key),
    vendedor_key INT NOT NULL REFERENCES dim_vendedor (vendedor_key),
    data_key INT NOT NULL REFERENCES dim_data (data_key),
    price DECIMAL(10, 2) NOT NULL,
    freight_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE fato_pedidos (
    order_id VARCHAR(32) NOT NULL,
    vendedor_key INT NOT NULL REFERENCES dim_vendedor (vendedor_key),
    cliente_key INT NOT NULL REFERENCES dim_cliente (cliente_key),
    data_key INT NOT NULL REFERENCES dim_data (data_key),
    order_status VARCHAR(20) NOT NULL,
    tempo_entrega_dias INT,
    entregue_no_prazo BOOLEAN,
    review_score INT,
    PRIMARY KEY (order_id, vendedor_key)
);