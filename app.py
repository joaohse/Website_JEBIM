import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
import os
from datetime import datetime
from github import Github

# -------------------------------------------------------------
# FUNÇÃO AUXILIAR PARA IMAGEM EM BASE64
# -------------------------------------------------------------
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

# Carrega o ícone JE.png para o favicon e para o menu lateral
b64_je_icon = get_base64_image("JE.png")
favicon_ref = "JE.png" if os.path.exists("JE.png") else "🔷"

# -------------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA & TEMA ESCURO EXECUTIVO
# -------------------------------------------------------------
st.set_page_config(
    page_title="BIM INSIGHT | Portal de Gestão",
    page_icon=favicon_ref,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS inspirada no layout executivo
st.markdown("""
<style>
    /* Fundo geral da aplicação */
    .stApp {
        background-color: #070d18 !important;
        color: #e2e8f0;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0a1120 !important;
        border-right: 1px solid #1e293b !important;
    }
    
    /* Headers do Streamlit */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Cards Executivos */
    .metric-card {
        background: linear-gradient(145deg, #0d1728, #09111e);
        border: 1px solid #1e2d42;
        border-radius: 12px;
        padding: 18px 20px;
        position: relative;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.03em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #64748b;
    }
    
    /* Card de Gráfico e Containers */
    .chart-container {
        background: #0a1220;
        border: 1px solid #1a2638;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    .chart-header {
        margin-bottom: 12px;
    }
    .chart-header h3 {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
    }
    .chart-header p {
        font-size: 0.8rem;
        color: #64748b;
        margin: 2px 0 0 0;
    }
    
    /* Painel de Insights */
    .insight-box {
        background: rgba(14, 25, 44, 0.65);
        border-left: 3px solid #0284c7;
        border-radius: 6px;
        padding: 14px;
        margin-top: 10px;
    }
    .insight-item {
        font-size: 0.82rem;
        color: #cbd5e1;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    
    /* Linha de Marcos (Steps) */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px solid #172338;
    }
    .step-item {
        text-align: center;
        flex: 1;
    }
    .step-badge {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .step-badge-active {
        background: #0284c7;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(2, 132, 199, 0.5);
    }
    .step-badge-inactive {
        background: #1e293b;
        color: #64748b;
    }
    .step-name {
        font-size: 0.74rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    .step-status {
        font-size: 0.68rem;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# INTEGRAÇÃO COM BANCO GITHUB
# -------------------------------------------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "")
DATA_FILE_PATH = "dados.json"

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        conteudo = repo.get_contents(DATA_FILE_PATH)
        dados = json.loads(conteudo.decoded_content.decode("utf-8"))
        return dados, conteudo.sha
    except Exception:
        try:
            with open("dados.json", "r", encoding="utf-8") as f:
                return json.load(f), None
        except:
            return {"empresas": {}}, None

def salvar_dados(novos_dados, sha=None):
    conteudo_str = json.dumps(novos_dados, indent=2, ensure_ascii=False)
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        if sha:
            repo.update_file(DATA_FILE_PATH, "Atualização via Portal BIM INSIGHT", conteudo_str, sha)
        else:
            conteudo_atual = repo.get_contents(DATA_FILE_PATH)
            repo.update_file(DATA_FILE_PATH, "Atualização via Portal BIM INSIGHT", conteudo_str, conteudo_atual.sha)
        st.cache_data.clear()
        return True
    except Exception:
        with open("dados.json", "w", encoding="utf-8") as f:
            f.write(conteudo_str)
        st.cache_data.clear()
        return True

DADOS, SHA_ATUAL = carregar_dados()
ADMIN_SENHA = st.secrets.get("ADMIN_SENHA", "admin123")

# -------------------------------------------------------------
# CONTROLE DE SESSÃO
# -------------------------------------------------------------
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
if "tipo_usuario" not in st.session_state:
    st.session_state["tipo_usuario"] = None

def login(usuario, senha):
    if usuario.lower() == "admin" and senha == ADMIN_SENHA:
        st.session_state["usuario_logado"] = "ADMIN"
        st.session_state["tipo_usuario"] = "admin"
        return True
    empresas = DADOS.get("empresas", {})
    if usuario in empresas and empresas[usuario]["senha"] == senha:
        st.session_state["usuario_logado"] = usuario
        st.session_state["tipo_usuario"] = "cliente"
        return True
    return False

def logout():
    st.session_state["usuario_logado"] = None
    st.session_state["tipo_usuario"] = None
    st.rerun()

# -------------------------------------------------------------
# TELA DE LOGIN (BACKGROUND VÍDEO + GLASSMORPHISM)
# -------------------------------------------------------------
if not st.session_state["usuario_logado"]:
    b64_video = ""
    try:
        with open("124333-730771399_medium.mp4", "rb") as vf:
            b64_video = base64.b64encode(vf.read()).decode()
    except Exception:
        pass

    b64_logo = ""
    try:
        with open("logo.png", "rb") as lf:
            b64_logo = base64.b64encode(lf.read()).decode()
    except Exception:
        pass

    st.markdown(
        f"""
        <style>
            .bg-video-container {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                overflow: hidden; z-index: -2;
            }}
            .bg-video {{ width: 100%; height: 100%; object-fit: cover; }}
            .bg-overlay {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: rgba(7, 13, 24, 0.82); backdrop-filter: blur(4px); z-index: -1;
            }}
            div[data-testid="stForm"] {{
                background: rgba(10, 18, 32, 0.8) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6) !important;
                border-radius: 14px !important;
            }}
        </style>
        <div class="bg-video-container">
            <video class="bg-video" autoplay loop muted playsinline>
                <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
            </video>
        </div>
        <div class="bg-overlay"></div>
        """,
        unsafe_allow_html=True
    )

    col_logo, _ = st.columns([1, 4])
    with col_logo:
        if b64_logo:
            st.markdown(
                f"""<div style="margin-top: 12px; margin-left: 10px; width: 140px;">
                    <img src="data:image/png;base64,{b64_logo}" style="width: 100%; filter: invert(1) brightness(1.2);">
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("""
        <div style="text-align: center; margin-top: 45px; margin-bottom: 25px;">
            <h1 style="font-size: 2.2rem; font-weight: 800; letter-spacing: 0.06em; color: #ffffff; margin-bottom: 4px;">PORTAL BIM INSIGHT</h1>
            <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 0px;">Acompanhamento Estratégico</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.15, 1])
    with c2:
        with st.form("form_login"):
            usuario = st.text_input("Código de Acesso / Usuário")
            senha = st.text_input("Senha", type="password")
            btn_entrar = st.form_submit_button("Entrar no Portal", use_container_width=True)
            if btn_entrar:
                if login(usuario, senha):
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
    st.stop()

# -------------------------------------------------------------
# PAINEL DO ADMINISTRADOR
# -------------------------------------------------------------
if st.session_state["tipo_usuario"] == "admin":
    st.sidebar.markdown(f"**Admin Conectado**")
    if st.sidebar.button("Encerrar Sessão", use_container_width=True):
        logout()

    st.title("Painel de Gestão da Consultoria | Admin")
    tab_cad, tab_av,
