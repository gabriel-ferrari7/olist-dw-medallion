-- Pergunta 1: receita e ticket medio por categoria e ano
SELECT
    d.ano,
    p.product_category_name_english AS categoria,
    SUM(f.price) AS receita,
    ROUND(SUM(f.price) / COUNT(DISTINCT f.order_id), 2) AS ticket_medio
FROM fato_pedidos_itens f
JOIN dim_produto p ON p.produto_key = f.produto_key
JOIN dim_data d ON d.data_key = f.data_key
WHERE f.order_status NOT IN ('canceled', 'unavailable')
GROUP BY d.ano, p.product_category_name_english
ORDER BY d.ano, receita DESC;

-- Pergunta 2: pedidos e frete por estado do cliente
SELECT
    c.customer_state AS estado,
    COUNT(DISTINCT f.order_id) AS pedidos,
    SUM(f.freight_value) AS frete_total,
    ROUND(SUM(f.freight_value) / COUNT(DISTINCT f.order_id), 2) AS frete_medio_por_pedido
FROM fato_pedidos_itens f
JOIN dim_cliente c ON c.cliente_key = f.cliente_key
WHERE f.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.customer_state
ORDER BY pedidos DESC;

-- Pergunta 3: entrega por vendedor (so vendedores com 100 pedidos entregues ou mais)
SELECT
    v.seller_id,
    COUNT(*) AS pedidos_entregues,
    ROUND(AVG(f.tempo_entrega_dias), 1) AS tempo_medio_dias,
    ROUND(100.0 * COUNT(*) FILTER (WHERE f.entregue_no_prazo) / COUNT(*), 1) AS percentual_no_prazo,
    ROUND(AVG(f.review_score), 2) AS nota_media
FROM fato_pedidos f
JOIN dim_vendedor v ON v.vendedor_key = f.vendedor_key
WHERE f.entregue_no_prazo IS NOT NULL
GROUP BY v.seller_id
HAVING COUNT(*) >= 100
ORDER BY percentual_no_prazo DESC;

-- Pergunta 3 (complemento): nota media dos pedidos entregues no prazo e fora do prazo
WITH pedidos_unicos AS (
    SELECT DISTINCT
        order_id,
        entregue_no_prazo,
        review_score
    FROM fato_pedidos
    WHERE entregue_no_prazo IS NOT NULL
)
SELECT
    entregue_no_prazo,
    COUNT(*) AS pedidos,
    ROUND(AVG(review_score), 2) AS nota_media
FROM pedidos_unicos
GROUP BY entregue_no_prazo
ORDER BY entregue_no_prazo;