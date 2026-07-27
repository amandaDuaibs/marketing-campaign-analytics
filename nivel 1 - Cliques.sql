--Nível 1
--clicks
-- Média de cliques por campanha
SELECT ROUND(AVG(clicks), 1) AS media_cliques FROM fact_campaign;

-- Total de cliques
SELECT SUM(clicks) AS total_cliques FROM fact_campaign;

-- Campanha com mais cliques (top 5)
SELECT fc.id_campaign, fc.clicks
FROM fact_campaign fc
ORDER BY fc.clicks DESC
LIMIT 5;

-- Campanha com mais impressões
SELECT fc.id_campaign, fc.impressions
FROM fact_campaign fc
ORDER BY fc.impressions DESC
LIMIT 1;