-- ETL da tabela fato
-- Ordem correta: limpeza na staging ANTES da carga da fato

-- 1. Limpeza do acquisition_cost na staging
-- (o valor chega como texto '$16,174.00'; sem essa limpeza o SQLite
--  não converte para número e as médias ignoram as linhas)
UPDATE marketing_campaign_dataset
SET acquisition_cost = REPLACE(REPLACE(acquisition_cost, '$', ''), ',', '');

-- 2. Colunas de ID na staging
ALTER TABLE marketing_campaign_dataset
ADD COLUMN id_audience INTEGER;

ALTER TABLE marketing_campaign_dataset
ADD COLUMN id_channel INTEGER;

ALTER TABLE marketing_campaign_dataset
ADD COLUMN id_company INTEGER;

ALTER TABLE marketing_campaign_dataset
ADD COLUMN id_date INTEGER;

ALTER TABLE marketing_campaign_dataset
ADD COLUMN id_location INTEGER;

-- 3. Mapeamento dos IDs (staging → dimensões)

UPDATE marketing_campaign_dataset as mkt
SET id_location = (
SELECT id_location
FROM dim_location as l
WHERE l.location =mkt.location
);

UPDATE marketing_campaign_dataset AS mkt
SET id_audience = (
    SELECT id_audience
    FROM dim_audience AS a
    WHERE a.target_audience = mkt.Target_Audience
      AND a.customer_segment = mkt.Customer_Segment
      AND a.language = mkt.Language
);

UPDATE marketing_campaign_dataset AS mkt
SET id_channel = (
    SELECT id_channel
    FROM dim_channel AS ch
    WHERE ch.channel_name = mkt.channel_used);
	
UPDATE marketing_campaign_dataset AS mkt
SET id_company = (
    SELECT id_company
    FROM dim_company AS co
    WHERE co.company_name = mkt.Company);

UPDATE marketing_campaign_dataset AS mkt
SET id_date = (
    SELECT id_date
    FROM dim_date AS d
    WHERE d.date = mkt.date);

-- 4. Carga da fato (com os IDs já mapeados e o custo já limpo)
INSERT INTO fact_campaign (
    id_campaign, id_audience, id_channel, id_date, id_company, id_location,
    duration, acquisition_cost, roi, clicks, impressions, engagement_score
)
SELECT
    id_campaign, id_audience, id_channel, id_date, id_company, id_location,
    duration, acquisition_cost, roi, clicks, impressions, engagement_score
FROM marketing_campaign_dataset;
