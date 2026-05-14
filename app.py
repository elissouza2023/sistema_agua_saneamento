import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Sistema Comercial de Água e Esgoto",
    layout="wide",
    page_icon="💧"
)

# =========================================================
# CSS REFORMULADO (Estilo Siderurgia Aplicado)
# =========================================================
st.markdown("""
<style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/assets/fundo.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }

    /* Camada de escurecimento sobre o fundo */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.40);
        z-index: -1;
    }

    /* Sidebar com Blur */
    section[data-testid="stSidebar"] {
        background-color: rgba(57, 91, 94, 0.70) !important;
        backdrop-filter: blur(10px);
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .titulo-dashboard {
        color: white;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.9);
        padding: 20px 0;
    }

    /* Container de Vidro para KPIs e Gráficos */
    .glass-container {
        background-color: rgba(49, 81, 82, 0.75) !important;
        padding: 25px;
        border-radius: 20px;
        margin: 15px 0;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Ajuste para que as métricas fiquem transparentes sobre o vidro */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px;
        padding: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stMetricLabel"] p {
        color: #6499B9 !important;
        font-weight: bold !important;
    }

    .insight-container {
        background-color: rgba(49, 81, 82, 0.85);
        border-left: 8px solid #6499B9;
        padding: 20px;
        border-radius: 15px;
        color: white;
        font-size: 16px;
    }

    .rodape {
        background-color: rgba(57, 91, 94, 0.8);
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-top: 40px;
    }

    /* Reset de cores para legibilidade */
    h1, h2, h3, p, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÃO PARA TRANSPARÊNCIA DO PLOTLY
# =========================================================
def apply_plotly_style(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.1)")
    fig.update_yaxis(gridcolor="rgba(255,255,255,0.1)")
    return fig

# =========================================================
# CARREGAMENTO DOS DADOS
# =========================================================
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/data/dados_micromedicao.xls"
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip().str.upper().str.replace(' ', '_').str.replace('.', '').str.replace('/', '_').str.replace('Ç', 'C').str.replace('Ã', 'A').str.replace('Á', 'A')
    df = df[df['SIT_LIG_AGUA'].notna()]
    colunas_numericas = df.select_dtypes(include=['float64', 'int64']).columns
    df[colunas_numericas] = df[colunas_numericas].fillna(0)
    df['CATEGORIA_PRINCIPAL'] = df['CATEGORIA_PRINCIPAL'].fillna('NAO INFORMADO')
    df['DATA_INSTALACAO_HIDROMETRO'] = pd.to_datetime(df['DATA_INSTALACAO_HIDROMETRO'], errors='coerce')
    colunas_consumo = [col for col in df.columns if 'VOLUME_FATURADO_' in col]
    colunas_receita = [col for col in df.columns if 'VALOR_TOTAL_' in col]
    df['CONSUMO_ACUMULADO'] = df[colunas_consumo].sum(axis=1)
    df['RECEITA_ACUMULADA'] = df[colunas_receita].sum(axis=1)
    df['IDADE_HIDROMETRO'] = (pd.Timestamp.today().year - df['DATA_INSTALACAO_HIDROMETRO'].dt.year)
    tarifa_media = df['RECEITA_ACUMULADA'].sum() / df['CONSUMO_ACUMULADO'].sum()
    df['RECEITA_POTENCIAL'] = df['CONSUMO_ACUMULADO'] * tarifa_media
    df['PERDA_ESTIMADA'] = df['RECEITA_POTENCIAL'] - df['RECEITA_ACUMULADA']
    df['TICKET_MEDIO_M3'] = np.where(df['CONSUMO_ACUMULADO'] > 0, df['RECEITA_ACUMULADA'] / df['CONSUMO_ACUMULADO'], 0)
    df['FLAG_SUSPEITA'] = np.where((df['CONSUMO_ACUMULADO'] > df['CONSUMO_ACUMULADO'].quantile(0.75)) & (df['TICKET_MEDIO_M3'] < df['TICKET_MEDIO_M3'].quantile(0.25)), 'SUSPEITO', 'NORMAL')
    df['STATUS_HIDROMETRO'] = np.where(df['IDADE_HIDROMETRO'] < 5, 'DENTRO DA VIDA UTIL', np.where(df['IDADE_HIDROMETRO'] < 7, 'PROXIMO DO VENCIMENTO', 'SUBSTITUICAO RECOMENDADA'))
    return df

df = carregar_dados()

# =========================================================
# SIDEBAR & HEADER
# =========================================================
st.sidebar.markdown("## Menu")
pagina = st.sidebar.radio("", ["🏠 Visão Geral", "💰 Perdas Comerciais", "🚨 Anomalias", "💧 Parque de Hidrômetros", "📈 Recomendações"])

st.markdown('<div class="titulo-dashboard">Dashboard Sistema Comercial de Água e Esgoto</div>', unsafe_allow_html=True)

# =========================================================
# LÓGICA DE PÁGINAS COM CONTAINERS DE VIDRO
# =========================================================
if pagina == "🏠 Visão Geral":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Receita Acumulada", f"R$ {df['RECEITA_ACUMULADA'].sum():,.2f}")
    c2.metric("Perda Estimada", f"R$ {df['PERDA_ESTIMADA'].clip(lower=0).sum():,.2f}")
    c3.metric("Ligações Suspeitas", f"{(df['FLAG_SUSPEITA'] == 'SUSPEITO').sum()}")
    c4.metric("Hidrômetros Críticos", f"{(df['STATUS_HIDROMETRO'] == 'SUBSTITUICAO RECOMENDADA').sum()}")
    c5.metric("Receita Potencial", f"R$ {df['RECEITA_POTENCIAL'].sum():,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="insight-container">Visão Geral de KPIs estratégicos visando identificação de oportunidades de recuperação de receitas.</div>', unsafe_allow_html=True)

elif pagina == "💰 Perdas Comerciais":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    fig = px.histogram(df, x='RECEITA_ACUMULADA', nbins=50, title='Distribuição da Receita', color_discrete_sequence=['#6499B9'])
    st.plotly_chart(apply_plotly_style(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif pagina == "🚨 Anomalias":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    fig = px.scatter(df, x='CONSUMO_ACUMULADO', y='RECEITA_ACUMULADA', color='FLAG_SUSPEITA', title='Detecção de Comportamentos Atípicos')
    st.plotly_chart(apply_plotly_style(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif pagina == "💧 Parque de Hidrômetros":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    status_hidrometro = df['STATUS_HIDROMETRO'].value_counts().reset_index()
    fig = px.bar(status_hidrometro, x='STATUS_HIDROMETRO', y='count', color='STATUS_HIDROMETRO', title='Situação dos Hidrômetros')
    st.plotly_chart(apply_plotly_style(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif pagina == "📈 Recomendações":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    dados_linha = df.groupby(['IDADE_HIDROMETRO', 'STATUS_HIDROMETRO'])['PERDA_ESTIMADA'].sum().reset_index()
    fig = px.line(dados_linha, x='IDADE_HIDROMETRO', y='PERDA_ESTIMADA', color='STATUS_HIDROMETRO', markers=True)
    st.plotly_chart(apply_plotly_style(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RODAPÉ
# =========================================================
st.markdown('<div class="rodape">@ Elisângela de Souza | Sistema Comercial de Água e Esgoto | 2026</div>', unsafe_allow_html=True)
