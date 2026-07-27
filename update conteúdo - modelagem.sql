--alterar atividades da coluna
UPDATE fact_campaign
SET acquisition_cost = REPLACE(REPLACE(acquisition_cost, '$', ''), ',', '');
--criar colunas 
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

--updates is ids

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
	
DROP TABLE fact_campaign;	
INSERT INTO fact_campaign (
    id_campaign, id_audience, id_channel, id_date, id_company, id_location,
    duration, acquisition_cost, roi, clicks, impressions, engagement_score
)
SELECT
    id_campaign, id_audience, id_channel, id_date, id_company, id_location,
    duration, acquisition_cost, roi, clicks, impressions, engagement_score
FROM marketing_campaign_dataset;