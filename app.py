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
# CSS CORRIGIDO - FOCO NO EFEITO DE VIDRO
# =========================================================
st.markdown("""
<style>
    /* Ajuste do container principal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Imagem de fundo */
    .stApp {
        background-image: url("https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/assets/fundo.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }

    /* Sidebar customizada */
    section[data-testid="stSidebar"] {
        background-color: rgba(57, 91, 94, 0.95) !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Título do Dashboard */
    .titulo-dashboard {
        color: white;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.9);
        margin-bottom: 30px;
    }

    /* ESTILIZAÇÃO DOS CONTAINERS NATIVOS (O SEGREDO DA CORREÇÃO) */
    /* Isso aplica o fundo diretamente nos elementos do Streamlit */
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="element-container"] .stMarkdown div[class*="kpi-card"],
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* Estilo para os containers de gráficos e KPIs */
    .glass-container {
        background-color: rgba(49, 81, 82, 0.85);
        padding: 25px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }

    .insight-container {
        background-color: rgba(49, 81, 82, 0.92);
        border-left: 8px solid #6499B9;
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-top: 15px;
    }

    .rodape {
        background-color: rgba(57, 91, 94, 0.9);
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-top: 40px;
    }
    
    /* Remove o header branco padrão do Streamlit */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CARREGAMENTO DOS DADOS
# =========================================================
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/data/dados_micromedicao.xls"
    df = pd.read_excel(url)
    
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(' ', '_')
        .str.replace('.', '')
        .str.replace('/', '_')
        .str.replace('Ç', 'C')
        .str.replace('Ã', 'A')
        .str.replace('Á', 'A')
    )
    
    df = df[df['SIT_LIG_AGUA'].notna()]
    colunas_numericas = df.select_dtypes(include=['float64', 'int64']).columns
    df[colunas_numericas] = df[colunas_numericas].fillna(0)
    df['CATEGORIA_PRINCIPAL'] = df['CATEGORIA_PRINCIPAL'].fillna('NAO INFORMADO')
    
    df['DATA_INSTALACAO_HIDROMETRO'] = pd.to_datetime(
        df['DATA_INSTALACAO_HIDROMETRO'], errors='coerce'
    )
    
    colunas_consumo = [col for col in df.columns if 'VOLUME_FATURADO_' in col]
    colunas_receita = [col for col in df.columns if 'VALOR_TOTAL_' in col]
    
    df['CONSUMO_ACUMULADO'] = df[colunas_consumo].sum(axis=1)
    df['RECEITA_ACUMULADA'] = df[colunas_receita].sum(axis=1)
    df['CONSUMO_MEDIO'] = df[colunas_consumo].mean(axis=1)
    df['RECEITA_MEDIA'] = df[colunas_receita].mean(axis=1)
    
    df['IDADE_HIDROMETRO'] = (
        pd.Timestamp.today().year - df['DATA_INSTALACAO_HIDROMETRO'].dt.year
    )
    
    df['TICKET_MEDIO_M3'] = np.where(
        df['CONSUMO_ACUMULADO'] > 0,
        df['RECEITA_ACUMULADA'] / df['CONSUMO_ACUMULADO'],
        0
    )
    
    tarifa_media = df['RECEITA_ACUMULADA'].sum() / df['CONSUMO_ACUMULADO'].sum()
    
    df['RECEITA_POTENCIAL'] = df['CONSUMO_ACUMULADO'] * tarifa_media
    df['PERDA_ESTIMADA'] = df['RECEITA_POTENCIAL'] - df['RECEITA_ACUMULADA']
    
    df['FLAG_SUSPEITA'] = np.where(
        (df['CONSUMO_ACUMULADO'] > df['CONSUMO_ACUMULADO'].quantile(0.75)) &
        (df['TICKET_MEDIO_M3'] < df['TICKET_MEDIO_M3'].quantile(0.25)),
        'SUSPEITO', 'NORMAL'
    )
    
    df['STATUS_HIDROMETRO'] = np.where(
        df['IDADE_HIDROMETRO'] < 5, 'DENTRO DA VIDA UTIL',
        np.where(df['IDADE_HIDROMETRO'] < 7, 'PROXIMO DO VENCIMENTO', 'SUBSTITUICAO RECOMENDADA')
    )
    
    return df

df = carregar_dados()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## Menu")
pagina = st.sidebar.radio(
    "",
    [
        "🏠 Visão Geral",
        "💰 Perdas Comerciais",
        "🚨 Anomalias",
        "💧 Parque de Hidrômetros",
        "📈 Recomendações"
    ]
)

# =========================================================
# HEADER
# =========================================================
st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
        <img src="https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/assets/icone.png" width="80">
        <h1 class="titulo-dashboard">Dashboard Sistema Comercial de Água e Esgoto</h1>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# VISÃO GERAL
# =========================================================
if pagina == "🏠 Visão Geral":
    receita_acumulada = df['RECEITA_ACUMULADA'].sum()
    perda_estimada = df['PERDA_ESTIMADA'].clip(lower=0).sum()
    ligacoes_suspeitas = (df['FLAG_SUSPEITA'] == 'SUSPEITO').sum()
    hidrometros_criticos = (df['STATUS_HIDROMETRO'] == 'SUBSTITUICAO RECOMENDADA').sum()
    receita_potencial = df['RECEITA_POTENCIAL'].sum()

    # Container de Vidro para KPIs
    with st.container():
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Receita Acumulada", f"R$ {receita_acumulada:,.2f}")
        c2.metric("Perda Estimada", f"R$ {perda_estimada:,.2f}")
        c3.metric("Ligações Suspeitas", f"{ligacoes_suspeitas}")
        c4.metric("Hidrômetros Críticos", f"{hidrometros_criticos}")
        c5.metric("Receita Potencial", f"R$ {receita_potencial:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-container">
    Visão Geral de KPIs estratégicos visando identificação de oportunidades de recuperação de receitas e detecção de fraudes e inconsistências.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# OUTRAS PÁGINAS
# =========================================================
elif pagina == "💰 Perdas Comerciais":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    fig = px.histogram(df, x='RECEITA_ACUMULADA', nbins=50, title='Distribuição da Receita Acumulada', template='plotly_dark')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-container">Os dados indicam crescimento progressivo da perda estimada em hidrômetros próximos ou acima da vida útil recomendada.</div>', unsafe_allow_html=True)

elif pagina == "🚨 Anomalias":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    fig = px.scatter(df, x='CONSUMO_ACUMULADO', y='RECEITA_ACUMULADA', color='FLAG_SUSPEITA',
                     title='Detecção de Comportamentos Atípicos', template='plotly_dark')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif pagina == "💧 Parque de Hidrômetros":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    status_hidrometro = df['STATUS_HIDROMETRO'].value_counts().reset_index()
    status_hidrometro.columns = ['STATUS', 'QUANTIDADE']
    fig = px.bar(status_hidrometro, x='STATUS', y='QUANTIDADE', color='STATUS', text='QUANTIDADE',
                 title='Situação Operacional dos Hidrômetros', template='plotly_dark',
                 color_discrete_map={'DENTRO DA VIDA UTIL': 'green','PROXIMO DO VENCIMENTO': 'yellow','SUBSTITUICAO RECOMENDADA': 'red'})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif pagina == "📈 Recomendações":
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    dados_linha = df.groupby(['IDADE_HIDROMETRO', 'STATUS_HIDROMETRO'])['PERDA_ESTIMADA'].sum().reset_index()
    fig = px.line(dados_linha, x='IDADE_HIDROMETRO', y='PERDA_ESTIMADA', color='STATUS_HIDROMETRO',
                  markers=True, template='plotly_dark',
                  title='Perdas Comerciais Associadas ao Envelhecimento dos Hidrômetros',
                  color_discrete_map={'DENTRO DA VIDA UTIL': 'green','PROXIMO DO VENCIMENTO': 'yellow','SUBSTITUICAO RECOMENDADA': 'red'})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RODAPÉ
# =========================================================
st.markdown("""
<div class="rodape">
@ Elisângela de Souza | Sistema Comercial de Água e Esgoto | 2026
</div>
""", unsafe_allow_html=True)
