import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
from datetime import datetime
from github import Github

# -------------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA & TEMA ESCURO EXECUTIVO
# -------------------------------------------------------------
st.set_page_config(
    page_title="BIM INSIGHT | Portal de Gestão",
    page_icon="🔷",
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

                st.markdown("**Principais Insights Estratégicos (Exibidos ao Cliente)**")
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
            t_doc = st.text_input("Título do Documento (Ex: Revisão bibliográfica sistematizada sobre BIM)")
            s_doc = st.text_input("Subtítulo / Descrição (Ex: BIM Fundamentals - Tratado Técnico Consolidado)")
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

# BARRA LATERAL ORIENTADA AO CLIENTE
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 24px; padding-top: 8px;">
            <div style="width: 32px; height: 32px; background: #0284c7; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1rem; color: #fff;">🔷</div>
            <div>
                <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: 0.04em; color: #f8fafc;">BIM INSIGHT</div>
                <div style="font-size: 0.7rem; color: #64748b;">Acompanhamento Estratégico</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    menu_selecionado = st.radio(
        "Navegação",
        [
            "Visão Geral",
            "Diagnóstico",
            "Análise SWOT",
            "Evolução BIM",
            "Plano de Ação",
            "Entregáveis",
            "Documentos",
            "Histórico"
        ],
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
# CONTEÚDO DA ABA: VISÃO GERAL
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
    
    # Tratamento para ausência de nota ou nota 0
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
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📋 Acompanhamento</div>
                <div class="metric-value">{total_ciclos} {'ciclo' if total_ciclos == 1 else 'ciclos'}</div>
                <div class="metric-sub">Ciclos de auditoria registrados</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 2. GRÁFICOS EXECUTIVOS (RADAR + EVOLUÇÃO)
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

    # 3. CENTRAL DE DOCUMENTOS & ENTREGÁVEIS
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    total_docs = len(documentos)
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <h3 style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 0;">📁 Central de Entregáveis</h3>
                <p style="font-size: 0.82rem; color: #64748b; margin: 2px 0 0 0;">Documentos técnicos produzidos e homologados para sua organização</p>
            </div>
            <div style="font-size: 0.82rem; color: #94a3b8; background: #0e1726; padding: 6px 14px; border-radius: 20px; border: 1px solid #1e2d42;">
                📄 <b>{total_docs}</b> {'documento disponível' if total_docs == 1 else 'documentos disponíveis'}
            </div>
        </div>
    """, unsafe_allow_html=True)

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
        st.info("Nenhum documento disponível nesta categoria no momento.")
    else:
        for doc in docs_filtrados:
            col_d1, col_d2 = st.columns([3.8, 1.2])
            with col_d1:
                st.markdown(f"""
                    <div style="padding: 10px 0;">
                        <div style="font-weight: 700; font-size: 0.95rem; color: #f1f5f9;">📄 {doc['titulo']}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">{doc.get('subtitulo', doc['nome_arquivo'])}</div>
                        <div style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">Disponibilizado em: {doc.get('data_envio', '-')}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_d2:
                st.write("")
                bytes_bin = base64.b64decode(doc['conteudo_b64'])
                st.download_button(
                    label="⬇️ Baixar documento",
                    data=bytes_bin,
                    file_name=doc['nome_arquivo'],
                    use_container_width=True,
                    key=f"dl_{doc['titulo']}"
                )
            st.markdown("<div style='border-bottom: 1px solid #142033; margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# DEMAIS MÓDULOS DO MENU LATERAL
# -------------------------------------------------------------
elif menu_selecionado == "Diagnóstico":
    st.subheader("Diagnóstico Estratégico")
    st.write("Visão aprofundada dos eixos de Tecnologia, Processos e Políticas segundo o BIM Framework.")
    st.info("Módulo detalhado em elaboração pelo consultor responsável.")

elif menu_selecionado == "Análise SWOT":
    st.subheader("Matriz SWOT da Transformação BIM")
    st.write("Forças, Fraquezas, Oportunidades e Ameaças mapeadas no ambiente da organização.")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown("### 🟢 Forças (Strengths)")
        st.caption("• Engajamento da liderança executiva na digitalização dos fluxos.")
        st.markdown("### 🟡 Fraquezas (Weaknesses)")
        st.caption("• Necessidade de padronização nos templates e famílias de modelagem.")
    with c_s2:
        st.markdown("### 🔵 Oportunidades (Opportunities)")
        st.caption("• Diferenciação comercial perante clientes exigentes em BIM.")
        st.markdown("### 🔴 Ameaças (Threats)")
        st.caption("• Curva de aprendizado das equipes e interoperabilidade com projetistas parceiros.")

elif menu_selecionado == "Evolução BIM":
    st.subheader("Evolução Histórica & Metas")
    st.write("Linha do tempo consolidada e projeção para os próximos ciclos de auditoria.")

elif menu_selecionado == "Plano de Ação":
    st.subheader("Plano de Ação & Roadmap de Implementação")
    st.write("Acompanhamento das tarefas prioritárias, responsáveis e prazos estabelecidos.")

elif menu_selecionado in ["Entregáveis", "Documentos"]:
    st.subheader("Repositório Completo de Documentos")
    st.write("Acesse os arquivos técnicos na aba **Visão Geral** ou navegue pelo repositório corporativo.")

elif menu_selecionado == "Histórico":
    st.subheader("Histórico de Registros")
    if avaliacoes:
        st.dataframe(pd.DataFrame(avaliacoes)[["ciclo", "data", "media_global", "nivel"]], use_container_width=True)
    else:
        st.info("Nenhum histórico disponível.")
