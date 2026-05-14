# 💧 Sistema Comercial de Água e Esgoto

> Sistema web para gestão comercial de serviços de água e esgoto, desenvolvido em Python com interface interativa via Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sistemaaguasaneamento.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Notebook-Jupyter-orange?logo=jupyter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Sobre o Projeto

O **Sistema Comercial de Água e Esgoto** é uma aplicação web desenvolvida para auxiliar na gestão e análise de dados relacionados ao fornecimento de água e serviços de esgoto. A solução foi construída com base em notebooks Python e disponibilizada na nuvem por meio do **Streamlit Cloud**, proporcionando acesso fácil e sem necessidade de instalação local.

---

## ✨ Funcionalidades

- 📊 **Dashboard interativo** com visualização de dados comerciais
- 💰 **Gestão de faturamento** — controle de cobranças e consumo por cliente
- 📈 **Análises e relatórios** — gráficos e tabelas para apoio à decisão
- 🗂️ **Base de dados integrada** — leitura e processamento de arquivos de dados
- 📥 **Exportação de relatórios** — suporte a formatos Excel (`.xlsx`) e outros
- 🔍 **Filtros dinâmicos** — consulta por período, região, categoria de consumidor, etc.

---

## 🗂️ Estrutura do Repositório

```
sistema_agua_saneamento/
│
├── assets/                  # Imagens, ícones e recursos visuais
├── data/                    # Base de dados (arquivos .csv, .xlsx, etc.)
├── notebooks/               # Notebooks Jupyter com a lógica do sistema
├── .gitignore               # Arquivos e pastas ignorados pelo Git
├── README.md                # Documentação do projeto
├── app.py                   # Aplicação principal Streamlit
└── requirements.txt         # Dependências do projeto
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/elissouza2023/sistema_agua_saneamento.git
cd sistema_agua_saneamento

# 2. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501` no seu navegador.

---

## ☁️ Deploy

A aplicação está hospedada no **Streamlit Community Cloud** e pode ser acessada diretamente pelo link:

🔗 **[sistemaaguasaneamento.streamlit.app](https://sistemaaguasaneamento.streamlit.app/)**

> Nenhuma instalação é necessária para utilizar a versão online.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| [Python](https://www.python.org/) | Linguagem principal |
| [Streamlit](https://streamlit.io/) | Interface web interativa |
| [Jupyter Notebook](https://jupyter.org/) | Desenvolvimento e prototipagem |
| [Pandas](https://pandas.pydata.org/) | Manipulação e análise de dados |
| [OpenPyXL](https://openpyxl.readthedocs.io/) | Leitura/escrita de arquivos Excel |
| [xlrd](https://xlrd.readthedocs.io/) | Suporte a arquivos `.xls` legados |
| [Plotly / Matplotlib](https://plotly.com/) | Visualização de dados |

> As dependências completas estão listadas em [`requirements.txt`](./requirements.txt).

---

## 📊 Notebooks

A pasta `notebooks/` contém os arquivos Jupyter utilizados para:

- Exploração e limpeza da base de dados
- Desenvolvimento das análises e cálculos
- Prototipagem das visualizações antes de integrar ao app

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um **fork** do repositório
2. Crie uma branch para sua feature: `git checkout -b feature/minha-feature`
3. Commit suas alterações: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Faça o push: `git push origin feature/minha-feature`
5. Abra um **Pull Request**

---

## 👤 Autor

Desenvolvido por **[@elissouza2023](https://github.com/elissouza2023)**
---

## 🛠️ Deploy

Link do Deploy:  **https://sistemaaguasaneamento.streamlit.app/**

---

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o arquivo [LICENSE](./LICENSE) para mais detalhes.
