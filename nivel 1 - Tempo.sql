--Nível 1 
--TEMPO
--quantas campanhas divemos, divididas em ano, mes e quarter
SELECT
    d.year,
    d.month,
    d.quarter,
    COUNT(*) AS total_campanhas
FROM fact_campaign fc
JOIN dim_date d ON fc.id_date = d.id_date
GROUP BY d.year, d.month, d.quarter
ORDER BY d.year, d.month;