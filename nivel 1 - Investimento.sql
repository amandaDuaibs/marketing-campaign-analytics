--Nível 1
--investimento
-- Custo médio de aquisição
SELECT AVG(acquisition_cost) AS custo_medio FROM fact_campaign;

-- Maior e menor custo de aquisição
SELECT
    MAX(acquisition_cost) AS maior_custo,
    MIN(acquisition_cost) AS menor_custo
FROM fact_campaign;

-- Investimento total
SELECT SUM(acquisition_cost) AS investimento_total FROM fact_campaign;