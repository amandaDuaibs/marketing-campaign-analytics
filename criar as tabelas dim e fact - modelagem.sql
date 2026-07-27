CREATE TABLE dim_audience (
    id_audience INTEGER PRIMARY KEY,
    target_audience TEXT,
    customer_segment TEXT,
    language TEXT
);
CREATE TABLE dim_campaign (
    id_campaign INTEGER PRIMARY KEY,
    campaign_type TEXT,
    channel TEXT
);

CREATE TABLE dim_date (
    id_date INTEGER PRIMARY KEY,
    date DATE,
    year INTEGER,
    month INTEGER,
    quarter INTEGER
);

CREATE TABLE dim_channel (

    id_channel INTEGER PRIMARY KEY,

    channel_name TEXT

);


CREATE TABLE dim_company (

    id_company integer PRIMARY key AUTOINCREMENT,

    company_name TEXT

);

CREATE TABLE dim_location (

    id_location integer PRIMARY key AUTOINCREMENT,

    location TEXT

);

CREATE TABLE fact_campaign (
    id_fact_campaign INTEGER PRIMARY KEY AUTOINCREMENT,
    id_campaign INTEGER,
    id_audience INTEGER,
    id_channel INTEGER,
    id_date INTEGER,
    id_company INTEGER,
	id_location INTEGER,
    duration INTEGER,
    acquisition_cost REAL,
    roi REAL,
    clicks INTEGER,
    impressions INTEGER,
    engagement_score REAL,
    FOREIGN KEY (id_campaign) REFERENCES dim_campaign(id_campaign),
    FOREIGN KEY (id_audience) REFERENCES dim_audience(id_audience),
    FOREIGN KEY (id_channel) REFERENCES dim_channel(id_channel),
    FOREIGN KEY (id_date) REFERENCES dim_date(id_date),
    FOREIGN KEY (id_company) REFERENCES dim_company(id_company),
	FOREIGN KEY (id_location) REFERENCES dim_location(id_location)
);

