--dim_audience
INSERT INTO dim_audience (
    target_audience,
    customer_segment,
    language
)
SELECT DISTINCT
    target_audience,
    customer_segment,
    language
FROM marketing_campaign_dataset;

alter TABLE marketing_campaign_dataset
RENAME COLUMN campaign_id to id_campaign;

--dim_campaign
INSERT INTO dim_campaign(
    id_campaign,
    campaign_type,
    channel
)

SELECT DISTINCT
    id_campaign,
    campaign_type,
    channel_used

FROM marketing_campaign_dataset;

--channel
INSERT INTO dim_channel (
  	channel_name
)
SELECT DISTINCT
    channel_used
FROM marketing_campaign_dataset;

--dim_date

INSERT INTO dim_date (
    id_date,
    date,
    year,
    month,
    quarter
)
SELECT DISTINCT
    CAST(strftime('%Y%m%d', date) AS INTEGER) AS id_date,
    date,
    CAST(strftime('%Y', date) AS INTEGER) AS year,
    CAST(strftime('%m', date) AS INTEGER) AS month,
    CASE
        WHEN CAST(strftime('%m', date) AS INTEGER) BETWEEN 1 AND 3 THEN 1
        WHEN CAST(strftime('%m', date) AS INTEGER) BETWEEN 4 AND 6 THEN 2
        WHEN CAST(strftime('%m', date) AS INTEGER) BETWEEN 7 AND 9 THEN 3
        ELSE 4
    END AS quarter
FROM marketing_campaign_dataset;
    
-- company
INSERT INTO dim_company (
  	company_name
)
SELECT DISTINCT
    company
FROM marketing_campaign_dataset;

--location
INSERT INTO dim_location (
  	location
)
SELECT DISTINCT
    location
FROM marketing_campaign_dataset;



  
SELECT * from marketing_campaign_dataset;
select * from dim_audience;
select * from dim_campaign;
SELECT * from dim_channel;
SELECT * from dim_date;
SELECT * from dim_location;
SELECT * from dim_company;
SELECT * from fact_campaign;