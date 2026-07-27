--Nível 1

-- Canais
-- Quantas campanhas foram realizadas por canal?
SELECT
	ch.channel_name,
	count(*) as total_campanhas
FROM fact_campaign as fc
JOIN dim_channel as ch
	on fc.id_channel = ch.id_channel
GROUP by
ch.channel_name
ORDER by
total_campanhas desc;