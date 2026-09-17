import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
import os
from datetime import datetime
from github import Github

# -------------------------------------------------------------
# FUNÇÃO AUXILIAR PARA ARQUIVOS EM BASE64
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
# CONFIGURAÇÃO DE PÁGINA
# -------------------------------------------------------------
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
# TELA DE LOGIN (BACKGROUND VÍDEO + GLASSMORPHISM)
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

    # Injeção de CSS para Vídeo Fullscreen e Glassmorphism
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
            /* Card do formulário estilo vidro escuro */
            div[data-testid="stForm"] {{
                background: rgba(15, 23, 42, 0.75) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
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
# PORTAL DO CLIENTE (BIM INSIGHT - VISÃO EXECUTIVA)
# -------------------------------------------------------------
empresa_id = st.session_state["usuario_logado"]
empresa_dados = DADOS.get("empresas", {}).get(empresa_id, {})
nome_empresa = empresa_dados.get("nome", "Organização")
avaliacoes = empresa_dados.get("avaliacoes", [])
documentos = empresa_dados.get("documentos", [])

b64_je_icon = get_base64_file("JE.png")

# BARRA LATERAL SIMPLIFICADA (APENAS VISÃO GERAL E ENTREGÁVEIS)
with st.sidebar:
    if b64_je_icon:
        icone_marca_html = f"""<img src="data:image/png;base64,{b64_je_icon}" style="width: 38px; height: 38px; object-fit: contain; border-radius: 4px; filter: brightness(1.2);">"""
    else:
        icone_marca_html = """<div style="width: 36px; height: 36px; background: #0284c7; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1rem; color: #fff;">JE</div>"""

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-top: 8px;">
            {icone_marca_html}
            <div>
                <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: 0.04em; color: #f8fafc;">BIM INSIGHT</div>
                <div style="font-size: 0.7rem; color: #64748b;">Acompanhamento Estratégico</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    menu_selecionado = st.radio(
        "Navegação",
        ["Visão Geral", "Entregáveis"],
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
    st.caption(f"Conectado como: **{nome_empresa.split()[0]}**")
    if st.button("Encerrar Sessão", use_container_width=True):
        logout()

# CABEÇALHO EXECUTIVO
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
        <div>
            <h1 style="font-size: 1.75rem; font-weight: 800; color: #f8fafc; margin: 0;">{nome_empresa}</h1>
            <p style="font-size: 0.92rem; color: #38bdf8; margin: 3px 0 0 0; font-weight: 600;">Visão Estratégica BIM</p>
        </div>
        <div style="text-align: right; color: #64748b; font-size: 0.78rem; line-height: 1.4;">
            Mais eficiência.<br>Melhores decisões.<br>Resultados sustentáveis.
        </div>
    </div>
""", unsafe_allow_html=True)

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

    # 1. LINHA DE CARDS KPIS
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
    with c_kpi1:
        st.markdown(f"""
