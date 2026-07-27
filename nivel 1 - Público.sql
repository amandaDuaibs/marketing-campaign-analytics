--Nível 1

--Público
-- Quantos públicos-alvo existem?
SELECT COUNT(*) AS total_publicos FROM dim_audience;

-- Quantas campanhas por público?
SELECT
    a.target_audience,
    a.customer_segment,
    COUNT(*) AS total_campanhas
FROM fact_campaign fc
JOIN dim_audience a ON fc.id_audience = a.id_audience
GROUP BY a.target_audience, a.customer_segment
ORDER BY total_campanhas DESC;