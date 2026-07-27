--Nível 1

--Segmentação
--Quantos segmentos de clientes existem?
select count(DISTINCT customer_segment) as total_segmentos from dim_audience;

-- Campanhas por segmento de cliente
SELECT
    a.customer_segment,
    COUNT(*) AS total_campanhas
FROM fact_campaign fc
JOIN dim_audience a ON fc.id_audience = a.id_audience
GROUP BY a.customer_segment
ORDER BY total_campanhas DESC;