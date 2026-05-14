import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Sistema Comercial de Água e Esgoto",
    layout="wide"
)

# =========================================================
# ESTILO CSS
# =========================================================

st.markdown(
    f"""
    <style>
[data-testid="metric-container"] {
    background-color: rgba(255,255,255,0.92);
    border-radius: 18px;
    padding: 15px;
}
    .stApp {{
        background-image: url("https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/assets/fundo.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(57, 91, 94, 0.60);
    }}

    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}

    .titulo-dashboard {{
        color: white;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin-top: -20px;
    }}

    .grafico-container {{
        background-color: rgba(49, 81, 82, 0.78);
        padding: 35px;
        border-radius: 35px;
        margin-top: 20px;
        backdrop-filter: blur(6px);

    }}

    .insight-container {{
        background-color: rgba(49, 81, 82, 0.78);
        border-left: 8px solid #6499B9;
        padding: 20px;
        border-radius: 20px;
        color: white;
        font-size: 16px;
        margin-top: 25px;
    }}

    .rodape {{
        background-color: #395B5E;
        color: #FFFFFF;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-top: 30px;
        font-size: 14px;
    }}

    .kpi-box {{
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }}

    .kpi-title {{
        font-size: 18px;
        color: #395B5E;
        font-weight: bold;
    }}

    .kpi-value {{
        font-size: 30px;
        color: #2E4F50;
        font-weight: bold;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# CARREGAMENTO DOS DADOS
# =========================================================

@st.cache_data
def carregar_dados():

    url = "https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/data/dados_micromedicao.xls"

    df = pd.read_excel(url)

    # PADRONIZAÇÃO
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

    # LIMPEZA
    df = df[df['SIT_LIG_AGUA'].notna()]

    colunas_numericas = df.select_dtypes(
        include=['float64', 'int64']
    ).columns

    df[colunas_numericas] = (
        df[colunas_numericas]
        .fillna(0)
    )

    df['CATEGORIA_PRINCIPAL'] = (
        df['CATEGORIA_PRINCIPAL']
        .fillna('NAO INFORMADO')
    )

    df['DATA_INSTALACAO_HIDROMETRO'] = pd.to_datetime(
        df['DATA_INSTALACAO_HIDROMETRO'],
        errors='coerce'
    )

    # ENGENHARIA DE ATRIBUTOS

    colunas_consumo = [
        col for col in df.columns
        if 'VOLUME_FATURADO_' in col
    ]

    colunas_receita = [
        col for col in df.columns
        if 'VALOR_TOTAL_' in col
    ]

    df['CONSUMO_ACUMULADO'] = (
        df[colunas_consumo]
        .sum(axis=1)
    )

    df['RECEITA_ACUMULADA'] = (
        df[colunas_receita]
        .sum(axis=1)
    )

    df['CONSUMO_MEDIO'] = (
        df[colunas_consumo]
        .mean(axis=1)
    )

    df['RECEITA_MEDIA'] = (
        df[colunas_receita]
        .mean(axis=1)
    )

    df['IDADE_HIDROMETRO'] = (
        pd.Timestamp.today().year -
        df['DATA_INSTALACAO_HIDROMETRO'].dt.year
    )

    # TICKET MEDIO

    df['TICKET_MEDIO_M3'] = np.where(
        df['CONSUMO_ACUMULADO'] > 0,
        df['RECEITA_ACUMULADA'] /
        df['CONSUMO_ACUMULADO'],
        0
    )

    # TARIFA MEDIA

    tarifa_media = (
        df['RECEITA_ACUMULADA'].sum() /
        df['CONSUMO_ACUMULADO'].sum()
    )

    # RECEITA POTENCIAL

    df['RECEITA_POTENCIAL'] = (
        df['CONSUMO_ACUMULADO'] *
        tarifa_media
    )

    # PERDA ESTIMADA

    df['PERDA_ESTIMADA'] = (
        df['RECEITA_POTENCIAL'] -
        df['RECEITA_ACUMULADA']
    )

    # FLAG SUSPEITA

    df['FLAG_SUSPEITA'] = np.where(
        (
            df['CONSUMO_ACUMULADO'] >
            df['CONSUMO_ACUMULADO'].quantile(0.75)
        ) &
        (
            df['TICKET_MEDIO_M3'] <
            df['TICKET_MEDIO_M3'].quantile(0.25)
        ),
        'SUSPEITO',
        'NORMAL'
    )

    # STATUS HIDROMETRO

    df['STATUS_HIDROMETRO'] = np.where(
        df['IDADE_HIDROMETRO'] < 5,
        'DENTRO DA VIDA UTIL',
        np.where(
            df['IDADE_HIDROMETRO'] < 7,
            'PROXIMO DO VENCIMENTO',
            'SUBSTITUICAO RECOMENDADA'
        )
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

col1, col2 = st.columns([1, 10])

with col1:
    st.image(
        "https://raw.githubusercontent.com/elissouza2023/sistema_agua_saneamento/main/assets/icone.png",
        width=80
    )

with col2:
    st.markdown(
        """
        <div class="titulo-dashboard">
        Dashboard Sistema Comercial de Água e Esgoto
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# VISÃO GERAL
# =========================================================

if pagina == "🏠 Visão Geral":

    with st.container():

    st.markdown(
        """
        <div class="grafico-container">
        """,
        unsafe_allow_html=True
    )

    receita_acumulada = df['RECEITA_ACUMULADA'].sum()

    perda_estimada = (
        df['PERDA_ESTIMADA']
        .clip(lower=0)
        .sum()
    )

    ligacoes_suspeitas = (
        df['FLAG_SUSPEITA'] == 'SUSPEITO'
    ).sum()

    hidrometros_criticos = (
        df['STATUS_HIDROMETRO'] ==
        'SUBSTITUICAO RECOMENDADA'
    ).sum()

    receita_potencial = (
        df['RECEITA_POTENCIAL']
        .sum()
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Receita Acumulada",
            f"R$ {receita_acumulada:,.2f}"
        )

    with c2:
        st.metric(
            "Perda Estimada",
            f"R$ {perda_estimada:,.2f}"
        )

    with c3:
        st.metric(
            "Ligações Suspeitas",
            f"{ligacoes_suspeitas}"
        )

    with c4:
        st.metric(
            "Hidrômetros Críticos",
            f"{hidrometros_criticos}"
        )

    with c5:
        st.metric(
            "Receita Potencial",
            f"R$ {receita_potencial:,.2f}"
        )

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="insight-container">
        Visão Geral de KPIs estratégicos visando identificação de oportunidades de recuperação de receitas e detecção de fraudes e inconsistências.
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PERDAS COMERCIAIS
# =========================================================

elif pagina == "💰 Perdas Comerciais":

    st.markdown('<div class="grafico-container">', unsafe_allow_html=True)

    fig = px.histogram(
        df,
        x='RECEITA_ACUMULADA',
        nbins=50,
        title='Distribuição da Receita Acumulada',
        template='plotly_white'
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="insight-container">
        Os dados indicam crescimento progressivo da perda estimada em hidrômetros próximos ou acima da vida útil recomendada, sugerindo que a substituição preventiva possui potencial de retorno financeiro superior ao custo operacional da troca.
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# ANOMALIAS
# =========================================================

elif pagina == "🚨 Anomalias":

    st.markdown('<div class="grafico-container">', unsafe_allow_html=True)

    fig = px.scatter(
        df,
        x='CONSUMO_ACUMULADO',
        y='RECEITA_ACUMULADA',
        color='FLAG_SUSPEITA',
        template='plotly_white',
        title='Detecção de Comportamentos Atípicos'
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="insight-container">
        Ligações com comportamento atípico e potencial necessidade de análise comercial.
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PARQUE HIDROMETROS
# =========================================================

elif pagina == "💧 Parque de Hidrômetros":

    st.markdown('<div class="grafico-container">', unsafe_allow_html=True)

    status_hidrometro = (
        df['STATUS_HIDROMETRO']
        .value_counts()
        .reset_index()
    )

    status_hidrometro.columns = [
        'STATUS',
        'QUANTIDADE'
    ]

    fig = px.bar(
        status_hidrometro,
        x='STATUS',
        y='QUANTIDADE',
        color='STATUS',
        text='QUANTIDADE',
        title='Situação Operacional dos Hidrômetros',
        template='plotly_white',
        color_discrete_map={
            'DENTRO DA VIDA UTIL': 'green',
            'PROXIMO DO VENCIMENTO': 'yellow',
            'SUBSTITUICAO RECOMENDADA': 'red'
        }
    )

    fig.update_traces(
        textposition='outside'
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="insight-container">
        Foi identificado percentual relevante de hidrômetros acima da vida útil recomendada pela Portaria 155/2022, indicando potencial risco de submedição e perdas comerciais.
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# RECOMENDACOES
# =========================================================

elif pagina == "📈 Recomendações":

    st.markdown('<div class="grafico-container">', unsafe_allow_html=True)

    dados_linha = (
        df.groupby(
            ['IDADE_HIDROMETRO', 'STATUS_HIDROMETRO']
        )['PERDA_ESTIMADA']
        .sum()
        .reset_index()
    )

    fig = px.line(
        dados_linha,
        x='IDADE_HIDROMETRO',
        y='PERDA_ESTIMADA',
        color='STATUS_HIDROMETRO',
        markers=True,
        title='Perdas Comerciais Associadas ao Envelhecimento dos Hidrômetros',
        template='plotly_white',
        color_discrete_map={
            'DENTRO DA VIDA UTIL': 'green',
            'PROXIMO DO VENCIMENTO': 'yellow',
            'SUBSTITUICAO RECOMENDADA': 'red'
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="insight-container">
        Com base nas análises realizadas, foram identificadas oportunidades relevantes de recuperação de receita associadas principalmente ao envelhecimento do parque de hidrômetros, inconsistências entre consumo e faturamento e padrões atípicos de comportamento comercial. Os dados indicam que hidrômetros com idade superior à vida útil recomendada apresentam maior potencial de submedição e perdas financeiras, reforçando a necessidade de substituição preventiva e priorização operacional. Também foram identificadas ligações com elevado consumo acumulado e baixo ticket médio por metro cúbico, sinalizando possíveis inconsistências cadastrais, falhas de medição ou necessidade de inspeção comercial. Recomenda-se como ações prioritárias a substituição gradual dos hidrômetros críticos, a intensificação das fiscalizações em ligações classificadas como suspeitas e a implementação de monitoramento contínuo dos indicadores estratégicos apresentados no dashboard. As medidas propostas possuem potencial de aumento de faturamento, mitigação de perdas comerciais e melhoria da eficiência operacional, contribuindo diretamente para a sustentabilidade financeira da operação de saneamento.
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# RODAPÉ
# =========================================================

st.markdown(
    """
    <div class="rodape">
    @ Elisângela de Souza | Sistema Comercial de Água e Esgoto | 2026
    </div>
    """,
    unsafe_allow_html=True
)
