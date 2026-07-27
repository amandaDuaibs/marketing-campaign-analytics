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

