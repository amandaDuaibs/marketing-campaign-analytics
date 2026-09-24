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
- Banco de perguntas de diagnóstico por nível (1, 2 e 3)
- Script de reprodução: o banco inteiro é gerado a partir do CSV em um comando

---
## 📁 Fonte de Dados
**Dado retirado da tabela presente em https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset**  
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
## 🗂️ Estrutura do Repositório

```
marketing-campaign-analytics/
├── README.md
├── sql/                              # ETL e modelagem (rodar nesta ordem)
│   ├── 01_criar_tabelas.sql          # criação das 6 dimensões + tabela fato
│   ├── 02_popular_dimensoes.sql      # carga das dimensões (SELECT DISTINCT)
│   └── 03_popular_fato.sql           # limpeza, mapeamento de IDs e carga da fato
├── analises/
│   ├── nivel1/                       # 10 consultas descritivas
│   │   ├── campanhas.sql             # contagens, duração, maior/menor (CTE + ROW_NUMBER)
│   │   ├── canais.sql                # campanhas por canal
│   │   ├── cliques.sql               # média/total de cliques, top 5, top impressões
│   │   ├── empresas.sql              # empresas e campanhas por empresa
│   │   ├── impressoes.sql            # impressões: média, total, top 5, por canal e tipo
│   │   ├── investimento.sql          # custo médio, min/max, investimento total
│   │   ├── publico.sql               # públicos-alvo e campanhas por público
│   │   ├── roi.sql                   # ROI médio, maior e menor
│   │   ├── segmentacao.sql           # segmentos de cliente
│   │   └── tempo.sql                 # campanhas por ano/mês/trimestre
│   └── diagnostico/                  # banco de perguntas de negócio
│       ├── perguntas-nivel2.sql      # diagnóstico comparativo (canal, tipo, público...)
│       └── perguntas-nivel3.sql      # recomendações e benchmark interno
├── dados/
│   └── marketing_campaign_amostra.csv  # amostra de 500 linhas para reprodução
└── scripts/
    └── criar_banco.py                # gera o banco SQLite a partir do CSV
```

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
2. **Limpeza na staging:** remoção de `$` e vírgulas do `acquisition_cost` com `REPLACE` — **antes** da carga da fato (assim o valor chega na fato já como número)
3. **Mapeamento de IDs** na staging via `UPDATE` ligando cada FK à dimensão
4. **População da fato** via `INSERT INTO ... SELECT`

```sql
-- Limpeza do acquisition_cost (na staging, antes da fato)
UPDATE marketing_campaign_dataset
SET acquisition_cost = REPLACE(REPLACE(acquisition_cost, '$', ''), ',', '');
```

> **Nota de correção:** na primeira versão, a limpeza do custo rodava sobre a fato ainda vazia (e a tabela era recriada depois). Movi a limpeza para a staging, antes da carga — o que garante que `AVG(acquisition_cost)` e somas trabalhem com número de verdade.

---
## 📈 Análises Realizadas (Nível 1 — Descritivas)

| # | Consulta | Técnica | Arquivo |
|---|---|---|---|
| 1 | Contagem total de campanhas | `COUNT(*)` | `campanhas.sql` |
| 2 | Campanhas por tipo | `GROUP BY` + `JOIN dim_campaign` | `campanhas.sql` |
| 3 | Duração média | `AVG(duration)` | `campanhas.sql` |
| 4 | Campanha de maior e menor duração | CTE + `ROW_NUMBER()` + `CASE` | `campanhas.sql` |
| 5 | Campanhas por ano/mês | `GROUP BY year, month` + `JOIN dim_date` | `tempo.sql` |
| 6 | Custo médio de aquisição | `AVG(acquisition_cost)` | `investimento.sql` |
| 7 | Média e total de cliques | `AVG` / `SUM` | `cliques.sql` |
| 8 | Top campanhas por impressões | `ORDER BY` + `LIMIT` | `impressoes.sql` |
| 9 | Impressões por canal e tipo | `SUM` + `GROUP BY` + `JOIN` | `impressoes.sql` |
| 10 | ROI médio, maior e menor | `AVG` / `MAX` / `MIN` | `roi.sql` |

**Exemplo — maior e menor duração (CTE + Window Function):**

```sql
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
```

---
## 📊 Principais Achados

Resultados da execução do ETL e das análises sobre a base completa (200.000 campanhas):

| Métrica | Valor |
|---|---|
| Campanhas analisadas | 200.000 |
| Empresas | 5 |
| Tipos de campanha | 5 (Influencer, Search, Display, Email, Social Media) |
| Canais | 5 (Email, Google Ads, YouTube, Instagram, Website) |
| Período | 2021–2022 (365 datas) |
| Duração média | 37,5 dias (mín. 15 / máx. 60) |
| ROI médio | 5,0 (mín. 2,0 / máx. 8,0) |
| Custo médio de aquisição | US$ 12.504 |
| Média de cliques por campanha | 550 |
| Média de impressões por campanha | 5.507 |

**Observações:**
- A base é sintética e bem balanceada: os 5 tipos de campanha têm participação quase idêntica (Influencer 40.169 a Email 39.870 — variação menor que 1%), e o mesmo vale para canais e empresas. Os achados descrevem a base, não um mercado real.
- Por ser balanceada, o valor do projeto está no **método** (modelagem + ETL + consultas reutilizáveis) e não em diferenças de performance entre grupos.

---
## 🛠️ Stack Utilizada

- **Banco de Dados:** SQLite (DB Browser for SQLite)
- **Linguagem:** SQL · Python (script de reprodução)
- **Modelagem:** Star Schema (Data Warehouse)
- **Conceitos:** CTEs, Window Functions (`ROW_NUMBER`), `CASE`, Agregações, Joins, Type Affinity

---
## 🚀 Como Reproduzir

**Opção 1 — script pronto (recomendado):**
```bash
python scripts/criar_banco.py dados/marketing_campaign_amostra.csv marketing.db
```
Isso cria a staging a partir do CSV e roda o ETL completo (`sql/01`, `02`, `03`) na ordem. Para a base completa, baixe o CSV no Kaggle e aponte o caminho.

**Opção 2 — manual:**
1. Clone o repositório
2. Carregue o CSV na tabela `marketing_campaign_dataset` (DB Browser for SQLite: Database → Import)
3. Execute os scripts na ordem:
   - `sql/01_criar_tabelas.sql` — criação das dimensões e fato
   - `sql/02_popular_dimensoes.sql` — carga das dimensões
   - `sql/03_popular_fato.sql` — limpeza, mapeamento e carga da fato
4. Rode as consultas da pasta `analises/nivel1/`

---
## 🔮 Próximos Passos

- Responder as perguntas de diagnóstico (nível 2) com query + resultado + insight
- Custo por clique (CPC) = `acquisition_cost / clicks`
- Relação duração × ROI
- Dashboard no Power BI / Looker Studio conectado ao banco

---
## 👩‍💻 Autora

**Amanda Duaibs**  
Analista de BI Júnior | Dados, Dashboards e Decisões

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/amanda-duaibs-6b54a81b9/)  
[![Portfólio](https://img.shields.io/badge/Portf%C3%B3lio-4479A1?style=flat&logo=github&logoColor=white)](https://amandaduaibs.github.io/Portfolio-Amanda-Duaibs/)  
📧 amanda.duaibs@gmail.com

---

> *"Dados são o ponto de partida. O insight é o destino."*
