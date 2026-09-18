import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
import os
from datetime import datetime
from github import Github

# -------------------------------------------------------------
# FUNÇÃO AUXILIAR PARA LEITURA DE FICHEIROS EM BASE64
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
# TELA DE LOGIN COM BACKGROUND EM VÍDEO
# -------------------------------------------------------------
if not st.session_state["usuario_logado"]:
    # Codificação do vídeo e da logo em Base64
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

    # Injeção de CSS para travar a cor cinza em qualquer tema (Light ou Dark)
    st.markdown(
        f"""
        <style>
            /* Remove fundos padrões do Streamlit */
            header[data-testid="stHeader"] {{
                background: transparent !important;
                z-index: 100;
            }}
            .stApp {{
                background: transparent !important;
            }}
            /* Camada de Vídeo em Tela Cheia */
            .bg-video-container {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                z-index: -2;
            }}
            .bg-video {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            /* Overlay escuro para contraste */
            .bg-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(11, 17, 32, 0.78);
                backdrop-filter: blur(4px);
                z-index: -1;
            }}
            
            /* Card do formulário com contorno cinza fixo */
            div[data-testid="stForm"] {{
                background: rgba(15, 23, 42, 0.85) !important;
                border: 1px solid #334155 !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
                border-radius: 14px !important;
                padding: 24px !important;
            }}

            /* Força a linha divisória nativa do stForm a ser cinza escuro (#334155) tanto no Light quanto no Dark */
            div[data-testid="stForm"] [data-testid="stVerticalBlock"] > div:has(button[kind="secondaryFormSubmit"]),
            div[data-testid="stForm"] [data-testid="stVerticalBlock"] > div:has(button[kind="primaryFormSubmit"]),
            div[data-testid="stForm"] > div:last-child {{
                border-top: 1px solid #334155 !important;
                padding-top: 14px !important;
                margin-top: 6px !important;
            }}

            /* Remove linhas ou bordas brancas padrão do Streamlit */
            div[data-testid="stForm"] hr {{
                border: none !important;
                border-top: 1px solid #334155 !important;
            }}

            /* Labels dos inputs sempre claras para contrastar com o card escuro */
            div[data-testid="stForm"] label p {{
                color: #CBD5E1 !important;
                font-weight: 600 !important;
            }}

            /* Campos de texto com borda e fundo escuro consistentes */
            div[data-testid="stForm"] input {{
                background-color: rgba(255, 255, 255, 0.07) !important;
                color: #F8F9FA !important;
                border: 1px solid #475569 !important;
                border-radius: 8px !important;
            }}
            div[data-testid="stForm"] input:focus {{
                border-color: #94A3B8 !important;
                box-shadow: 0 0 0 1px #94A3B8 !important;
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

    # Header / Logo
    col_logo, _ = st.columns([1, 4])
    with col_logo:
        if b64_logo:
            st.markdown(
                f"""
                <div style="margin-top: 10px; margin-left: 10px; width: 140px;">
                    <img src="data:image/png;base64,{b64_logo}" style="width: 100%; height: auto; display: block; filter: invert(1) brightness(1.2);">
                </div>
                """,
                unsafe_allow_html=True
            )

    # Título Principal e Subtítulo
    st.markdown("""
        <div style="text-align: center; margin-top: 35px; margin-bottom: 25px;">
            <h1 style="font-size: 2.3rem; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 4px; color: #ffffff; text-shadow: 0 2px 10px rgba(0,0,0,0.6);">PORTAL BIM INSIGHT</h1>
            <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 0px; text-shadow: 0 2px 6px rgba(0,0,0,0.6);">Acompanhamento Estratégico</p>
        </div>
    """, unsafe_allow_html=True)

    # Card de Login Centralizado
    c1, c2, c3 = st.columns([1, 1.15, 1])
    with c2:
        with st.form("form_login"):
            usuario = st.text_input("Código de Acesso / Usuário")
            senha = st.text_input("Senha", type="password")
            
            btn_entrar = st.form_submit_button("Entrar no Portal", use_container_width=True)
            
            if btn_entrar:
                if login(usuario, senha):
                    st.success("Acesso autorizado!")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique o código e a senha.")
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

    /* 30% ESTRUTURA: BARRA LATERAL EM AZUL MARINHO (#0A192F) */
    section[data-testid="stSidebar"] {
        background-color: #0A192F !important;
        border-right: 1px solid #1B263B !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #F8F9FA !important;
    }

    /* 10% DESTAQUE: BOTÕES CALL-TO-ACTION EM LARANJA INDUSTRIAL (#F26419) */
    button[kind="primary"], div.stButton > button {
        background-color: #F26419 !important;
        color: #FFFFFF !important;
        border: 1px solid #F26419 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 10px rgba(242, 100, 25, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[kind="primary"]:hover, div.stButton > button:hover {
        background-color: #D9530F !important;
        border-color: #D9530F !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(242, 100, 25, 0.35) !important;
    }

    /* MENU LATERAL CUSTOMIZADO SEM BOLINHA COM DESTAQUE ATIVO LARANJA */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child,
    div[data-testid="stRadio"] div[role="radiogroup"] label input[type="radio"],
    div[data-testid="stRadio"] svg {
        display: none !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        display: flex !important;
        align-items: center !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 9px 14px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: rgba(242, 100, 25, 0.12) !important;
        border-color: rgba(242, 100, 25, 0.4) !important;
        transform: translateX(3px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: rgba(242, 100, 25, 0.18) !important;
        border-left: 4px solid #F26419 !important;
        border-top: 1px solid rgba(242, 100, 25, 0.3) !important;
        border-right: 1px solid rgba(242, 100, 25, 0.3) !important;
        border-bottom: 1px solid rgba(242, 100, 25, 0.3) !important;
        box-shadow: 0 2px 10px rgba(242, 100, 25, 0.2) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: #94A3B8 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        letter-spacing: 0.02em !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        color: #F8F9FA !important;
        font-weight: 800 !important;
    }

    /* CARTÕES DE INDICADORES NÍTIDOS E BEM DEFINIDOS */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(10, 25, 47, 0.05);
        border-top: 3px solid #0A192F;
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #475569 !important;
        letter-spacing: 0.02em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 900;
        color: #0A192F !important;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #64748B !important;
        font-weight: 600;
    }
    .swot-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 10px rgba(10, 25, 47, 0.04);
        height: 100%;
    }
    .swot-title {
        font-weight: 800;
        font-size: 0.95rem;
        color: #0A192F !important;
        margin-bottom: 8px;
    }
    .doc-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(10, 25, 47, 0.03);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# PAINEL DO ADMINISTRADOR (CONSULTORIA)
# -------------------------------------------------------------
if st.session_state["tipo_usuario"] == "admin":
    st.sidebar.markdown("**Administrador Conectado**")
    if st.sidebar.button("Terminar Sessão", use_container_width=True):
        logout()

    st.title("Painel de Gestão & Diagnóstico BIM (Admin)")
    tab_cad, tab_av, tab_doc, tab_del = st.tabs([
        "➕ Registar Empresa", "📝 Inserir Nova Avaliação", "📁 Upload de Documentos", "🗑️ Eliminar Empresa"
    ])
    
    with tab_cad:
        st.subheader("Nova Empresa Cliente")
        with st.form("form_nova_empresa"):
            id_emp = st.text_input("ID único da Empresa (sem espaços, minúsculo)", placeholder="ex: fz_arquitetura")
            nome_emp = st.text_input("Nome da Empresa", placeholder="ex: FZ Arquitetura, Projeto e Gerenciamento")
            senha_emp = st.text_input("Senha de acesso do cliente", type="password")
            if st.form_submit_button("Salvar Empresa"):
                if id_emp and nome_emp and senha_emp:
                    DADOS.setdefault("empresas", {})[id_emp] = {
                        "nome": nome_emp, "senha": senha_emp, "avaliacoes": [], "documentos": []
                    }
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success(f"Empresa '{nome_emp}' registrada com sucesso!")
                        st.rerun()
                else:
                    st.warning("Preencha todos os campos obrigatórios.")

    with tab_av:
        st.subheader("Registrar Ciclo de Maturidade BIM")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if not empresas_opts:
            st.info("Cadastre uma empresa primeiro.")
        else:
            emp_sel = st.selectbox("Selecione a Empresa", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"])
            with st.form("form_avaliacao"):
                c1, c2 = st.columns(2)
                ciclo_nome = c1.text_input("Identificação do Ciclo", value="Ciclo 1 - Start")
                data_av = c2.date_input("Data da Avaliação", value=datetime.today())
                
                st.markdown("### Pontuação por Domínio (0 a 40 pts - Matriz Succar)")
                st.caption("0: Ad-hoc | 10: Definido | 20: Gerenciado | 30: Integrado | 40: Otimizado")
                
                col_tec, col_proc, col_pol = st.columns(3)
                with col_tec:
                    st.markdown("**Tecnologia**")
                    p_soft = st.slider("Software", 0, 40, 20, step=10)
                    p_hard = st.slider("Hardware", 0, 40, 20, step=10)
                    p_rede = st.slider("Rede / Infra", 0, 40, 10, step=10)
                
                with col_proc:
                    st.markdown("**Processos**")
                    p_rec = st.slider("Recursos & Pessoal", 0, 40, 20, step=10)
                    p_flux = st.slider("Fluxo de Trabalho", 0, 40, 20, step=10)
                    p_prod = st.slider("Produtos & Serviços", 0, 40, 15, step=10)
                
                with col_pol:
                    st.markdown("**Políticas & Estágios**")
                    p_pol = st.slider("Políticas & Contratos", 0, 40, 10, step=10)
                    p_est1 = st.slider("Estágio 1 (Modelagem)", 0, 40, 20, step=10)
                    p_est2 = st.slider("Estágio 2 (Colaboração)", 0, 40, 10, step=10)
                    p_est3 = st.slider("Estágio 3 (Integração)", 0, 40, 0, step=10)
                
                btn_salvar_av = st.form_submit_button("Salvar Avaliação no Banco", use_container_width=True)
                if btn_salvar_av:
                    pontos = [p_soft, p_hard, p_rede, p_rec, p_flux, p_prod, p_pol, p_est1, p_est2, p_est3]
                    media = sum(pontos) / len(pontos)
                    
                    nivel = "Ad-Hoc / Inicial"
                    if media >= 35: nivel = "Otimizado"
                    elif media >= 25: nivel = "Integrado"
                    elif media >= 15: nivel = "Gerenciado"
                    elif media >= 5: nivel = "Definido"
                    
                    nova_av = {
                        "data": str(data_av),
                        "ciclo": ciclo_nome,
                        "software": p_soft,
                        "hardware": p_hard,
                        "rede": p_rede,
                        "recursos": p_rec,
                        "fluxo": p_flux,
                        "produtos": p_prod,
                        "politicas": p_pol,
                        "estagio_modelagem": p_est1,
                        "estagio_colaboracao": p_est2,
                        "estagio_integracao": p_est3,
                        "media_global": round(media, 1),
                        "nivel": nivel
                    }
                    DADOS["empresas"][emp_sel]["avaliacoes"].append(nova_av)
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success("Avaliação gravada e sincronizada com sucesso!")
                        st.rerun()

    with tab_doc:
        st.subheader("Subir Relatório ou Diretrizes para a Empresa")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_doc = st.selectbox("Selecione a Empresa Destinatária", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"], key="sel_emp_doc")
            categoria = st.selectbox("Tipo de Documento (ISO 19650)", [
                "BIM Mandate", "BEP", "MIDP", "OIR", "AIR", "PIR", "EIR", "Geral"
            ])
            doc_nome = st.text_input("Título do Documento (Ex: Plano de Execução BIM - Revisão A)")
            s_doc = st.text_input("Subtítulo / Descrição (Ex: Versão preliminar para homologação)")
            arquivo = st.file_uploader("Selecione o arquivo (PDF, DWG, XLSX, ZIP)", type=["pdf", "xlsx", "docx", "zip"])
            
            if st.button("Enviar Arquivo"):
                if arquivo and doc_nome:
                    bytes_data = arquivo.read()
                    base64_str = base64.b64encode(bytes_data).decode("utf-8")
                    novo_doc = {
                        "categoria": categoria,
                        "titulo": doc_nome,
                        "subtitulo": s_doc,
                        "nome_arquivo": arquivo.name,
                        "data_envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "conteudo_b64": base64_str
                    }
                    DADOS["empresas"][emp_doc].setdefault("documentos", []).append(novo_doc)
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success(f"Documento '{arquivo.name}' disponibilizado com sucesso!")
                        st.rerun()
                else:
                    st.warning("Forneça o título e selecione um arquivo.")

    with tab_del:
        st.subheader("Eliminar Empresa")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_rm = st.selectbox("Empresa a remover", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"], key="rm_emp")
            if st.button("Confirmar Eliminação Definitiva", type="primary"):
                del DADOS["empresas"][emp_rm]
                if salvar_dados(DADOS, SHA_ATUAL):
                    st.success("Empresa eliminada do sistema!")
                    st.rerun()
    st.stop()

# -------------------------------------------------------------
# ÁREA DO CLIENTE (PORTAL BIM INSIGHT)
# -------------------------------------------------------------
empresa_id = st.session_state["usuario_logado"]
empresa_dados = DADOS.get("empresas", {}).get(empresa_id, {})
nome_empresa = empresa_dados.get("nome", "Organização")
avaliacoes = empresa_dados.get("avaliacoes", [])
documentos = empresa_dados.get("documentos", [])

b64_je_icon = get_base64_file("JE.png")

# BARRA LATERAL COM A TAXONOMIA ISO 19650
with st.sidebar:
    if b64_je_icon:
        icone_marca_html = f'<img src="data:image/png;base64,{b64_je_icon}" style="width: 38px; height: 38px; object-fit: contain; border-radius: 4px; filter: invert(1); display: block;">'
    else:
        icone_marca_html = '<div style="width: 36px; height: 36px; background: #1B263B; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1rem; color: #F26419;">JE</div>'

    html_header_side = f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-top: 8px;">
            {icone_marca_html}
            <div>
                <div style="font-weight: 900; font-size: 1.05rem; letter-spacing: 0.04em; color: #F8F9FA;">BIM INSIGHT</div>
                <div style="font-size: 0.72rem; color: #94A3B8;">Acompanhamento Estratégico</div>
            </div>
        </div>
    """
    st.markdown(html_header_side, unsafe_allow_html=True)
    
    lista_abas = [
        "Visão Geral",
        "BIM Mandate",
        "BEP",
        "MIDP",
        "OIR",
        "AIR",
        "PIR",
        "EIR"
    ]
    
    menu_selecionado = st.radio(
        "Navegação",
        lista_abas,
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    primeiro_nome = nome_empresa.split()[0] if nome_empresa else "Cliente"
    st.caption(f"Conectado como: **{primeiro_nome}**")
    if st.button("Terminar Sessão", use_container_width=True):
        logout()

# CABEÇALHO EXECUTIVO NA ÁREA PRINCIPAL
html_topo_exec = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
        <div>
            <h1 style="font-size: 1.95rem; font-weight: 900; color: #0A192F; margin: 0;">{nome_empresa}</h1>
            <p style="font-size: 0.95rem; color: #F26419; margin: 4px 0 0 0; font-weight: 700;">Visão Estratégica BIM</p>
        </div>
        <div style="text-align: right; color: #475569; font-size: 0.82rem; line-height: 1.4; font-weight: 600;">
            Mais eficiência.<br>Melhores decisões.<br>Resultados sustentáveis.
        </div>
    </div>
"""
st.markdown(html_topo_exec, unsafe_allow_html=True)

# -------------------------------------------------------------
# FUNÇÃO PARA RENDERIZAR SECÇÕES DOCUMENTAIS (ISO 19650)
# -------------------------------------------------------------
def renderizar_modulo_documental(sigla, nome_completo, descricao, norma_ref, objetivos):
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="background: #F26419; color: #FFFFFF !important; font-weight: 800; font-size: 0.85rem; padding: 4px 10px; border-radius: 6px;">{sigla}</span>
                <h2 style="font-size: 1.4rem; font-weight: 800; color: #0A192F; margin: 0;">{nome_completo}</h2>
            </div>
            <p style="font-size: 0.9rem; color: #475569; margin: 6px 0 0 0; font-weight: 500;">{descricao}</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.8, 1.2])
    with c1:
        st.markdown(f"""
            <div class="swot-card" style="border-left: 4px solid #F26419;">
                <div class="swot-title">📌 Âmbito & Diretrizes de Aplicação</div>
                <div style="font-size: 0.86rem; color: #1B263B; line-height: 1.6; font-weight: 500;">
                    {objetivos}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="swot-card" style="border-left: 4px solid #0A192F;">
                <div class="swot-title">📐 Referência Normativa</div>
                <div style="font-size: 0.86rem; color: #1B263B; line-height: 1.6; font-weight: 500;">
                    <b>Padrão:</b> {norma_ref}<br>
                    <b>Governança:</b> Gestão da Informação em BIM<br>
                    <b>Responsável:</b> Consultoria JE BIM Management
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #0A192F; font-weight: 800;'>📄 Documentos & Entregáveis Homologados ({sigla})</h3>", unsafe_allow_html=True)

    docs_categoria = [d for d in documentos if d.get("categoria") == sigla or sigla in d.get("titulo", "").upper()]

    if not docs_categoria:
        st.markdown(f"""
            <div class="doc-box" style="text-align: center; padding: 30px 20px;">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">📑</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #0A192F;">Documento em Fase de Estruturação / Homologação</div>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 4px;">
                    O documento de <b>{sigla}</b> está a ser desenvolvido com a equipa técnica. Assim que for concluído e validado, ficará disponível para descarregamento nesta secção.
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for doc in docs_categoria:
            col_d1, col_d2 = st.columns([3.8, 1.2])
            with col_d1:
                t_doc = doc.get('titulo', sigla)
                s_doc = doc.get('subtitulo', doc.get('nome_arquivo', ''))
                dt_doc = doc.get('data_envio', '-')
                st.markdown(f"""
                    <div style="padding: 8px 0;">
                        <div style="font-weight: 800; font-size: 1rem; color: #0A192F;">📄 {t_doc}</div>
                        <div style="font-size: 0.85rem; color: #475569; margin-top: 3px;">{s_doc}</div>
                        <div style="font-size: 0.78rem; color: #64748B; margin-top: 4px;">
                            <span style="background: #F26419; color: #FFFFFF !important; padding: 2px 8px; border-radius: 4px; font-weight: 700;">Homologado</span>
                            &nbsp;•&nbsp; Disponibilizado em: {dt_doc}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_d2:
                st.write("")
                bytes_bin = base64.b64decode(doc['conteudo_b64'])
                st.download_button(
                    label="⬇️ Descarregar ficheiro",
                    data=bytes_bin,
                    file_name=doc.get('nome_arquivo', f'{sigla}.pdf'),
                    use_container_width=True,
                    key=f"dl_mod_{sigla}_{doc.get('titulo', '')}"
                )
            st.markdown("<div style='border-bottom: 1px solid #E2E8F0; margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# CONTEÚDO: VISÃO GERAL (DASHBOARD)
# -------------------------------------------------------------
if menu_selecionado == "Visão Geral":
    if not avaliacoes:
        st.info("Nenhuma avaliação registrada até o momento. O consultor está preparando seus dados.")
    else:
        ult_av = avaliacoes[-1]
        
        # 1. CARDS KPIS SUPERIORES NÍTI DOS E DESTACADOS
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">⏱️ Índice Médio Global</div>
                    <div class="metric-value">{ult_av['media_global']} pts</div>
                    <div class="metric-sub">/ 40 pts (Escala Succar)</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">📚 Nível Predominante</div>
                    <div class="metric-value">{ult_av['nivel']}</div>
                    <div class="metric-sub">Estágio de Maturidade BIM</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🔄 Último Ciclo</div>
                    <div class="metric-value">{ult_av['ciclo']}</div>
                    <div class="metric-sub">Avaliação mais recente</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">📋 Total de Revisões</div>
                    <div class="metric-value">{len(avaliacoes)} ciclos</div>
                    <div class="metric-sub">Histórico acumulado</div>
                </div>
            """, unsafe_allow_html=True)
                
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        
        # 2. GRÁFICOS ANALÍTICOS (LARANJA INDUSTRIAL #F26419 + EIXOS NÍTIDOS)
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("""
                <div style="margin-bottom: 8px;">
                    <h3 style="font-size: 1.2rem; font-weight: 800; color: #0A192F; margin: 0;">Equilíbrio de Competências (Radar)</h3>
                </div>
            """, unsafe_allow_html=True)
            
            categorias = ['Software', 'Hardware', 'Rede', 'Recursos', 'Fluxo', 'Produtos', 'Políticas']
            valores_atuais = [
                ult_av.get('software', 0), ult_av.get('hardware', 0), ult_av.get('rede', 0),
                ult_av.get('recursos', 0), ult_av.get('fluxo', 0), ult_av.get('produtos', 0), ult_av.get('politicas', 0)
            ]
            
            fig_radar = go.Figure()
            # Ciclo atual em Laranja Industrial vibrante (#F26419)
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_atuais,
                theta=categorias,
                fill='toself',
                fillcolor='rgba(242, 100, 25, 0.18)',
                name=ult_av['ciclo'],
                line=dict(color='#F26419', width=3),
                marker=dict(size=7, color='#F26419', line=dict(color='#FFFFFF', width=1.5))
            ))
            
            # Ciclo anterior tracejado em tom escuro de contraste (#0A192F)
            if len(avaliacoes) > 1:
                penult_av = avaliacoes[-2]
                valores_ant = [
                    penult_av.get('software', 0), penult_av.get('hardware', 0), penult_av.get('rede', 0),
                    penult_av.get('recursos', 0), penult_av.get('fluxo', 0), penult_av.get('produtos', 0), penult_av.get('politicas', 0)
                ]
                fig_radar.add_trace(go.Scatterpolar(
                    r=valores_ant,
                    theta=categorias,
                    name=penult_av['ciclo'],
                    line=dict(color='#0A192F', dash='dash', width=2),
                    marker=dict(size=5, color='#0A192F')
                ))
            
            # Eixos e malhas com leitura em cinza e azul marinho
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, 
                        range=[0, 40],
                        gridcolor='#CBD5E1',
                        linecolor='#94A3B8',
                        tickfont=dict(size=9, color='#64748B', family='Arial, sans-serif')
                    ),
                    angularaxis=dict(
                        gridcolor='#CBD5E1',
                        linecolor='#94A3B8',
                        tickfont=dict(size=11, color='#0A192F', family='Arial, sans-serif', weight='bold')
                    )
                ),
                showlegend=True,
                legend=dict(font=dict(color='#0A192F', family='Arial, sans-serif')),
                margin=dict(l=40, r=40, t=30, b=30),
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
        with g2:
            st.markdown("""
                <div style="margin-bottom: 8px;">
                    <h3 style="font-size: 1.2rem; font-weight: 800; color: #0A192F; margin: 0;">Evolução Histórica da Maturidade</h3>
                </div>
            """, unsafe_allow_html=True)
            
            df_hist = pd.DataFrame(avaliacoes)
            fig_line = go.Figure()
            # Linha e pontos de marcação em Laranja Industrial (#F26419)
            fig_line.add_trace(go.Scatter(
                x=df_hist['ciclo'],
                y=df_hist['media_global'],
                mode='lines+markers+text',
                text=[f"{v} pts" for v in df_hist['media_global']],
                textposition="top center",
                textfont=dict(color='#0A192F', size=11, family='Arial, sans-serif', weight='bold'),
                line=dict(color='#F26419', width=3.5),
                marker=dict(size=9, color='#F26419', line=dict(color='#0A192F', width=2))
            ))
            fig_line.update_layout(
                yaxis=dict(
                    range=[0, 42], 
                    title=dict(text="Pontuação Média", font=dict(color='#0A192F', size=11, weight='bold')),
                    gridcolor='#CBD5E1',
                    linecolor='#94A3B8',
                    tickfont=dict(color='#475569', size=10)
                ),
                xaxis=dict(
                    title=dict(text="Ciclos de Auditoria", font=dict(color='#0A192F', size=11, weight='bold')),
                    gridcolor='#CBD5E1',
                    linecolor='#94A3B8',
                    tickfont=dict(color='#0A192F', size=10, weight='bold')
                ),
                height=350,
                margin=dict(l=40, r=40, t=30, b=30),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # 3. IDENTIDADE ESTRATÉGICA CORPORATIVA
        st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="margin-bottom: 14px;">
                <h3 style="font-size: 1.25rem; font-weight: 800; color: #0A192F; margin: 0;">🎯 Identidade Estratégica Corporativa</h3>
                <p style="font-size: 0.88rem; color: #475569; margin: 2px 0 0 0; font-weight: 500;">Diretrizes fundamentais para orientar a transformação digital e os padrões de entrega</p>
            </div>
        """, unsafe_allow_html=True)

        col_m, col_v, col_val = st.columns(3)
        with col_m:
            st.markdown("""
                <div class="metric-card" style="min-height: 240px; border-top: 4px solid #F26419;">
                    <div style="font-size: 1.2rem; margin-bottom: 8px;">🎯</div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #0A192F; margin-bottom: 8px;">Missão</div>
                    <div style="font-size: 0.88rem; color: #1B263B; line-height: 1.6; font-weight: 500;">
                        Desenvolver projetos integrados e gestão técnica com excelência, transformando necessidades espaciais e operacionais em soluções arquitetónicas eficientes, sustentáveis e tecnologicamente sólidas.
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col_v:
            st.markdown("""
                <div class="metric-card" style="min-height: 240px; border-top: 4px solid #0A192F;">
                    <div style="font-size: 1.2rem; margin-bottom: 8px;">🔭</div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #0A192F; margin-bottom: 8px;">Visão</div>
                    <div style="font-size: 0.88rem; color: #1B263B; line-height: 1.6; font-weight: 500;">
                        Consolidar-se como referência regional em maturidade digital e metodologia BIM, garantindo tomadas de decisão antecipadas, previsibilidade de custo/obra e entregáveis de alto padrão construtivo.
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col_val:
            st.markdown("""
                <div class="metric-card" style="min-height: 240px; border-top: 4px solid #F26419;">
                    <div style="font-size: 1.2rem; margin-bottom: 8px;">💎</div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #0A192F; margin-bottom: 8px;">Valores</div>
                    <div style="font-size: 0.88rem; color: #1B263B; line-height: 1.6; font-weight: 500;">
                        • <b>Rigor Técnico</b>: Modelação precisa e consistência na informação.<br>
                        • <b>Colaboração Aberta</b>: Integração ativa com parceiros e clientes.<br>
                        • <b>Inovação Contínua</b>: Adoção prática das melhores diretrizes BIM.<br>
                        • <b>Sustentabilidade</b>: Redução de retrabalho pela pré-construção virtual.
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 4. ANÁLISE SWOT
        st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="margin-bottom: 14px;">
                <h3 style="font-size: 1.25rem; font-weight: 800; color: #0A192F; margin: 0;">📊 Matriz SWOT da Transformação BIM</h3>
                <p style="font-size: 0.88rem; color: #475569; margin: 2px 0 0 0; font-weight: 500;">Mapeamento de forças internas e dinâmica externa de mercado</p>
            </div>
        """, unsafe_allow_html=True)

        c_swot1, c_swot2 = st.columns(2)
        with c_swot1:
            st.markdown("""
                <div class="swot-card" style="border-left: 4px solid #0A192F; margin-bottom: 12px;">
                    <div class="swot-title">🟢 Forças (Strengths)</div>
                    <div style="font-size: 0.88rem; color: #1B263B; line-height: 1.55; font-weight: 500;">
                        • Empenho da liderança na consolidação dos fluxos digitais.<br>
                        • Reputação consolidada em arquitetura de alto padrão e detalhe executivo.<br>
                        • Disponibilidade da equipa técnica para integrar novos softwares e rotinas BIM.
                    </div>
                </div>
                <div class="swot-card" style="border-left: 4px solid #F26419;">
                    <div class="swot-title">🟡 Fraquezas (Weaknesses)</div>
                    <div style="font-size: 0.88rem; color: #1B263B; line-height: 1.55; font-weight: 500;">
                        • Necessidade de padronização nas famílias e modelos paramétricos.<br>
                        • Processos de deteção de colisões (Clash Detection) em fase inicial de estruturação.<br>
                        • Documentação de processos (BEP interno) em consolidação.
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with c_swot2:
            st.markdown("""
                <div class="swot-card" style="border-left: 4px solid #0A192F; margin-bottom: 12px;">
                    <div class="swot-title">🔵 Oportunidades (Opportunities)</div>
                    <div style="font-size: 0.88rem; color: #1B263B; line-height: 1.55; font-weight: 500;">
                        • Posicionamento de destaque perante clientes e concursos que exigem BIM.<br>
                        • Redução mensurável de retrabalho no estaleiro via coordenação 3D/4D.<br>
                        • Oferta de serviços consultivos integrados e compatibilização avançada.
                    </div>
                </div>
                <div class="swot-card" style="border-left: 4px solid #F26419;">
                    <div class="swot-title">🔴 Ameaças (Threats)</div>
                    <div style="font-size: 0.88rem; color: #1B263B; line-height: 1.55; font-weight: 500;">
                        • Projetistas parceiros com práticas limitadas a CAD 2D tradicional.<br>
                        • Prazos contratuais reduzidos que condicionam o tempo de arranque da modelação.<br>
                        • Custos de atualização contínua de licenças e postos de trabalho de alto rendimento.
                    </div>
                </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# CONTEÚDO DAS ABAS DE GOVERNANÇA ISO 19650
# -------------------------------------------------------------
elif menu_selecionado == "BIM Mandate":
    renderizar_modulo_documental(
        sigla="BIM Mandate",
        nome_completo="Mandato Institucional BIM",
        descricao="Diretriz corporativa que estabelece a obrigatoriedade, princípios e padrões corporativos para adoção do BIM em todos os empreendimentos.",
        norma_ref="Diretriz Estratégica Institucional / ISO 19650-1",
        objetivos="• Fixar metas corporativas para a metodologia BIM nos ciclos de projeto.<br>• Estabelecer papéis e responsabilidades institucionais da direção e equipas.<br>• Definir os requisitos mínimos de interoperabilidade e formato aberto (IFC/BCF)."
    )

elif menu_selecionado == "BEP":
    renderizar_modulo_documental(
        sigla="BEP",
        nome_completo="BIM Execution Plan (Plano de Execução BIM)",
        descricao="Documento orientador que especifica a operacionalização dos requisitos de modelação, coordenação e entrega de informação pelas equipas envolvidas.",
        norma_ref="ISO 19650-2 (Cláusula 5.3 & 5.4)",
        objetivos="• Detalhar os fluxos de trabalho, software utilizado e versões adotadas.<br>• Mapear a matriz de responsabilidades e níveis de necessidade de informação (LOIN/LOD).<br>• Definir os procedimentos de controlo de qualidade e deteção de interferências."
    )

elif menu_selecionado == "MIDP":
    renderizar_modulo_documental(
        sigla="MIDP",
        nome_completo="Master Information Delivery Plan",
        descricao="Plano Diretor de Entrega de Informação que consolida o cronograma das entregas de modelos, desenhos, especificações e relatórios de todas as disciplinas.",
        norma_ref="ISO 19650-2 (Cláusula 5.4.5)",
        objetivos="• Integrar os Planos Individuais de Entrega de Tarefas (TIDP).<br>• Assegurar a coerência temporal entre entregáveis de arquitetura e especialidades.<br>• Vincular datas de entrega aos marcos de decisão do cliente."
    )

elif menu_selecionado == "OIR":
    renderizar_modulo_documental(
        sigla="OIR",
        nome_completo="Organizational Information Requirements",
        descricao="Requisitos de Informação da Organização que decorrem dos objetivos estratégicos corporativos e das metas de gestão a nível empresarial.",
        norma_ref="ISO 19650-1 (Cláusula 5.1)",
        objetivos="• Alinhar os dados recolhidos no modelo com o plano estratégico do negócio.<br>• Fornecer indicadores para análise financeira, sustentabilidade e conformidade.<br>• Garantir a continuidade de informação para apoio a auditorias de gestão."
    )

elif menu_selecionado == "AIR":
    renderizar_modulo_documental(
        sigla="AIR",
        nome_completo="Asset Information Requirements",
        descricao="Requisitos de Informação do Ativo que estabelecem os dados operacionais e de manutenção necessários para a fase de exploração do edifício (Facility Management).",
        norma_ref="ISO 19650-1 & ISO 19650-3",
        objetivos="• Especificar propriedades técnicas, garantias e códigos de manutenção dos equipamentos.<br>• Estruturar a passagem do modelo de construção (PIM) para o modelo de operação (AIM).<br>• Reduzir os custos de ciclo de vida através da integração com plataformas GMAO/FM."
    )

elif menu_selecionado == "PIR":
    renderizar_modulo_documental(
        sigla="PIR",
        nome_completo="Project Information Requirements",
        descricao="Requisitos de Informação do Projeto que explicitam as informações críticas necessárias para apoiar decisões estratégicas em cada marco de aprovação do projeto.",
        norma_ref="ISO 19650-1 (Cláusula 5.2)",
        objetivos="• Estabelecer as questões estratégicas a responder em cada fase de desenvolvimento.<br>• Estruturar os pontos de controlo para validação de custos, prazos e conformidade regulamentar.<br>• Servir de base para a redação dos requisitos contratuais de contratação."
    )

elif menu_selecionado == "EIR":
    renderizar_modulo_documental(
        sigla="EIR",
        nome_completo="Exchange Information Requirements",
        descricao="Caderno de encargos e requisitos de contratação BIM que define formalmente o que, quando e em que formato cada disciplina deve entregar os seus dados.",
        norma_ref="ISO 19650-2 (Cláusula 5.2)",
        objetivos="• Estabelecer padrões técnicos obrigatórios nos contratos de projetistas externos.<br>• Definir sistemas de coordenadas partilhadas, matriz de atributos e convenções de nomenclatura.<br>• Regular o funcionamento do Ambiente Comum de Dados (CDE)."
    )
