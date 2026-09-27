"""
Dashboard de campanhas de marketing — marketing-campaign-analytics
App Streamlit que lê o banco SQLite (star schema) e publica as análises nível 1.

Uso local:
    pip install -r requirements.txt
    streamlit run app.py
"""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Marketing Campaign Analytics",
    page_icon="📊",
    layout="wide",
)

DB = Path(__file__).parent / "marketing.db"

# ------------------------------------------------------------------
# Dados (cache: o banco só é relido se o arquivo mudar)
# ------------------------------------------------------------------
@st.cache_data
def carregar_dados() -> dict[str, pd.DataFrame]:
    conn = sqlite3.connect(DB)
    tabelas = {
        "fato": """
            SELECT f.*, ch.channel_name, co.company_name, loc.location,
                   d.date, d.year, d.month, d.quarter
            FROM fact_campaign f
            LEFT JOIN dim_channel ch ON f.id_channel = ch.id_channel
            LEFT JOIN dim_company co ON f.id_company = co.id_company
            LEFT JOIN dim_location loc ON f.id_location = loc.id_location
            LEFT JOIN dim_date d ON f.id_date = d.id_date
        """,
        "canais": "SELECT * FROM dim_channel",
        "empresas": "SELECT * FROM dim_company",
        "locais": "SELECT * FROM dim_location",
    }
    dados = {nome: pd.read_sql(sql, conn) for nome, sql in tabelas.items()}
    conn.close()
    fat = dados["fato"].copy()
    fat["date"] = pd.to_datetime(fat["date"])
    fat["ctr"] = fat["clicks"] / fat["impressions"].replace(0, pd.NA)
    fat["cpc"] = fat["acquisition_cost"] / fat["clicks"].replace(0, pd.NA)
    fat["mes"] = fat["date"].dt.strftime("%Y-%m")
    dados["fato"] = fat
    return dados


dados = carregar_dados()
fat = dados["fato"]

# ------------------------------------------------------------------
# Filtros (sidebar)
# ------------------------------------------------------------------
st.sidebar.header("Filtros")
canais = st.sidebar.multiselect(
    "Canal", sorted(fat["channel_name"].dropna().unique())
)
empresas = st.sidebar.multiselect(
    "Empresa", sorted(fat["company_name"].dropna().unique())
)
locais = st.sidebar.multiselect(
    "Local", sorted(fat["location"].dropna().unique())
)
meses = st.sidebar.multiselect(
    "Mês", sorted(fat["mes"].dropna().unique())
)

df = fat.copy()
if canais:
    df = df[df["channel_name"].isin(canais)]
if empresas:
    df = df[df["company_name"].isin(empresas)]
if locais:
    df = df[df["location"].isin(locais)]
if meses:
    df = df[df["mes"].isin(meses)]

if df.empty:
    st.warning("Nenhum dado para os filtros escolhidos.")
    st.stop()

# ------------------------------------------------------------------
# Cabeçalho
# ------------------------------------------------------------------
st.title("📊 Marketing Campaign Analytics")
st.caption(
    "Dashboard sobre o data warehouse em SQLite do projeto "
    "[marketing-campaign-analytics](https://github.com/amandaDuaibs/marketing-campaign-analytics) — "
    "dados públicos (Kaggle)."
)

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
total_cost = df["acquisition_cost"].sum()
total_clicks = df["clicks"].sum()
total_impr = df["impressions"].sum()
ctr_medio = total_clicks / total_impr if total_impr else 0
roi_medio = df["roi"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Campanhas", f"{len(df):,}")
c2.metric("Investimento", f"US$ {total_cost:,.0f}")
c3.metric("Cliques", f"{total_clicks:,}")
c4.metric("CTR médio", f"{ctr_medio:.2%}")
c5.metric("ROI médio", f"{roi_medio:.2f}")

st.divider()

# ------------------------------------------------------------------
# Gráficos
# ------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("ROI médio por canal")
    g1 = (
        df.groupby("channel_name", as_index=False)["roi"].mean()
        .sort_values("roi", ascending=False)
    )
    fig1 = px.bar(
        g1, x="channel_name", y="roi", text_auto=".2f",
        labels={"channel_name": "Canal", "roi": "ROI médio"},
        color_discrete_sequence=["#0E7C8C"],
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("CTR médio por canal")
    g2 = (
        df.groupby("channel_name", as_index=False)
        .agg(impr=("impressions", "sum"), cli=("clicks", "sum"))
    )
    g2["ctr"] = g2["cli"] / g2["impr"]
    fig2 = px.bar(
        g2, x="channel_name", y="ctr", text_auto=".2%",
        labels={"channel_name": "Canal", "ctr": "CTR"},
        color_discrete_sequence=["#02255F"],
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Evolução mensal (ROI médio)")
g3 = df.groupby("mes", as_index=False).agg(roi=("roi", "mean"), n=("id_campaign", "count"))
fig3 = px.line(
    g3, x="mes", y="roi", markers=True,
    labels={"mes": "Mês", "roi": "ROI médio"},
    color_discrete_sequence=["#02255F"],
)
st.plotly_chart(fig3, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Campanhas por empresa")
    g4 = df.groupby("company_name", as_index=False)["id_campaign"].count()
    fig4 = px.pie(
        g4, names="company_name", values="id_campaign", hole=0.4,
        color_discrete_sequence=px.colors.sequential.Teal,
    )
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("ROI por local")
    g5 = (
        df.groupby("location", as_index=False)["roi"].mean()
        .sort_values("roi", ascending=False)
    )
    fig5 = px.bar(
        g5, x="location", y="roi", text_auto=".2f",
        labels={"location": "Local", "roi": "ROI médio"},
        color_discrete_sequence=["#0E7C8C"],
    )
    st.plotly_chart(fig5, use_container_width=True)

# ------------------------------------------------------------------
# Tabela de detalhe
# ------------------------------------------------------------------
st.subheader("Detalhe por empresa e canal")
g6 = (
    df.groupby(["company_name", "channel_name"], as_index=False)
    .agg(
        campanhas=("id_campaign", "count"),
        investimento=("acquisition_cost", "sum"),
        roi_medio=("roi", "mean"),
        cliques=("clicks", "sum"),
        impressoes=("impressions", "sum"),
    )
)
g6["ctr"] = g6["cliques"] / g6["impressoes"]
st.dataframe(
    g6.style.format(
        {
            "investimento": "US$ {:,.0f}",
            "roi_medio": "{:.2f}",
            "ctr": "{:.2%}",
        }
    ),
    use_container_width=True,
)

st.caption(
    "Dados públicos (Kaggle) · Star schema em SQLite · "
    "Repositório: github.com/amandaDuaibs/marketing-campaign-analytics"
)
