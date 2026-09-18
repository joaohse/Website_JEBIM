import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
import os
from datetime import datetime
from github import Github

# -------------------------------------------------------------
# FUNÇÃO AUXILIAR PARA LEITURA DE ARQUIVOS EM BASE64
# -------------------------------------------------------------
def get_base64_file(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""

icone_favicon = "JE.png" if os.path.exists("JE.png") else "🔷"

# -------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------------------
st.set_page_config(
    page_title="BIM INSIGHT | Portal de Gestão Estratégica",
    page_icon=icone_favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# INTEGRAÇÃO COM A BASE DE DADOS NO GITHUB
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
        except Exception:
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
# GESTÃO DE SESSÃO DO UTILIZADOR
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
# ECRÃ DE AUTENTICAÇÃO (LOGIN)
# -------------------------------------------------------------
if not st.session_state["usuario_logado"]:
    b64_video = get_base64_file("124333-730771399_medium.mp4")
    b64_logo = get_base64_file("logo.png")

    st.markdown("""
        <style>
            .bg-video-container {
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                overflow: hidden;
                z-index: -2;
            }
            .bg-video {
                width: 100%; height: 100%;
                object-fit: cover;
            }
            .bg-overlay {
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                background: rgba(10, 25, 47, 0.85);
                backdrop-filter: blur(4px);
                z-index: -1;
            }
            div[data-testid="stForm"] {
                background: rgba(248, 249, 250, 0.96) !important;
                border: 1px solid #CBD5E1 !important;
                box-shadow: 0 20px 45px rgba(10, 25, 47, 0.35) !important;
                border-radius: 14px !important;
                padding: 24px !important;
            }
            div[data-testid="stForm"] label, div[data-testid="stForm"] h1, div[data-testid="stForm"] p {
                color: #0A192F !important;
            }
        </style>
    """, unsafe_allow_html=True)

    if b64_video:
        st.markdown(
            f"""
            <div class="bg-video-container">
                <video class="bg-video" autoplay loop muted playsinline>
                    <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
                </video>
            </div>
            <div class="bg-overlay"></div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="bg-overlay"></div>', unsafe_allow_html=True)

    col_logo, _ = st.columns([1, 4])
    with col_logo:
        if b64_logo:
            st.markdown(
                f"""
                <div style="margin-top: 12px; margin-left: 10px; width: 140px;">
                    <img src="data:image/png;base64,{b64_logo}" style="width: 100%; filter: invert(1) brightness(1.2);">
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("""
        <div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
            <h1 style="font-size: 2.2rem; font-weight: 900; letter-spacing: 0.06em; color: #F8F9FA; margin-bottom: 4px;">PORTAL BIM INSIGHT</h1>
            <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 0px;">Acompanhamento Estratégico</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.15, 1])
    with c2:
        with st.form("form_login"):
            usuario = st.text_input("Código de Acesso / Utilizador")
            senha = st.text_input("Palavra-passe", type="password")
            btn_entrar = st.form_submit_button("Entrar no Portal", use_container_width=True)
            if btn_entrar:
                if login(usuario, senha):
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique o código e a palavra-passe.")
    st.stop()

# -------------------------------------------------------------
# PALETA 60-30-10: BASE #F8F9FA | ESTRUTURA #0A192F | DESTAQUE #F26419
# -------------------------------------------------------------
st.markdown("""
<style>
    /* 60% BASE: BRANCO NEVE (#F8F9FA) */
    .stApp,
    section[data-testid="stMain"],
    div[data-testid="stAppViewBlockContainer"],
    div[data-testid="stMainBlockContainer"] {
        background-color: #F8F9FA !important;
        color: #0A192F !important;
    }
    
    /* 30% ESTRUTURA: TIPOGRAFIA PRINCIPAL EM AZUL MARINHO PROFUNDO (#0A192F) */
    section[data-testid="stMain"] h1,
    section[data-testid="stMain"] h2,
    section[data-testid="stMain"] h3,
    section[data-testid="stMain"] h4 {
        color: #0A192F !important;
        font-weight: 800 !important;
    }
    section[data-testid="stMain"] p,
    section[data-testid="stMain"] span,
    section[data-testid="stMain"] div,
    section[data-testid="stMain"] label {
        color: #1B263B !important;
    }

    /*
