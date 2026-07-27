# 📊 Marketing Campaign Analytics — Star Schema + SQL Analysis

Projeto de **modelagem dimensional e análise descritiva** de campanhas de marketing.  
Partindo de uma base flat, construí um star schema em SQLite e executei consultas analíticas para extrair insights de performance, investimento e engajamento.

---
## 📌 Sobre o Projeto

Este projeto simula o dia a dia de um **Analista de BI** especializado em marketing: pegar dados crus, modelar, limpar, documentar e extrair respostas de negócio através de SQL.

**Principais entregas:**
- Modelagem dimensional (6 dimensões + 1 tabela fato)
- ETL completo com SQL puro
- Consultas descritivas de Nível 1 (contagens, médias, rankings, distribuições)
- Documentação do schema e das análises

---
## 📁 Fonte de Dados
** https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset 
**Tabela staging:** `marketing_campaign_dataset` — dados flat de campanhas multicanais.

| Coluna | Tipo Original | Descrição |
|---|---|---|
| Campaign_ID | INTEGER | ID da campanha |
| Company | TEXT | Nome da empresa |
| Campaign_Type | TEXT | Tipo (Display, SEO, Email, Social Media...) |
| Target_Audience | TEXT | Público-alvo |
| Duration | TEXT | Duração em dias |
| Channel_Used | TEXT | Canal utilizado |
| Conversion_Rate | REAL | Taxa de conversão |
| Acquisition_Cost | TEXT | Custo de aquisição (formato `$16,174.00`) |
| ROI | REAL | Retorno sobre investimento |
| Location | TEXT | Localização |
| Language | TEXT | Idioma |
| Clicks | INTEGER | Número de cliques |
| Impressions | INTEGER | Número de impressões |
| Engagement_Score | INTEGER | Pontuação de engajamento |
| Customer_Segment | TEXT | Segmento do cliente |
| Date | TEXT | Data da campanha |

---
## 🏗️ Modelagem — Star Schema

### Dimensões

```sql
-- dim_audience
id_audience       INTEGER PK
target_audience   TEXT
customer_segment  TEXT
language          TEXT

-- dim_campaign
id_campaign       INTEGER PK
campaign_type     TEXT
channel           TEXT

-- dim_channel
id_channel        INTEGER PK
channel_name      TEXT

-- dim_company
id_company        INTEGER PK
company_name      TEXT

-- dim_date
id_date           INTEGER PK
date              DATE
year              INTEGER
month             INTEGER
quarter           INTEGER

-- dim_location
id_location       INTEGER PK
location          TEXT
```
### Tabela Fato

| Coluna | Tipo | Descrição |
|---|---|---|
| id_fact_campaign | INTEGER PK | surrogate key (AUTOINCREMENT) |
| id_campaign | INTEGER FK | → dim_campaign(id_campaign) |
| id_audience | INTEGER FK | → dim_audience(id_audience) |
| id_channel | INTEGER FK | → dim_channel(id_channel) |
| id_date | INTEGER FK | → dim_date(id_date) |
| id_company | INTEGER FK | → dim_company(id_company) |
| id_location | INTEGER FK | → dim_location(id_location) |
| duration | INTEGER | Duração em dias |
| acquisition_cost | REAL | Custo de aquisição |
| roi | REAL | Retorno sobre investimento |
| clicks | INTEGER | Número de cliques |
| impressions | INTEGER | Número de impressões |
| engagement_score | REAL | Pontuação de engajamento |

---
## 🔄 Processo de ETL

1. **Carga das dimensões** com `SELECT DISTINCT` da staging
2. **População da fato** via `INSERT INTO ... SELECT ... JOIN` ligando cada FK à staging
3. **Limpeza de dados:** remoção de `$` e vírgulas do `acquisition_cost` com `REPLACE` + `CAST`

```sql
-- Limpeza do acquisition_cost
UPDATE fact_campaign
SET acquisition_cost = CAST(
    REPLACE(REPLACE(acquisition_cost, '$', ''), ',', '') AS REAL
);
```

---

## 📈 Análises Realizadas (Nível 1 — Descritivas)

| # | Consulta | Técnica |
|---|---|---|
| 1 | Contagem total de campanhas | `COUNT(*)` |
| 2 | Campanhas por tipo | `GROUP BY` + `JOIN dim_campaign` |
| 3 | Duração média | `AVG(duration)` |
| 4 | Campanha de maior e menor duração | CTE + `ROW_NUMBER()` + `CASE` |
| 5 | Campanhas por ano/mês | `GROUP BY year, month` + `JOIN dim_date` |
| 6 | Custo médio de aquisição | `AVG(acquisition_cost)` |
| 7 | Média de cliques | `AVG(clicks)` |
| 8 | Média de impressões | `AVG(impressions)` |
| 9 | ROI médio | `AVG(roi)` |
| 10 | Visão geral de KPIs | Query única com múltiplos agregadores |

**Exemplo — maior e menor duração (CTE + Window Function):**

```sql
WITH ranked AS (
    SELECT
        fc.id_fact_campaign,
        c.campaign_type,
        fc.duration,
        ROW_NUMBER() OVER (ORDER BY fc.duration) AS rn_asc,
        ROW_NUMBER() OVER (ORDER BY fc.duration DESC) AS rn_desc
    FROM fact_campaign fc
    JOIN dim_campaign c ON fc.id_campaign = c.id_campaign
)
SELECT
    campaign_type AS campaign_name,
    duration,
    CASE
        WHEN rn_asc = 1 THEN 'menor'
        WHEN rn_desc = 1 THEN 'maior'
    END AS status
FROM ranked
WHERE rn_asc = 1 OR rn_desc = 1
ORDER BY duration DESC;
```

---

## 🛠️ Stack Utilizada

- **Banco de Dados:** SQLite (DB Browser for SQLite)
- **Linguagem:** SQL
- **Modelagem:** Star Schema (Data Warehouse)
- **Conceitos:** CTEs, Window Functions (`ROW_NUMBER`), `CASE`, Agregações, Joins, Type Affinity

---

## 🚀 Como Reproduzir

1. Clone o repositório
2. Abra o arquivo `.db` no DB Browser for SQLite (ou qualquer cliente SQLite)
3. Execute os scripts na ordem:
   - `01_create_tables.sql` — criação das dimensões e fato
   - `02_populate_dimensions.sql` — carga das dimensões
   - `03_populate_fact.sql` — carga e limpeza da fato
   - `04_analysis_queries.sql` — consultas analíticas

---

## 🔮 Próximos Passos

- Custo por clique (CPC) = `acquisition_cost / clicks`
- Relação duração × ROI
- Eficiência por canal
- Segmentação por público × conversão
- Análise temporal de sazonalidade
- Top N campanhas por clique, ROI e impressão
- Dashboard no Power BI / Looker Studio conectado ao banco

---

## 👩‍💻 Autora

**Amanda Duaibs**  
Analista de BI Júnior | Dados, Dashboards e Decisões

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/amanda-duaibs-6b54a81b9/)  
📧 amanda.duaibs@gmail.com

---

> *"Dados são o ponto de partida. O insight é o destino."*

