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
# CSS
# =========================================================
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Fundo fixo atrás de tudo via pseudo-elemento */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/assets/fundo.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        z-index: 0;
    }

    .stApp > * {
        position: relative;
        z-index: 1;
    }

    section[data-testid="stSidebar"] {
        background-color: rgba(57, 91, 94, 0.90) !important;
        position: relative;
        z-index: 10;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Título sem container — flutua diretamente sobre a imagem de fundo */
    .titulo-dashboard {
        color: white;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 12px rgba(0,0,0,0.95), 0 0 30px rgba(0,0,0,0.7);
        margin-top: 0;
        padding-top: 10px;
        background: none !important;
    }

    /* KPIs — fundo aplicado SOMENTE no bloco que contém métricas (não no header) */
    div[data-testid="stHorizontalBlock"]:has([data-testid="metric-container"]) {
        background-color: rgba(49, 81, 82, 0.85);
        padding: 25px 20px;
        border-radius: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* Cards individuais de métrica: fundo translúcido, fonte BRANCA */
    [data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px;
        padding: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.20);
    }

    /* Rótulo da métrica — seletores máximos para sobrescrever o tema Streamlit */
    [data-testid="metric-container"] [data-testid="stMetricLabel"],
    [data-testid="metric-container"] [data-testid="stMetricLabel"] *,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] p,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] span,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] div,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] label {
        color: #ffffff !important;
        opacity: 1 !important;
        visibility: visible !important;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.8);
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    /* Valor principal da métrica — branco com sombra */
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] * {
        color: #ffffff !important;
        opacity: 1 !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 6px rgba(0,0,0,0.6);
    }

    /* Gráficos diretos sobre o fundo — sem container extra,
       fundo branco semi-opaco e borda arredondada no próprio chart */
    div[data-testid="stPlotlyChart"] {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        margin-top: 15px;
        margin-bottom: 10px;
    }

    /* Insight box */
    .insight-container {
        background-color: rgba(49, 81, 82, 0.88);
        border-left: 8px solid #6499B9;
        padding: 20px;
        border-radius: 20px;
        color: white;
        font-size: 16px;
        margin-top: 15px;
        margin-bottom: 10px;
        line-height: 1.6;
        backdrop-filter: blur(6px);
    }

    /* Rodapé */
    .rodape {
        background-color: rgba(57, 91, 94, 0.90);
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-top: 40px;
        font-size: 14px;
    }

    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0.0) !important;
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
# HEADER — título flutua livre sobre a imagem, sem container
# =========================================================
col1, col2, col3 = st.columns([1, 8, 1])
with col1:
    st.image(
        "https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/assets/icone.png",
        width=90
    )
with col2:
    st.markdown("""
    <div class="titulo-dashboard">
    Dashboard Sistema Comercial de Água e Esgoto
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

    # O CSS :has(metric-container) aplica o fundo verde apenas neste bloco
    c1, c2, c3, c4, c5 = st.columns(5, gap="small")
    with c1:
        st.metric("Receita Acumulada", f"R$ {receita_acumulada:,.2f}")
    with c2:
        st.metric("Perda Estimada", f"R$ {perda_estimada:,.2f}")
    with c3:
        st.metric("Ligações Suspeitas", f"{ligacoes_suspeitas}")
    with c4:
        st.metric("Hidrômetros Críticos", f"{hidrometros_criticos}")
    with c5:
        st.metric("Receita Potencial", f"R$ {receita_potencial:,.2f}")

    st.markdown("""
    <div class="insight-container">
    Visão Geral de KPIs estratégicos visando identificação de oportunidades de recuperação de receitas
    e detecção de fraudes e inconsistências.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PERDAS COMERCIAIS
# =========================================================
elif pagina == "💰 Perdas Comerciais":
    fig = px.histogram(
        df, x='RECEITA_ACUMULADA', nbins=50,
        title='Distribuição da Receita Acumulada',
        template='plotly_white'
    )
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0.93)',
        plot_bgcolor='rgba(255,255,255,0.93)',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-container">
    Os dados indicam crescimento progressivo da perda estimada em hidrômetros
    próximos ou acima da vida útil recomendada.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ANOMALIAS
# =========================================================
elif pagina == "🚨 Anomalias":
    fig = px.scatter(
        df, x='CONSUMO_ACUMULADO', y='RECEITA_ACUMULADA',
        color='FLAG_SUSPEITA',
        title='Detecção de Comportamentos Atípicos',
        template='plotly_white',
        color_discrete_map={'SUSPEITO': '#e74c3c', 'NORMAL': '#2ecc71'}
    )
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0.93)',
        plot_bgcolor='rgba(255,255,255,0.93)',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-container">
    Ligações com comportamento atípico e potencial necessidade de análise comercial.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PARQUE DE HIDRÔMETROS
# =========================================================
elif pagina == "💧 Parque de Hidrômetros":
    status_hidrometro = df['STATUS_HIDROMETRO'].value_counts().reset_index()
    status_hidrometro.columns = ['STATUS', 'QUANTIDADE']
    fig = px.bar(
        status_hidrometro, x='STATUS', y='QUANTIDADE',
        color='STATUS', text='QUANTIDADE',
        title='Situação Operacional dos Hidrômetros',
        template='plotly_white',
        color_discrete_map={
            'DENTRO DA VIDA UTIL': '#2ecc71',
            'PROXIMO DO VENCIMENTO': '#f1c40f',
            'SUBSTITUICAO RECOMENDADA': '#e74c3c'
        }
    )
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0.93)',
        plot_bgcolor='rgba(255,255,255,0.93)',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-container">
    Foi identificado percentual relevante de hidrômetros acima da vida útil recomendada
    pela Portaria 155/2022.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# RECOMENDAÇÕES
# =========================================================
elif pagina == "📈 Recomendações":
    dados_linha = df.groupby(
        ['IDADE_HIDROMETRO', 'STATUS_HIDROMETRO']
    )['PERDA_ESTIMADA'].sum().reset_index()

    fig = px.line(
        dados_linha, x='IDADE_HIDROMETRO', y='PERDA_ESTIMADA',
        color='STATUS_HIDROMETRO', markers=True,
        template='plotly_white',
        title='Perdas Comerciais Associadas ao Envelhecimento dos Hidrômetros',
        color_discrete_map={
            'DENTRO DA VIDA UTIL': '#2ecc71',
            'PROXIMO DO VENCIMENTO': '#f1c40f',
            'SUBSTITUICAO RECOMENDADA': '#e74c3c'
        }
    )
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0.93)',
        plot_bgcolor='rgba(255,255,255,0.93)',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-container">
    Com base nas análises realizadas, foram identificadas oportunidades relevantes de recuperação de receita
    associadas principalmente ao envelhecimento do parque de hidrômetros, inconsistências entre consumo e
    faturamento e padrões atípicos de comportamento comercial. Os dados indicam que hidrômetros com idade
    superior à vida útil recomendada apresentam maior potencial de submedição e perdas financeiras,
    reforçando a necessidade de substituição preventiva e priorização operacional. Também foram identificadas
    ligações com elevado consumo acumulado e baixo ticket médio por metro cúbico, sinalizando possíveis
    inconsistências cadastrais, falhas de medição ou necessidade de inspeção comercial.<br><br>
    Recomenda-se como ações prioritárias a substituição gradual dos hidrômetros críticos, a intensificação
    das fiscalizações em ligações classificadas como suspeitas e a implementação de monitoramento contínuo
    dos indicadores estratégicos apresentados no dashboard. As medidas propostas possuem potencial de
    aumento de faturamento, mitigação de perdas comerciais e melhoria da eficiência operacional,
    contribuindo diretamente para a sustentabilidade financeira da operação de saneamento.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# RODAPÉ
# =========================================================
st.markdown("""
<div class="rodape">
@ Elisângela de Souza | Sistema Comercial de Água e Esgoto | 2026
</div>
""", unsafe_allow_html=True)
