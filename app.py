"""
Dashboard de campanhas de marketing — marketing-campaign-analytics
App Streamlit v2 que lê o banco SQLite (star schema) e publica as análises.

Novidades da v2:
- Tema dark Van Gogh (azul-noite + dourado), alinhado à identidade visual da marca
- Slider de período (data inicial → data final)
- Abas que espelham as pastas analises/nivel1|2|3
- Explorador dimensão × métrica (Canal, Empresa, Tipo, Público, Segmento, Local)
- Drill-down em cascata: empresa → canal → tipo, com top 15 campanhas

Uso local:
    pip install -r requirements.txt
    python scripts/criar_banco.py dados/marketing_campaign_amostra.csv marketing.db
    streamlit run app.py

Na nuvem (Streamlit Community Cloud) o marketing.db não vem do repo: o app
constrói o banco sozinho na primeira carga, a partir do CSV de amostra e dos
scripts sql/ do projeto.
"""
import csv
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Identidade visual — Van Gogh "Noite Estrelada" (marca da Amanda)
# ------------------------------------------------------------------
NAVY = "#0D1B3E"        # fundo azul-noite
NAVY_2 = "#16295C"      # azul secundário
GOLD = "#F2C94C"        # acento dourado
CREAM = "#F5F1E6"       # texto claro
TEAL = "#0E7C8C"        # apoio (herda da v1)
AZUL = "#4C6FBF"        # apoio frio

PALETA = [GOLD, AZUL, TEAL, "#8A6FBF", "#BF6F5A", "#6FBF9E", "#BF9E6F", "#BF4F6F"]

st.set_page_config(
    page_title="Marketing Campaign Analytics",
    page_icon="📊",
    layout="wide",
)

# Tema escuro Van Gogh via CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {NAVY};
        color: {CREAM};
    }}
    .stApp header {{
        background: transparent;
    }}
    [data-testid="stSidebar"] {{
        background-color: {NAVY_2};
    }}
    [data-testid="stSidebar"] * {{
        color: {CREAM};
    }}
    div[data-testid="stMetric"] {{
        background-color: {NAVY_2};
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid rgba(242, 201, 76, 0.25);
    }}
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div[data-testid="stMetricLabel"] {{
        color: {CREAM};
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {GOLD};
    }}
    h1, h2, h3, .stMarkdown {{
        color: {CREAM};
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {CREAM};
        background-color: {NAVY_2};
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
    }}
    .stTabs [aria-selected="true"] {{
        color: {NAVY} !important;
        background-color: {GOLD} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def vangogh(fig: go.Figure) -> go.Figure:
    """Aplica o tema Van Gogh a um gráfico Plotly (fundo, fonte e grades)."""
    fig.update_layout(
        paper_bgcolor=NAVY_2,
        plot_bgcolor=NAVY_2,
        font_color=CREAM,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.12)", linecolor="rgba(255,255,255,0.25)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.12)", linecolor="rgba(255,255,255,0.25)")
    return fig


DB = Path(__file__).parent / "marketing.db"


def _garantir_banco() -> str:
    """Garante um banco com o ETL rodado.

    1. Se existir um marketing.db junto ao app (rodada local), usa ele.
    2. Senão (Streamlit Cloud: FS read-only), constrói o banco em pasta
       temporária a partir do CSV de amostra + scripts sql/ do repo.
    """
    if DB.exists():
        return str(DB)

    st.info("Construindo o banco pela primeira vez (a partir do CSV de amostra)...", icon="⏳")
    caminho_csv = Path(__file__).parent / "dados" / "marketing_campaign_amostra.csv"
    pasta_sql = Path(__file__).parent / "sql"
    tmp = Path(tempfile.mkdtemp())
    banco = tmp / "marketing.db"

    conn = sqlite3.connect(banco)
    cur = conn.cursor()

    with open(caminho_csv, newline="", encoding="utf-8") as f:
        leitor = csv.reader(f)
        header = next(leitor)
        linhas = list(leitor)

    colunas = ", ".join(f'"{c}" TEXT' for c in header)
    cur.execute(f"CREATE TABLE marketing_campaign_dataset ({colunas})")
    placeholders = ", ".join("?" * len(header))
    cur.executemany(
        f"INSERT INTO marketing_campaign_dataset VALUES ({placeholders})", linhas
    )
    conn.commit()

    for script in ["01_criar_tabelas.sql", "02_popular_dimensoes.sql", "03_popular_fato.sql"]:
        cur.executescript((pasta_sql / script).read_text(encoding="utf-8"))
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM fact_campaign")
    n = cur.fetchone()[0]
    conn.close()
    st.info(f"Banco pronto: {n} campanhas carregadas.", icon="✅")
    return str(banco)


DB_PATH = _garantir_banco()

# ------------------------------------------------------------------
# Dados (cache: o banco só é relido se o arquivo mudar)
# ------------------------------------------------------------------
@st.cache_data
def carregar_dados() -> dict[str, pd.DataFrame]:
    conn = sqlite3.connect(DB_PATH)
    tabelas = {
        "fato": """
            SELECT f.*, ch.channel_name, co.company_name, loc.location,
                   dc.campaign_type, da.target_audience, da.customer_segment,
                   d.date, d.year, d.month, d.quarter
            FROM fact_campaign f
            LEFT JOIN dim_channel ch ON f.id_channel = ch.id_channel
            LEFT JOIN dim_company co ON f.id_company = co.id_company
            LEFT JOIN dim_location loc ON f.id_location = loc.id_location
            LEFT JOIN dim_campaign dc ON f.id_campaign = dc.id_campaign
            LEFT JOIN dim_audience da ON f.id_audience = da.id_audience
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


@st.cache_data
def aplicar_filtros(_fat: pd.DataFrame, canais: tuple, empresas: tuple, locais: tuple, periodo: tuple) -> pd.DataFrame:
    df = _fat.copy()
    if canais:
        df = df[df["channel_name"].isin(canais)]
    if empresas:
        df = df[df["company_name"].isin(empresas)]
    if locais:
        df = df[df["location"].isin(locais)]
    d1, d2 = pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1])
    df = df[(df["date"] >= d1) & (df["date"] <= d2)]
    return df


dados = carregar_dados()
fat = dados["fato"]

# ------------------------------------------------------------------
# Filtros (sidebar)
# ------------------------------------------------------------------
st.sidebar.header("Filtros")

d_min, d_max = fat["date"].min(), fat["date"].max()
periodo = st.sidebar.slider(
    "Período",
    min_value=d_min.to_pydatetime().date(),
    max_value=d_max.to_pydatetime().date(),
    value=(d_min.to_pydatetime().date(), d_max.to_pydatetime().date()),
    format="DD/MM/YYYY",
)

canais = st.sidebar.multiselect("Canal", sorted(fat["channel_name"].dropna().unique()))
empresas = st.sidebar.multiselect("Empresa", sorted(fat["company_name"].dropna().unique()))
locais = st.sidebar.multiselect("Local", sorted(fat["location"].dropna().unique()))

df = aplicar_filtros(fat, tuple(canais), tuple(empresas), tuple(locais), tuple(periodo))

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
# Layout em abas — espelha as pastas analises/nivel1|2|3
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Visão geral", "Por dimensão", "Tendências", "Drill-down"])

# ============================ ABA 1 — VISÃO GERAL ============================
with tab1:
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
            color_discrete_sequence=[GOLD],
        )
        st.plotly_chart(vangogh(fig1), use_container_width=True, key="grafico1")

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
            color_discrete_sequence=[AZUL],
        )
        st.plotly_chart(vangogh(fig2), use_container_width=True, key="grafico2")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Campanhas por empresa")
        g4 = df.groupby("company_name", as_index=False)["id_campaign"].count()
        fig4 = px.pie(
            g4, names="company_name", values="id_campaign", hole=0.4,
            color_discrete_sequence=PALETA,
        )
        st.plotly_chart(vangogh(fig4), use_container_width=True, key="grafico4")

    with col4:
        st.subheader("ROI por local")
        g5 = (
            df.groupby("location", as_index=False)["roi"].mean()
            .sort_values("roi", ascending=False)
        )
        fig5 = px.bar(
            g5, x="location", y="roi", text_auto=".2f",
            labels={"location": "Local", "roi": "ROI médio"},
            color_discrete_sequence=[TEAL],
        )
        st.plotly_chart(vangogh(fig5), use_container_width=True, key="grafico5")

# ============================ ABA 2 — POR DIMENSÃO ============================
with tab2:
    st.caption("Corte livre: escolha a dimensão e a métrica — é o espelho das perguntas dos níveis 2 e 3.")
    colA, colB = st.columns(2)
    with colA:
        dimensao = st.selectbox(
            "Dimensão",
            ["Canal", "Empresa", "Tipo de campanha", "Público", "Segmento", "Local"],
        )
    with colB:
        metrica = st.selectbox("Métrica", ["ROI médio", "CTR", "Investimento", "Cliques", "Impressões"])

    col_dim = {
        "Canal": "channel_name",
        "Empresa": "company_name",
        "Tipo de campanha": "campaign_type",
        "Público": "target_audience",
        "Segmento": "customer_segment",
        "Local": "location",
    }[dimensao]

    if metrica == "CTR":
        g = (
            df.groupby(col_dim, as_index=False)
            .agg(impr=("impressions", "sum"), cli=("clicks", "sum"))
        )
        g["valor"] = g["cli"] / g["impr"]
        fmt = ".2%"
    else:
        agg_map = {
            "ROI médio": ("roi", "mean", ".2f"),
            "Investimento": ("acquisition_cost", "sum", ",.0f"),
            "Cliques": ("clicks", "sum", ",.0f"),
            "Impressões": ("impressions", "sum", ",.0f"),
        }
        col, agg, fmt = agg_map[metrica]
        g = df.groupby(col_dim, as_index=False).agg(valor=(col, agg))

    g = g.sort_values("valor", ascending=False)
    fig6 = px.bar(
        g, x=col_dim, y="valor", text_auto=fmt,
        labels={col_dim: dimensao, "valor": metrica},
        color_discrete_sequence=[GOLD],
    )
    st.plotly_chart(vangogh(fig6), use_container_width=True, key="grafico6")

    with st.expander("Ver tabela do corte"):
        st.dataframe(g, use_container_width=True)

# ============================ ABA 3 — TENDÊNCIAS ============================
with tab3:
    st.subheader("Evolução mensal (ROI médio)")
    g3 = df.groupby("mes", as_index=False).agg(roi=("roi", "mean"), n=("id_campaign", "count"))
    fig3 = px.line(
        g3, x="mes", y="roi", markers=True,
        labels={"mes": "Mês", "roi": "ROI médio"},
        color_discrete_sequence=[GOLD],
    )
    st.plotly_chart(vangogh(fig3), use_container_width=True, key="grafico3")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cliques por mês")
        g7 = df.groupby("mes", as_index=False)["clicks"].sum()
        fig7 = px.area(
            g7, x="mes", y="clicks",
            labels={"mes": "Mês", "clicks": "Cliques"},
            color_discrete_sequence=[AZUL],
        )
        st.plotly_chart(vangogh(fig7), use_container_width=True, key="grafico7")

    with col2:
        st.subheader("Engajamento médio por mês")
        g8 = df.groupby("mes", as_index=False)["engagement_score"].mean()
        fig8 = px.line(
            g8, x="mes", y="engagement_score", markers=True,
            labels={"mes": "Mês", "engagement_score": "Engajamento médio"},
            color_discrete_sequence=[TEAL],
        )
        st.plotly_chart(vangogh(fig8), use_container_width=True, key="grafico8")

    st.subheader("Investimento × ROI por mês")
    g9 = df.groupby("mes", as_index=False).agg(
        investimento=("acquisition_cost", "sum"), roi=("roi", "mean")
    )
    fig9 = go.Figure()
    fig9.add_bar(x=g9["mes"], y=g9["investimento"], name="Investimento (US$)", marker_color=AZUL, opacity=0.7)
    fig9.add_scatter(
        x=g9["mes"], y=g9["roi"], name="ROI médio", yaxis="y2",
        line=dict(color=GOLD, width=3),
    )
    fig9.update_layout(
        yaxis=dict(title="Investimento (US$)"),
        yaxis2=dict(title="ROI médio", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(vangogh(fig9), use_container_width=True, key="grafico9")

# ============================ ABA 4 — DRILL-DOWN ============================
with tab4:
    st.subheader("🔍 Drill-down — investigar um recorte")
    st.caption("Vá afunilando: empresa → canal → tipo. Os KPIs e o top 15 acompanham o recorte.")

    pool = df
    op_empresa = st.selectbox("Empresa", ["Todas"] + sorted(pool["company_name"].dropna().unique()))
    if op_empresa != "Todas":
        pool = pool[pool["company_name"] == op_empresa]

    op_canal = st.selectbox("Canal", ["Todos"] + sorted(pool["channel_name"].dropna().unique()))
    if op_canal != "Todos":
        pool = pool[pool["channel_name"] == op_canal]

    op_tipo = st.selectbox("Tipo de campanha", ["Todos"] + sorted(pool["campaign_type"].dropna().unique()))
    if op_tipo != "Todos":
        pool = pool[pool["campaign_type"] == op_tipo]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Campanhas no recorte", f"{len(pool):,}")
    m2.metric("ROI médio", f"{pool['roi'].mean():.2f}" if len(pool) else "—")
    m3.metric(
        "CTR",
        f"{(pool['clicks'].sum() / pool['impressions'].sum()):.2%}" if pool["impressions"].sum() else "—",
    )
    m4.metric("Investimento", f"US$ {pool['acquisition_cost'].sum():,.0f}")

    top = (
        pool.sort_values("roi", ascending=False)
        .head(15)[["date", "company_name", "channel_name", "campaign_type", "location", "roi", "ctr", "acquisition_cost"]]
        .rename(columns={
            "date": "data", "company_name": "empresa", "channel_name": "canal",
            "campaign_type": "tipo", "location": "local", "roi": "ROI",
            "ctr": "CTR", "acquisition_cost": "custo de aquisição",
        })
    )
    top["data"] = top["data"].dt.strftime("%d/%m/%Y")
    st.dataframe(
        top.style.format({
            "ROI": "{:.2f}",
            "CTR": "{:.2%}",
            "custo de aquisição": "US$ {:,.0f}",
        }),
        use_container_width=True,
    )

# ------------------------------------------------------------------
# Tabela de detalhe
# ------------------------------------------------------------------
st.subheader("Detalhe por empresa e canal")
g10 = (
    df.groupby(["company_name", "channel_name"], as_index=False)
    .agg(
        campanhas=("id_campaign", "count"),
        investimento=("acquisition_cost", "sum"),
        roi_medio=("roi", "mean"),
        cliques=("clicks", "sum"),
        impressoes=("impressions", "sum"),
    )
)
g10["ctr"] = g10["cliques"] / g10["impressoes"]
st.dataframe(
    g10.style.format(
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