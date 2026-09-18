import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
import os
from datetime import datetime
from github import Github

def get_base64_file(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")import streamlit as st
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
# INTEGRAÇÃO COM BASE DE DADOS NO GITHUB
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
# ECRÃ DE AUTENTICAÇÃO (VÍDEO DE FUNDO & GLASSMORPHISM)
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
                background: rgba(7, 13, 24, 0.82);
                backdrop-filter: blur(4px);
                z-index: -1;
            }
            div[data-testid="stForm"] {
                background: rgba(10, 18, 32, 0.85) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6) !important;
                border-radius: 14px !important;
                padding: 24px !important;
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
            <h1 style="font-size: 2.2rem; font-weight: 800; letter-spacing: 0.06em; color: #ffffff; margin-bottom: 4px;">PORTAL BIM INSIGHT</h1>
            <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 0px;">Acompanhamento Estratégico</p>
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
# CSS DO PORTAL EXECUTIVO INTERNO
# -------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #070d18;
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background-color: #0a1120 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Oculta as bolinhas de seleção e estiliza as caixas transparentes do menu */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: rgba(2, 132, 199, 0.12) !important;
        border-color: rgba(56, 189, 248, 0.35) !important;
        transform: translateX(3px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: rgba(2, 132, 199, 0.22) !important;
        border-color: #0284c7 !important;
        box-shadow: 0 2px 12px rgba(2, 132, 199, 0.25) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }

    .metric-card {
        background: linear-gradient(145deg, #0d1728, #09111e);
        border: 1px solid #1e2d42;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.03em;
        margin-bottom: 6px;
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
    .chart-header h3 {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
    }
    .chart-header p {
        font-size: 0.8rem;
        color: #64748b;
        margin: 2px 0 10px 0;
    }
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
        margin-bottom: 8px;
        line-height: 1.4;
    }
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
    .swot-card {
        background: #0a1322;
        border: 1px solid #162438;
        border-radius: 10px;
        padding: 16px;
        height: 100%;
    }
    .swot-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 8px;
    }
    .doc-box {
        background: #0d1627;
        border: 1px solid #1e2d42;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
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

    st.title("Painel de Gestão da Consultoria | Admin")
    tab_cad, tab_av, tab_doc, tab_del = st.tabs([
        "➕ Registar Empresa", "📝 Registar Ciclo", "📁 Carregar Entregável", "🗑️ Eliminar Empresa"
    ])
    
    with tab_cad:
        st.subheader("Registar Nova Organização")
        with st.form("form_cad_emp"):
            id_e = st.text_input("ID único da empresa (ex: fz_arquitetura)").strip().lower()
            nome_e = st.text_input("Nome Corporativo (ex: FZ Arquitetura, Projeto e Gerenciamento)")
            senha_e = st.text_input("Palavra-passe de Acesso", type="password")
            if st.form_submit_button("Guardar Organização"):
                if id_e and nome_e and senha_e:
                    DADOS.setdefault("empresas", {})[id_e] = {
                        "nome": nome_e, "senha": senha_e, "avaliacoes": [], "documentos": []
                    }
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success("Empresa registada com sucesso!")
                        st.rerun()

    with tab_av:
        st.subheader("Lançar Diagnóstico / Ciclo de Maturidade BIM")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_sel = st.selectbox("Selecione a Organização", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"])
            with st.form("form_reg_av"):
                c1, c2 = st.columns(2)
                ciclo_txt = c1.text_input("Identificação do Ciclo", value="Ciclo 1 - Start")
                data_av = c2.date_input("Data do Ciclo", value=datetime.today())
                
                st.caption("Pontuações da Matriz Succar (0 = Inicial a 40 = Otimizado)")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown("**Tecnologia & Estratégia**")
                    p_soft = st.slider("Tecnologia / Software", 0, 40, 20, 10)
                    p_hard = st.slider("Infraestrutura / Hardware", 0, 40, 20, 10)
                    p_est = st.slider("Estratégia BIM", 0, 40, 10, 10)
                with col_b:
                    st.markdown("**Processos & Pessoas**")
                    p_proc = st.slider("Processos / Fluxos", 0, 40, 15, 10)
                    p_pess = st.slider("Pessoas / Competências", 0, 40, 10, 10)
                    p_gest = st.slider("Gestão & Liderança", 0, 40, 10, 10)
                with col_c:
                    st.markdown("**Políticas & Contratos**")
                    p_cont = st.slider("Contratos & Políticas", 0, 40, 10, 10)
                    p_prod = st.slider("Produtos & Entregáveis", 0, 40, 15, 10)
                    p_proj = st.slider("Projetos / Colaboração", 0, 40, 10, 10)

                st.markdown("**Principais Insights Estratégicos (Apresentados ao Cliente)**")
                insight_1 = st.text_input("Insight 1", value="Destaque para a competência em Tecnologia, com melhor desempenho no ciclo atual.")
                insight_2 = st.text_input("Insight 2", value="Oportunidade de evolução nas competências de Pessoas e Gestão.")
                insight_3 = st.text_input("Insight 3", value="Equilíbrio geral com espaço para estruturação progressiva em todas as áreas.")

                if st.form_submit_button("Gravar Ciclo de Avaliação"):
                    pontos = [p_soft, p_hard, p_est, p_proc, p_pess, p_gest, p_cont, p_prod, p_proj]
                    media = sum(pontos) / len(pontos)
                    
                    nivel = "Ad-Hoc / Inicial"
                    if media >= 35: nivel = "Otimizado"
                    elif media >= 25: nivel = "Integrado"
                    elif media >= 15: nivel = "Gerenciado"
                    elif media >= 5: nivel = "Definido"

                    nova_av = {
                        "ciclo": ciclo_txt,
                        "data": str(data_av),
                        "software": p_soft, "hardware": p_hard, "estrategia": p_est,
                        "processos": p_proc, "pessoas": p_pess, "gestao": p_gest,
                        "contratos": p_cont, "produtos": p_prod, "projetos": p_proj,
                        "media_global": round(media, 1),
                        "nivel": nivel,
                        "insights": [insight_1, insight_2, insight_3]
                    }
                    DADOS["empresas"][emp_sel]["avaliacoes"].append(nova_av)
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success("Ciclo registado com sucesso!")
                        st.rerun()

    with tab_doc:
        st.subheader("Carregar Documento / Entregável para a Organização")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_d = st.selectbox("Empresa Destinatária", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"], key="doc_emp")
            categoria = st.selectbox("Tipo de Documento (ISO 19650)", [
                "BIM Mandate", "BEP", "MIDP", "OIR", "AIR", "PIR", "EIR", "Geral"
            ])
            t_doc = st.text_input("Título do Documento (Ex: Plano de Execução BIM - Revisão A)")
            s_doc = st.text_input("Subtítulo / Descrição (Ex: Versão preliminar para homologação)")
            arq = st.file_uploader("Ficheiro", type=["pdf", "xlsx", "docx", "zip"])
            
            if st.button("Disponibilizar Entregável"):
                if arq and t_doc:
                    b64_arq = base64.b64encode(arq.read()).decode("utf-8")
                    novo_d = {
                        "categoria": categoria,
                        "titulo": t_doc,
                        "subtitulo": s_doc,
                        "nome_arquivo": arq.name,
                        "data_envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "conteudo_b64": b64_arq
                    }
                    DADOS["empresas"][emp_d].setdefault("documentos", []).append(novo_d)
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success("Documento publicado com sucesso!")
                        st.rerun()

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
        icone_marca_html = '<div style="width: 36px; height: 36px; background: #0284c7; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1rem; color: #fff;">JE</div>'

    html_header_side = f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-top: 8px;">
            {icone_marca_html}
            <div>
                <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: 0.04em; color: #f8fafc;">BIM INSIGHT</div>
                <div style="font-size: 0.7rem; color: #64748b;">Acompanhamento Estratégico</div>
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

# CABEÇALHO EXECUTIVO
html_topo_exec = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
        <div>
            <h1 style="font-size: 1.75rem; font-weight: 800; color: #f8fafc; margin: 0;">{nome_empresa}</h1>
            <p style="font-size: 0.92rem; color: #38bdf8; margin: 3px 0 0 0; font-weight: 600;">Visão Estratégica BIM</p>
        </div>
        <div style="text-align: right; color: #64748b; font-size: 0.78rem; line-height: 1.4;">
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
                <span style="background: #0284c7; color: #ffffff; font-weight: 800; font-size: 0.85rem; padding: 4px 10px; border-radius: 6px;">{sigla}</span>
                <h2 style="font-size: 1.35rem; font-weight: 700; color: #f8fafc; margin: 0;">{nome_completo}</h2>
            </div>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 6px 0 0 0;">{descricao}</p>
        </div>
    """, unsafe_allow_html=True)

    # Cartões informativos de enquadramento
    c1, c2 = st.columns([1.8, 1.2])
    with c1:
        st.markdown(f"""
            <div class="swot-card" style="border-left: 3px solid #38bdf8;">
                <div class="swot-title" style="color: #38bdf8;">📌 Âmbito & Diretrizes de Aplicação</div>
                <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6;">
                    {objetivos}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="swot-card" style="border-left: 3px solid #10b981;">
                <div class="swot-title" style="color: #34d399;">📐 Referência Normativa</div>
                <div style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6;">
                    <b>Padrão:</b> {norma_ref}<br>
                    <b>Governança:</b> Gestão da Informação em BIM<br>
                    <b>Responsável:</b> Consultoria JE BIM Management
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown(f"### 📄 Documentos & Entregáveis Homologados ({sigla})")

    # Filtra os documentos associados a esta sigla/categoria
    docs_categoria = [d for d in documentos if d.get("categoria") == sigla or sigla in d.get("titulo", "").upper()]

    if not docs_categoria:
        st.markdown(f"""
            <div class="doc-box" style="text-align: center; padding: 30px 20px;">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">📑</div>
                <div style="font-weight: 700; font-size: 1rem; color: #f1f5f9;">Documento em Fase de Estruturação / Homologação</div>
                <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">
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
                        <div style="font-weight: 700; font-size: 0.98rem; color: #f1f5f9;">📄 {t_doc}</div>
                        <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 3px;">{s_doc}</div>
                        <div style="font-size: 0.74rem; color: #64748b; margin-top: 4px;">
                            <span style="background: #162438; padding: 2px 8px; border-radius: 4px; color: #38bdf8;">Homologado</span>
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
            st.markdown("<div style='border-bottom: 1px solid #142033; margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# CONTEÚDO: VISÃO GERAL (DASHBOARD COMPLETO)
# -------------------------------------------------------------
if menu_selecionado == "Visão Geral":
    tem_avaliacao = len(avaliacoes) > 0
    ult_av = avaliacoes[-1] if tem_avaliacao else {}
    
    score_val = ult_av.get("media_global", 0.0)
    ciclo_atual_nome = ult_av.get("ciclo", "Ciclo 1")
    data_atual_fmt = ult_av.get("data", datetime.today().strftime("%Y-%m-%d"))
    try:
        data_atual_exib = datetime.strptime(data_atual_fmt, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        data_atual_exib = data_atual_fmt
    
    if score_val == 0.0 or not tem_avaliacao:
        kpi_maturidade_txt = "Em avaliação"
        kpi_maturidade_sub = f"{ciclo_atual_nome} • {data_atual_exib}"
    else:
        kpi_maturidade_txt = f"{score_val} pts"
        kpi_maturidade_sub = f"Média ponderada • {ciclo_atual_nome}"

    nivel_val = ult_av.get("nivel", "Ad-Hoc / Inicial")
    total_ciclos = len(avaliacoes)

    # 1. CARDS KPIS
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
    with c_kpi1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⏱️ Índice de Maturidade</div>
                <div class="metric-value">{kpi_maturidade_txt}</div>
                <div class="metric-sub">{kpi_maturidade_sub}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c_kpi2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📚 Nível de Maturidade</div>
                <div class="metric-value">{nivel_val}</div>
                <div class="metric-sub">Avaliação estratégica inicial</div>
            </div>
        """, unsafe_allow_html=True)

    with c_kpi3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🔄 Ciclo Atual</div>
                <div class="metric-value">{ciclo_atual_nome}</div>
                <div class="metric-sub">Início da jornada de transformação</div>
            </div>
        """, unsafe_allow_html=True)

    with c_kpi4:
        txt_ciclos = 'ciclo' if total_ciclos == 1 else 'ciclos'
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📋 Acompanhamento</div>
                <div class="metric-value">{total_ciclos} {txt_ciclos}</div>
                <div class="metric-sub">Ciclos de auditoria registados</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 2. GRÁFICOS POWER BI (RADAR + EVOLUÇÃO)
    col_radar, col_evol = st.columns([1, 1])

    with col_radar:
        st.markdown("""
            <div class="chart-header">
                <h3>Equilíbrio de Competências</h3>
                <p>Radar de Competências e Capacidade BIM</p>
            </div>
        """, unsafe_allow_html=True)
        
        cats = ['Tecnologia', 'Processos', 'Pessoas', 'Gestão', 'Contratos', 'Produtos', 'Projetos', 'Estratégia']
        
        if tem_avaliacao:
            val_atual = [
                ult_av.get('software', 10), ult_av.get('processos', 10),
                ult_av.get('pessoas', 10), ult_av.get('gestao', 10),
                ult_av.get('contratos', 10), ult_av.get('produtos', 10),
                ult_av.get('projetos', 10), ult_av.get('estrategia', 10)
            ]
        else:
            val_atual = [10, 10, 10, 10, 10, 10, 10, 10]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=val_atual,
            theta=cats,
            fill='toself',
            fillcolor='rgba(2, 132, 199, 0.25)',
            name=ciclo_atual_nome,
            line=dict(color='#0284c7', width=2),
            marker=dict(size=5, color='#38bdf8')
        ))
        
        fig_r.update_layout(
            template="plotly_dark",
            polar=dict(
                bgcolor='rgba(10, 18, 32, 0.4)',
                radialaxis=dict(
                    visible=True, 
                    range=[0, 40], 
                    gridcolor='#1e293b', 
                    linecolor='#1e293b',
                    tickfont=dict(size=8, color='#64748b')
                ),
                angularaxis=dict(
                    gridcolor='#1e293b', 
                    linecolor='#1e293b',
                    tickfont=dict(size=10, color='#94a3b8')
                )
            ),
            showlegend=False,
            height=280,
            margin=dict(l=35, r=35, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_r, use_container_width=True)

        insights_lista = ult_av.get("insights", [
            "Destaque para a competência em Tecnologia, com melhor desempenho no ciclo atual.",
            "Oportunidade de estruturação nas competências de Pessoas e Gestão de Processos.",
            "Equilíbrio geral em fase de desenvolvimento, com espaço para consolidação contínua."
        ])
        
        st.markdown(f"""
            <div class="insight-box">
                <div style="font-weight: 700; font-size: 0.85rem; color: #38bdf8; margin-bottom: 8px;">🎯 Principais Insights</div>
                <div class="insight-item">• {insights_lista[0]}</div>
                <div class="insight-item">• {insights_lista[1]}</div>
                <div class="insight-item">• {insights_lista[2]}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_evol:
        st.markdown("""
            <div class="chart-header">
                <h3>Evolução da Transformação BIM</h3>
                <p>Acompanhamento progressivo dos ciclos de avaliação</p>
            </div>
        """, unsafe_allow_html=True)

        nomes_ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4"]
        valores_reais = [av.get("media_global", 0.0) for av in avaliacoes]
        
        while len(valores_reais) < 4:
            valores_reais.append(None)

        valores_meta = [5.0, 15.0, 25.0, 35.0]

        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(
            x=nomes_ciclos,
            y=valores_meta,
            mode='lines',
            name='Meta Estratégica',
            line=dict(color='#475569', dash='dash', width=1.5)
        ))
        fig_l.add_trace(go.Scatter(
            x=nomes_ciclos,
            y=valores_reais,
            mode='lines+markers',
            name='Índice Medido',
            line=dict(color='#0284c7', width=3),
            marker=dict(size=8, color='#38bdf8', line=dict(color='#ffffff', width=1.5))
        ))

        fig_l.update_layout(
            template="plotly_dark",
            yaxis=dict(range=[0, 42], gridcolor='#172338', tickfont=dict(color='#64748b', size=9)),
            xaxis=dict(gridcolor='#172338', tickfont=dict(color='#94a3b8', size=10)),
            height=280,
            margin=dict(l=30, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9, color='#94a3b8'))
        )
        st.plotly_chart(fig_l, use_container_width=True)

        st.markdown("""
            <div class="stepper-container">
                <div class="step-item">
                    <div class="step-badge step-badge-active">1</div>
                    <div class="step-name">Ciclo 1</div>
                    <div class="step-status">Start</div>
                </div>
                <div style="flex: 1; height: 1px; background: #1e293b; margin-top: -12px;"></div>
                <div class="step-item">
                    <div class="step-badge step-badge-inactive">2</div>
                    <div class="step-name">Ciclo 2</div>
                    <div class="step-status">Em andamento</div>
                </div>
                <div style="flex: 1; height: 1px; background: #1e293b; margin-top: -12px;"></div>
                <div class="step-item">
                    <div class="step-badge step-badge-inactive">3</div>
                    <div class="step-name">Ciclo 3</div>
                    <div class="step-status">Planeado</div>
                </div>
                <div style="flex: 1; height: 1px; background: #1e293b; margin-top: -12px;"></div>
                <div class="step-item">
                    <div class="step-badge step-badge-inactive">4</div>
                    <div class="step-name">Ciclo 4</div>
                    <div class="step-status">Futuro</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 3. IDENTIDADE ESTRATÉGICA CORPORATIVA
    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="margin-bottom: 14px;">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 0;">🎯 Identidade Estratégica Corporativa</h3>
            <p style="font-size: 0.82rem; color: #64748b; margin: 2px 0 0 0;">Diretrizes fundamentais para orientar a transformação digital e os padrões de entrega</p>
        </div>
    """, unsafe_allow_html=True)

    col_m, col_v, col_val = st.columns(3)
    with col_m:
        st.markdown("""
            <div class="metric-card" style="min-height: 250px; border-top: 3px solid #0284c7;">
                <div style="font-size: 1.2rem; margin-bottom: 8px;">🎯</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc; margin-bottom: 8px;">Missão</div>
                <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                    Desenvolver projetos integrados e gestão técnica com excelência, transformando necessidades espaciais e operacionais em soluções arquitetónicas eficientes, sustentáveis e tecnologicamente sólidas.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_v:
        st.markdown("""
            <div class="metric-card" style="min-height: 250px; border-top: 3px solid #38bdf8;">
                <div style="font-size: 1.2rem; margin-bottom: 8px;">🔭</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc; margin-bottom: 8px;">Visão</div>
                <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                    Consolidar-se como referência regional em maturidade digital e metodologia BIM, garantindo tomadas de decisão antecipadas, previsibilidade de custo/obra e entregáveis de alto padrão construtivo.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_val:
        st.markdown("""
            <div class="metric-card" style="min-height: 250px; border-top: 3px solid #10b981;">
                <div style="font-size: 1.2rem; margin-bottom: 8px;">💎</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc; margin-bottom: 8px;">Valores</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.6;">
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
            <h3 style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 0;">📊 Matriz SWOT da Transformação BIM</h3>
            <p style="font-size: 0.82rem; color: #64748b; margin: 2px 0 0 0;">Mapeamento de forças internas e dinâmica externa de mercado</p>
        </div>
    """, unsafe_allow_html=True)

    c_swot1, c_swot2 = st.columns(2)
    with c_swot1:
        st.markdown("""
            <div class="swot-card" style="border-left: 4px solid #10b981; margin-bottom: 12px;">
                <div class="swot-title" style="color: #34d399;">🟢 Forças (Strengths)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
                    • Empenho da liderança na consolidação dos fluxos digitais.<br>
                    • Reputação consolidada em arquitetura de alto padrão e detalhe executivo.<br>
                    • Disponibilidade da equipa técnica para integrar novos softwares e rotinas BIM.
                </div>
            </div>
            <div class="swot-card" style="border-left: 4px solid #f59e0b;">
                <div class="swot-title" style="color: #fbbf24;">🟡 Fraquezas (Weaknesses)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
                    • Necessidade de padronização nas famílias e modelos paramétricos.<br>
                    • Processos de deteção de colisões (Clash Detection) em fase inicial de estruturação.<br>
                    • Documentação de processos (BEP interno) em consolidação.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_swot2:
        st.markdown("""
            <div class="swot-card" style="border-left: 4px solid #38bdf8; margin-bottom: 12px;">
                <div class="swot-title" style="color: #60a5fa;">🔵 Oportunidades (Opportunities)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
                    • Posicionamento de destaque perante clientes e concursos que exigem BIM.<br>
                    • Redução mensurável de retrabalho no estaleiro via coordenação 3D/4D.<br>
                    • Oferta de serviços consultivos integrados e compatibilização avançada.
                </div>
            </div>
            <div class="swot-card" style="border-left: 4px solid #ef4444;">
                <div class="swot-title" style="color: #f87171;">🔴 Ameaças (Threats)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
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
        except Exception:
            return ""
    return ""

icone_favicon = "JE.png" if os.path.exists("JE.png") else "🔷"

st.set_page_config(
    page_title="BIM INSIGHT | Portal de Gestão",
    page_icon=icone_favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# TELA DE LOGIN
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
                background: rgba(7, 13, 24, 0.82);
                backdrop-filter: blur(4px);
                z-index: -1;
            }
            div[data-testid="stForm"] {
                background: rgba(10, 18, 32, 0.85) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6) !important;
                border-radius: 14px !important;
                padding: 24px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    html_video = f"""
        <div class="bg-video-container">
            <video class="bg-video" autoplay loop muted playsinline>
                <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
            </video>
        </div>
        <div class="bg-overlay"></div>
    """
    st.markdown(html_video, unsafe_allow_html=True)

    col_logo, _ = st.columns([1, 4])
    with col_logo:
        if b64_logo:
            html_logo = f"""
                <div style="margin-top: 12px; margin-left: 10px; width: 140px;">
                    <img src="data:image/png;base64,{b64_logo}" style="width: 100%; filter: invert(1) brightness(1.2);">
                </div>
            """
            st.markdown(html_logo, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
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
# CSS DO PORTAL INTERNO
# -------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #070d18;
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background-color: #0a1120 !important;
        border-right: 1px solid #1e293b !important;
    }
    .metric-card {
        background: linear-gradient(145deg, #0d1728, #09111e);
        border: 1px solid #1e2d42;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.03em;
        margin-bottom: 6px;
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
    .chart-header h3 {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
    }
    .chart-header p {
        font-size: 0.8rem;
        color: #64748b;
        margin: 2px 0 10px 0;
    }
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
        margin-bottom: 8px;
        line-height: 1.4;
    }
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
    .swot-card {
        background: #0a1322;
        border: 1px solid #162438;
        border-radius: 10px;
        padding: 16px;
        height: 100%;
    }
    .swot-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# PAINEL DO ADMINISTRADOR
# -------------------------------------------------------------
if st.session_state["tipo_usuario"] == "admin":
    st.sidebar.markdown("**Admin Conectado**")
    if st.sidebar.button("Encerrar Sessão", use_container_width=True):
        logout()

    st.title("Painel de Gestão da Consultoria | Admin")
    tab_cad, tab_av, tab_doc, tab_del = st.tabs([
        "➕ Cadastrar Empresa", "📝 Registrar Ciclo", "📁 Subir Documentos", "🗑️ Excluir Empresa"
    ])
    
    with tab_cad:
        st.subheader("Cadastrar Nova Organização")
        with st.form("form_cad_emp"):
            id_e = st.text_input("ID único (ex: fz_arquitetura)").strip().lower()
            nome_e = st.text_input("Nome Corporativo da Empresa (ex: FZ Arquitetura, Projeto e Gerenciamento)")
            senha_e = st.text_input("Senha de Acesso", type="password")
            if st.form_submit_button("Cadastrar Empresa"):
                if id_e and nome_e and senha_e:
                    DADOS.setdefault("empresas", {})[id_e] = {
                        "nome": nome_e, "senha": senha_e, "avaliacoes": [], "documentos": []
                    }
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success("Empresa cadastrada com sucesso!")
                        st.rerun()

    with tab_av:
        st.subheader("Lançar Diagnóstico / Ciclo de Maturidade")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_sel = st.selectbox("Selecione a Organização", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"])
            with st.form("form_reg_av"):
                c1, c2 = st.columns(2)
                ciclo_txt = c1.text_input("Identificação do Ciclo", value="Ciclo 1 - Start")
                data_av = c2.date_input("Data do Ciclo", value=datetime.today())
                
                st.caption("Pontuações da Matriz Succar (0 = Inicial a 40 = Otimizado)")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown("**Tecnologia & Estratégia**")
                    p_soft = st.slider("Tecnologia / Software", 0, 40, 20, 10)
                    p_hard = st.slider("Infraestrutura / Hardware", 0, 40, 20, 10)
                    p_est = st.slider("Estratégia BIM", 0, 40, 10, 10)
                with col_b:
                    st.markdown("**Processos & Pessoas**")
                    p_proc = st.slider("Processos / Fluxos", 0, 40, 15, 10)
                    p_pess = st.slider("Pessoas / Competências", 0, 40, 10, 10)
                    p_gest = st.slider("Gestão & Liderança", 0, 40, 10, 10)
                with col_c:
                    st.markdown("**Políticas & Contratos**")
                    p_cont = st.slider("Contratos & Políticas", 0, 40, 10, 10)
                    p_prod = st.slider("Produtos & Entregáveis", 0, 40, 15, 10)
                    p_proj = st.slider("Projetos / Colaboração", 0, 40, 10, 10)

                st.markdown("**Principais Insights Estratégicos**")
                insight_1 = st.text_input("Insight 1", value="Destaque para a competência em Tecnologia, com melhor desempenho no ciclo atual.")
                insight_2 = st.text_input("Insight 2", value="Oportunidade de evolução nas competências de Pessoas e Gestão.")
                insight_3 = st.text_input("Insight 3", value="Equilíbrio geral com espaço para estruturação progressiva em todas as áreas.")

                if st.form_submit_button("Gravar Ciclo de Avaliação"):
                    pontos = [p_soft, p_hard, p_est, p_proc, p_pess, p_gest, p_cont, p_prod, p_proj]
                    media = sum(pontos) / len(pontos)
                    
                    nivel = "Ad-Hoc / Inicial"
                    if media >= 35: nivel = "Otimizado"
                    elif media >= 25: nivel = "Integrado"
                    elif media >= 15: nivel = "Gerenciado"
                    elif media >= 5: nivel = "Definido"

                    nova_av = {
                        "ciclo": ciclo_txt,
                        "data": str(data_av),
                        "software": p_soft, "hardware": p_hard, "estrategia": p_est,
                        "processos": p_proc, "pessoas": p_pess, "gestao": p_gest,
                        "contratos": p_cont, "produtos": p_prod, "projetos": p_proj,
                        "media_global": round(media, 1),
                        "nivel": nivel,
                        "insights": [insight_1, insight_2, insight_3]
                    }
                    DADOS["empresas"][emp_sel]["avaliacoes"].append(nova_av)
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success("Avaliação gravada com sucesso!")
                        st.rerun()

    with tab_doc:
        st.subheader("Subir Entregável para a Organização")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_d = st.selectbox("Empresa Destinatária", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"], key="doc_emp")
            t_doc = st.text_input("Título do Documento")
            s_doc = st.text_input("Subtítulo / Descrição")
            categoria = st.selectbox("Categoria", ["Relatórios", "Diagnósticos", "Planos", "Outros"])
            arq = st.file_uploader("Arquivo", type=["pdf", "xlsx", "docx", "zip"])
            
            if st.button("Disponibilizar Entregável"):
                if arq and t_doc:
                    b64_arq = base64.b64encode(arq.read()).decode("utf-8")
                    novo_d = {
                        "titulo": t_doc,
                        "subtitulo": s_doc,
                        "categoria": categoria,
                        "nome_arquivo": arq.name,
                        "data_envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "conteudo_b64": b64_arq
                    }
                    DADOS["empresas"][emp_d].setdefault("documentos", []).append(novo_d)
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success("Documento publicado!")
                        st.rerun()

    with tab_del:
        st.subheader("Remover Empresa")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_rm = st.selectbox("Empresa a ser excluída", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"], key="rm_emp")
            if st.button("Confirmar Exclusão Definitiva", type="primary"):
                del DADOS["empresas"][emp_rm]
                if salvar_dados(DADOS, SHA_ATUAL):
                    st.success("Empresa excluída!")
                    st.rerun()
    st.stop()

# -------------------------------------------------------------
# PORTAL DO CLIENTE
# -------------------------------------------------------------
empresa_id = st.session_state["usuario_logado"]
empresa_dados = DADOS.get("empresas", {}).get(empresa_id, {})
nome_empresa = empresa_dados.get("nome", "Organização")
avaliacoes = empresa_dados.get("avaliacoes", [])
documentos = empresa_dados.get("documentos", [])

b64_je_icon = get_base64_file("JE.png")

with st.sidebar:
    if b64_je_icon:
        icone_marca_html = f'<img src="data:image/png;base64,{b64_je_icon}" style="width: 38px; height: 38px; object-fit: contain; border-radius: 4px; filter: brightness(1.2);">'
    else:
        icone_marca_html = '<div style="width: 36px; height: 36px; background: #0284c7; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1rem; color: #fff;">JE</div>'

    html_header_side = f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-top: 8px;">
            {icone_marca_html}
            <div>
                <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: 0.04em; color: #f8fafc;">BIM INSIGHT</div>
                <div style="font-size: 0.7rem; color: #64748b;">Acompanhamento Estratégico</div>
            </div>
        </div>
    """
    st.markdown(html_header_side, unsafe_allow_html=True)
    
    menu_selecionado = st.radio(
        "Navegação",
        ["Visão Geral", "Entregáveis"],
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
    primeiro_nome = nome_empresa.split()[0] if nome_empresa else "Cliente"
    st.caption(f"Conectado como: **{primeiro_nome}**")
    if st.button("Encerrar Sessão", use_container_width=True):
        logout()

html_topo_exec = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
        <div>
            <h1 style="font-size: 1.75rem; font-weight: 800; color: #f8fafc; margin: 0;">{nome_empresa}</h1>
            <p style="font-size: 0.92rem; color: #38bdf8; margin: 3px 0 0 0; font-weight: 600;">Visão Estratégica BIM</p>
        </div>
        <div style="text-align: right; color: #64748b; font-size: 0.78rem; line-height: 1.4;">
            Mais eficiência.<br>Melhores decisões.<br>Resultados sustentáveis.
        </div>
    </div>
"""
st.markdown(html_topo_exec, unsafe_allow_html=True)

# -------------------------------------------------------------
# CONTEÚDO: VISÃO GERAL
# -------------------------------------------------------------
if menu_selecionado == "Visão Geral":
    tem_avaliacao = len(avaliacoes) > 0
    ult_av = avaliacoes[-1] if tem_avaliacao else {}
    
    score_val = ult_av.get("media_global", 0.0)
    ciclo_atual_nome = ult_av.get("ciclo", "Ciclo 1")
    data_atual_fmt = ult_av.get("data", datetime.today().strftime("%Y-%m-%d"))
    try:
        data_atual_exib = datetime.strptime(data_atual_fmt, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        data_atual_exib = data_atual_fmt
    
    if score_val == 0.0 or not tem_avaliacao:
        kpi_maturidade_txt = "Em avaliação"
        kpi_maturidade_sub = f"{ciclo_atual_nome} • {data_atual_exib}"
    else:
        kpi_maturidade_txt = f"{score_val} pts"
        kpi_maturidade_sub = f"Média ponderada • {ciclo_atual_nome}"

    nivel_val = ult_av.get("nivel", "Ad-Hoc / Inicial")
    total_ciclos = len(avaliacoes)

    # 1. CARDS KPIS
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
    with c_kpi1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⏱️ Índice de Maturidade</div>
                <div class="metric-value">{kpi_maturidade_txt}</div>
                <div class="metric-sub">{kpi_maturidade_sub}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c_kpi2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📚 Nível de Maturidade</div>
                <div class="metric-value">{nivel_val}</div>
                <div class="metric-sub">Avaliação estratégica inicial</div>
            </div>
        """, unsafe_allow_html=True)

    with c_kpi3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🔄 Ciclo Atual</div>
                <div class="metric-value">{ciclo_atual_nome}</div>
                <div class="metric-sub">Início da jornada de transformação</div>
            </div>
        """, unsafe_allow_html=True)

    with c_kpi4:
        txt_ciclos = 'ciclo' if total_ciclos == 1 else 'ciclos'
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📋 Acompanhamento</div>
                <div class="metric-value">{total_ciclos} {txt_ciclos}</div>
                <div class="metric-sub">Ciclos de auditoria registrados</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 2. GRÁFICOS (RADAR + EVOLUÇÃO)
    col_radar, col_evol = st.columns([1, 1])

    with col_radar:
        st.markdown("""
            <div class="chart-header">
                <h3>Equilíbrio de Competências</h3>
                <p>Radar de Competências e Capacidade BIM</p>
            </div>
        """, unsafe_allow_html=True)
        
        cats = ['Tecnologia', 'Processos', 'Pessoas', 'Gestão', 'Contratos', 'Produtos', 'Projetos', 'Estratégia']
        
        if tem_avaliacao:
            val_atual = [
                ult_av.get('software', 10), ult_av.get('processos', 10),
                ult_av.get('pessoas', 10), ult_av.get('gestao', 10),
                ult_av.get('contratos', 10), ult_av.get('produtos', 10),
                ult_av.get('projetos', 10), ult_av.get('estrategia', 10)
            ]
        else:
            val_atual = [10, 10, 10, 10, 10, 10, 10, 10]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=val_atual,
            theta=cats,
            fill='toself',
            fillcolor='rgba(2, 132, 199, 0.25)',
            name=ciclo_atual_nome,
            line=dict(color='#0284c7', width=2),
            marker=dict(size=5, color='#38bdf8')
        ))
        
        fig_r.update_layout(
            template="plotly_dark",
            polar=dict(
                bgcolor='rgba(10, 18, 32, 0.4)',
                radialaxis=dict(
                    visible=True, 
                    range=[0, 40], 
                    gridcolor='#1e293b', 
                    linecolor='#1e293b',
                    tickfont=dict(size=8, color='#64748b')
                ),
                angularaxis=dict(
                    gridcolor='#1e293b', 
                    linecolor='#1e293b',
                    tickfont=dict(size=10, color='#94a3b8')
                )
            ),
            showlegend=False,
            height=280,
            margin=dict(l=35, r=35, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_r, use_container_width=True)

        insights_lista = ult_av.get("insights", [
            "Destaque para a competência em Tecnologia, com melhor desempenho no ciclo atual.",
            "Oportunidade de estruturação nas competências de Pessoas e Gestão de Processos.",
            "Equilíbrio geral em fase de desenvolvimento, com espaço para consolidação contínua."
        ])
        
        html_insights = f"""
            <div class="insight-box">
                <div style="font-weight: 700; font-size: 0.85rem; color: #38bdf8; margin-bottom: 8px;">🎯 Principais Insights</div>
                <div class="insight-item">• {insights_lista[0]}</div>
                <div class="insight-item">• {insights_lista[1]}</div>
                <div class="insight-item">• {insights_lista[2]}</div>
            </div>
        """
        st.markdown(html_insights, unsafe_allow_html=True)

    with col_evol:
        st.markdown("""
            <div class="chart-header">
                <h3>Evolução da Transformação BIM</h3>
                <p>Acompanhamento progressivo dos ciclos de avaliação</p>
            </div>
        """, unsafe_allow_html=True)

        nomes_ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4"]
        valores_reais = [av.get("media_global", 0.0) for av in avaliacoes]
        
        while len(valores_reais) < 4:
            valores_reais.append(None)

        valores_meta = [5.0, 15.0, 25.0, 35.0]

        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(
            x=nomes_ciclos,
            y=valores_meta,
            mode='lines',
            name='Meta Estratégica',
            line=dict(color='#475569', dash='dash', width=1.5)
        ))
        fig_l.add_trace(go.Scatter(
            x=nomes_ciclos,
            y=valores_reais,
            mode='lines+markers',
            name='Índice Medido',
            line=dict(color='#0284c7', width=3),
            marker=dict(size=8, color='#38bdf8', line=dict(color='#ffffff', width=1.5))
        ))

        fig_l.update_layout(
            template="plotly_dark",
            yaxis=dict(range=[0, 42], gridcolor='#172338', tickfont=dict(color='#64748b', size=9)),
            xaxis=dict(gridcolor='#172338', tickfont=dict(color='#94a3b8', size=10)),
            height=280,
            margin=dict(l=30, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9, color='#94a3b8'))
        )
        st.plotly_chart(fig_l, use_container_width=True)

        st.markdown("""
            <div class="stepper-container">
                <div class="step-item">
                    <div class="step-badge step-badge-active">1</div>
                    <div class="step-name">Ciclo 1</div>
                    <div class="step-status">Start</div>
                </div>
                <div style="flex: 1; height: 1px; background: #1e293b; margin-top: -12px;"></div>
                <div class="step-item">
                    <div class="step-badge step-badge-inactive">2</div>
                    <div class="step-name">Ciclo 2</div>
                    <div class="step-status">Em andamento</div>
                </div>
                <div style="flex: 1; height: 1px; background: #1e293b; margin-top: -12px;"></div>
                <div class="step-item">
                    <div class="step-badge step-badge-inactive">3</div>
                    <div class="step-name">Ciclo 3</div>
                    <div class="step-status">Planejado</div>
                </div>
                <div style="flex: 1; height: 1px; background: #1e293b; margin-top: -12px;"></div>
                <div class="step-item">
                    <div class="step-badge step-badge-inactive">4</div>
                    <div class="step-name">Ciclo 4</div>
                    <div class="step-status">Futuro</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 3. IDENTIDADE ESTRATÉGICA
    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="margin-bottom: 14px;">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 0;">🎯 Identidade Estratégica Corporativa</h3>
            <p style="font-size: 0.82rem; color: #64748b; margin: 2px 0 0 0;">Diretrizes fundamentais para guiar a transformação digital e os padrões de entrega</p>
        </div>
    """, unsafe_allow_html=True)

    col_m, col_v, col_val = st.columns(3)
    with col_m:
        st.markdown("""
            <div class="metric-card" style="min-height: 250px; border-top: 3px solid #0284c7;">
                <div style="font-size: 1.2rem; margin-bottom: 8px;">🎯</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc; margin-bottom: 8px;">Missão</div>
                <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                    Desenvolver projetos integrados e gestão técnica com excelência, transformando necessidades espaciais e operacionais em soluções arquitetônicas eficientes, sustentáveis e tecnologicamente sólidas.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_v:
        st.markdown("""
            <div class="metric-card" style="min-height: 250px; border-top: 3px solid #38bdf8;">
                <div style="font-size: 1.2rem; margin-bottom: 8px;">🔭</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc; margin-bottom: 8px;">Visão</div>
                <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                    Consolidar-se como referência regional em maturidade digital e metodologia BIM, garantindo tomadas de decisão antecipadas, previsibilidade de custo/obra e entregáveis de alto padrão construtivo.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_val:
        st.markdown("""
            <div class="metric-card" style="min-height: 250px; border-top: 3px solid #10b981;">
                <div style="font-size: 1.2rem; margin-bottom: 8px;">💎</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #f8fafc; margin-bottom: 8px;">Valores</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.6;">
                    • <b>Rigor Técnico</b>: Modelagem precisa e consistência na informação.<br>
                    • <b>Colaboração Aberta</b>: Integração ativa com parceiros e clientes.<br>
                    • <b>Inovação Contínua</b>: Adoção prática das melhores diretrizes BIM.<br>
                    • <b>Sustentabilidade</b>: Redução de retrabalhos pela pré-construção virtual.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 4. ANÁLISE SWOT
    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="margin-bottom: 14px;">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 0;">📊 Matriz SWOT da Transformação BIM</h3>
            <p style="font-size: 0.82rem; color: #64748b; margin: 2px 0 0 0;">Mapeamento de forças internas e dinâmica externa de mercado</p>
        </div>
    """, unsafe_allow_html=True)

    c_swot1, c_swot2 = st.columns(2)
    with c_swot1:
        st.markdown("""
            <div class="swot-card" style="border-left: 4px solid #10b981; margin-bottom: 12px;">
                <div class="swot-title" style="color: #34d399;">🟢 Forças (Strengths)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
                    • Engajamento da liderança na consolidação dos fluxos digitais.<br>
                    • Forte reputação em arquitetura de alto padrão e detalhamento executivo.<br>
                    • Abertura da equipe técnica para absorver novos softwares e rotinas BIM.
                </div>
            </div>
            <div class="swot-card" style="border-left: 4px solid #f59e0b;">
                <div class="swot-title" style="color: #fbbf24;">🟡 Fraquezas (Weaknesses)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
                    • Necessidade de padronização nas famílias e templates paramétricos.<br>
                    • Processos de checagem de interferências (Clash Detection) ainda em estruturação inicial.<br>
                    • Documentação de processos (BEP interno) em fase de amadurecimento.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_swot2:
        st.markdown("""
            <div class="swot-card" style="border-left: 4px solid #38bdf8; margin-bottom: 12px;">
                <div class="swot-title" style="color: #60a5fa;">🔵 Oportunidades (Opportunities)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
                    • Posicionamento de destaque em editais e clientes corporativos que exigem BIM.<br>
                    • Redução mensurável de retrabalhos em canteiro através da coordenação 3D/4D.<br>
                    • Oferta de serviços consultivos integrados e compatibilização avançada.
                </div>
            </div>
            <div class="swot-card" style="border-left: 4px solid #ef4444;">
                <div class="swot-title" style="color: #f87171;">🔴 Ameaças (Threats)</div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.5;">
                    • Projetistas parceiros e complementares trabalhando apenas em CAD 2D tradicional.<br>
                    • Prazos agressivos de mercado que podem pressionar o tempo inicial de modelagem.<br>
                    • Custos e atualização contínua de licenças e estações de trabalho de alta performance.
                </div>
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# CONTEÚDO: ENTREGÁVEIS
# -------------------------------------------------------------
elif menu_selecionado == "Entregáveis":
    total_docs = len(documentos)
    txt_docs = 'documento disponível' if total_docs == 1 else 'documentos disponíveis'
    
    html_entregaveis_header = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
            <div>
                <h2 style="font-size: 1.4rem; font-weight: 700; color: #f8fafc; margin: 0;">📁 Central de Entregáveis</h2>
                <p style="font-size: 0.85rem; color: #64748b; margin: 4px 0 0 0;">Repositório homologado dos documentos técnicos, relatórios de diagnóstico e diretrizes</p>
            </div>
            <div style="font-size: 0.84rem; color: #94a3b8; background: #0e1726; padding: 6px 14px; border-radius: 20px; border: 1px solid #1e2d42;">
                📄 <b>{total_docs}</b> {txt_docs}
            </div>
        </div>
    """
    st.markdown(html_entregaveis_header, unsafe_allow_html=True)

    filtro_cat = st.radio(
        "Filtros de Categoria",
        ["Todos", "Relatórios", "Diagnósticos", "Planos", "Outros"],
        horizontal=True,
        label_visibility="collapsed"
    )

    docs_filtrados = documentos
    if filtro_cat != "Todos":
        docs_filtrados = [d for d in documentos if d.get("categoria", "Relatórios") == filtro_cat]

    if not docs_filtrados:
        st.info("Nenhum entregável disponível para os critérios selecionados.")
    else:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        for doc in docs_filtrados:
            col_d1, col_d2 = st.columns([3.8, 1.2])
            with col_d1:
                t_doc = doc.get('titulo', 'Documento')
                s_doc = doc.get('subtitulo', doc.get('nome_arquivo', ''))
                cat_doc = doc.get('categoria', 'Relatório')
                dt_doc = doc.get('data_envio', '-')
                
                html_doc_item = f"""
                    <div style="padding: 8px 0;">
                        <div style="font-weight: 700; font-size: 0.98rem; color: #f1f5f9;">📄 {t_doc}</div>
                        <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 3px;">{s_doc}</div>
                        <div style="font-size: 0.74rem; color: #64748b; margin-top: 4px;">
                            <span style="background: #162438; padding: 2px 8px; border-radius: 4px; color: #38bdf8;">{cat_doc}</span>
                            &nbsp;•&nbsp; Disponibilizado em: {dt_doc}
                        </div>
                    </div>
                """
                st.markdown(html_doc_item, unsafe_allow_html=True)
            with col_d2:
                st.write("")
                bytes_bin = base64.b64decode(doc['conteudo_b64'])
                st.download_button(
                    label="⬇️ Baixar documento",
                    data=bytes_bin,
                    file_name=doc.get('nome_arquivo', 'documento.pdf'),
                    use_container_width=True,
                    key=f"dl_{doc.get('titulo', '')}_{doc.get('nome_arquivo', '')}"
                )
            st.markdown("<div style='border-bottom: 1px solid #142033; margin-bottom: 10px;'></div>", unsafe_allow_html=True)
