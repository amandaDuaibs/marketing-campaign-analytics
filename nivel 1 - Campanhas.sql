--Nível 1:
--Campanhas
-- Quantas campanhas foram realizadas?
SELECT COUNT(*) AS total_campanhas FROM fact_campaign;
-- Quantos tipos de campanha existem?
SELECT count (DISTINCT campaign_type) as total_tipos from dim_campaign;
-- Distribuição de campanhas por tipo
SELECT c.campaign_type,
	count(*) as total_campanhas
FROM fact_campaign as fc
join dim_campaign c 
	on 
	fc.id_campaign = c.id_campaign
GROUP by
	c.campaign_type
ORDER by
	total_campanhas DESC;
-- Duração média das campanhas
select round(avg(duration),1) as duracao_medias_dias from fact_campaign;	
-- Campanha com maior e menor duração
WITH ranked AS (
    SELECT
        fc.id_fact_campaign,
        fc.duration,
        ROW_NUMBER() OVER (ORDER BY fc.duration) AS rn_asc,
        ROW_NUMBER() OVER (ORDER BY fc.duration DESC) AS rn_desc
    FROM fact_campaign fc
)
SELECT
    duration,
    CASE
        WHEN rn_asc = 1 THEN 'menor'
        WHEN rn_desc = 1 THEN 'maior'
    END AS status
FROM ranked
WHERE rn_asc = 1 OR rn_desc = 1
ORDER BY duration DESC;
