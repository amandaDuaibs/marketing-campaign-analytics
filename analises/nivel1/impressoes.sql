--Nível 1
--Impressões

-- Média de impressões por campanha
SELECT ROUND(AVG(impressions), 1) AS media_impressoes FROM fact_campaign;

-- Total de impressões
SELECT SUM(impressions) AS total_impressoes FROM fact_campaign;

-- Top 5 campanhas por impressões
SELECT fc.id_campaign, fc.impressions
FROM fact_campaign fc
ORDER BY fc.impressions DESC
LIMIT 5;

-- Impressões por canal
SELECT
    ch.channel_name,
    SUM(fc.impressions) AS total_impressoes
FROM fact_campaign fc
JOIN dim_channel ch ON fc.id_channel = ch.id_channel
GROUP BY ch.channel_name
ORDER BY total_impressoes DESC;

-- Impressões por tipo de campanha
SELECT
    c.campaign_type,
    SUM(fc.impressions) AS total_impressoes
FROM fact_campaign fc
JOIN dim_campaign c ON fc.id_campaign = c.id_campaign
GROUP BY c.campaign_type
ORDER BY total_impressoes DESC;
