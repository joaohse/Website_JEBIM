import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
from datetime import datetime
from github import Github

# Configuração da Página
st.set_page_config(
    page_title="Portal de Maturidade BIM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# INTEGRAÇÃO COM GITHUB (BANCO DE DADOS EM NUVEM)
# -------------------------------------------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_NAME = st.secrets.get("REPO_NAME", "") # Ex: "seu-usuario/seu-repositorio"
DATA_FILE_PATH = "dados.json"

@st.cache_data(ttl=5)
def carregar_dados():
    """Lê o arquivo dados.json diretamente do repositório GitHub"""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        conteudo = repo.get_contents(DATA_FILE_PATH)
        dados = json.loads(conteudo.decoded_content.decode("utf-8"))
        return dados, conteudo.sha
    except Exception as e:
        # Fallback local se estiver testando no computador sem secrets
        try:
            with open("dados.json", "r", encoding="utf-8") as f:
                return json.load(f), None
        except:
            return {"empresas": {}}, None

def salvar_dados(novos_dados, sha=None):
    """Atualiza o arquivo dados.json no GitHub via commit automático"""
    conteudo_str = json.dumps(novos_dados, indent=2, ensure_ascii=False)
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        if sha:
            repo.update_file(DATA_FILE_PATH, "Atualização de dados via Dashboard BIM", conteudo_str, sha)
        else:
            conteudo_atual = repo.get_contents(DATA_FILE_PATH)
            repo.update_file(DATA_FILE_PATH, "Atualização de dados via Dashboard BIM", conteudo_str, conteudo_atual.sha)
        st.cache_data.clear()
        return True
    except Exception as e:
        # Salva localmente se falhar a API
        with open("dados.json", "w", encoding="utf-8") as f:
            f.write(conteudo_str)
        st.cache_data.clear()
        return True

# -------------------------------------------------------------
# AUTENTICAÇÃO E SESSÃO
# -------------------------------------------------------------
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
if "tipo_usuario" not in st.session_state:
    st.session_state["tipo_usuario"] = None

DADOS, SHA_ATUAL = carregar_dados()
ADMIN_SENHA = st.secrets.get("ADMIN_SENHA", "admin123")

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
# BARRA LATERAL (MENU & PERFIL)
# -------------------------------------------------------------
st.sidebar.markdown(f"**Conectado como:** `{st.session_state['usuario_logado']}`")
if st.sidebar.button("Encerrar Sessão", use_container_width=True):
    logout()

# -------------------------------------------------------------
# VISÃO ADMIN (ALIMENTAR DADOS, CADASTRAR E UPLOAD)
# -------------------------------------------------------------
if st.session_state["tipo_usuario"] == "admin":
    st.title("Painel de Gestão & Diagnóstico BIM (Admin)")
    
    aba_cadastrar, aba_avaliar, aba_documentos = st.tabs([
        "➕ Cadastrar Empresa", 
        "📝 Inserir Nova Avaliação", 
        "📁 Upload de Documentos"
    ])
    
    # 1. Cadastrar Empresa
    with aba_cadastrar:
        st.subheader("Nova Empresa Cliente")
        with st.form("form_nova_empresa"):
            id_emp = st.text_input("ID único da Empresa (sem espaços, minúsculo)", placeholder="ex: construtora_alfa")
            nome_emp = st.text_input("Nome da Empresa", placeholder="ex: Construtora Alfa Ltda")
            senha_emp = st.text_input("Senha de acesso do cliente", type="password")
            
            if st.form_submit_button("Salvar Empresa"):
                if id_emp and nome_emp and senha_emp:
                    DADOS.setdefault("empresas", {})[id_emp] = {
                        "nome": nome_emp,
                        "senha": senha_emp,
                        "avaliacoes": [],
                        "documentos": []
                    }
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success(f"Empresa '{nome_emp}' registrada com sucesso no banco!")
                        st.rerun()
                else:
                    st.warning("Preencha todos os campos obrigatórios.")
                    
    # 2. Inserir Avaliação BIM
    with aba_avaliar:
        st.subheader("Registrar Ciclo de Maturidade BIM")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if not empresas_opts:
            st.info("Cadastre uma empresa primeiro.")
        else:
            emp_sel = st.selectbox("Selecione a Empresa", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"])
            
            with st.form("form_avaliacao"):
                c1, c2 = st.columns(2)
                ciclo_nome = c1.text_input("Identificação do Ciclo", value="Ciclo 2 - Acompanhamento")
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
                        st.success("Avaliação gravada e sincronizada no GitHub com sucesso!")
                        st.rerun()

    # 3. Upload de Documentos
    with aba_documentos:
        st.subheader("Subir Relatório ou Diretrizes para a Empresa")
        empresas_opts = list(DADOS.get("empresas", {}).keys())
        if empresas_opts:
            emp_doc = st.selectbox("Selecione a Empresa Destinatária", empresas_opts, format_func=lambda x: DADOS["empresas"][x]["nome"], key="sel_emp_doc")
            doc_nome = st.text_input("Título do Documento (Ex: Relatório Executivo Ciclo 1)")
            arquivo = st.file_uploader("Selecione o arquivo (PDF, DWG, XLSX)", type=["pdf", "xlsx", "docx", "zip"])
            
            if st.button("Enviar Arquivo"):
                if arquivo and doc_nome:
                    bytes_data = arquivo.read()
                    base64_str = base64.b64encode(bytes_data).decode("utf-8")
                    
                    novo_doc = {
                        "titulo": doc_nome,
                        "nome_arquivo": arquivo.name,
                        "data_envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "conteudo_b64": base64_str
                    }
                    DADOS["empresas"][emp_doc].setdefault("documentos", []).append(novo_doc)
                    if salvar_dados(DADOS, SHA_ATUAL):
                        st.success(f"Documento '{arquivo.name}' disponibilizado para a empresa!")
                        st.rerun()
                else:
                    st.warning("Forneça o título e selecione um arquivo.")

# -------------------------------------------------------------
# VISÃO CLIENTE (DASHBOARD ANALÍTICO ESTILO POWER BI)
# -------------------------------------------------------------
else:
    empresa_id = st.session_state["usuario_logado"]
    dados_cliente = DADOS.get("empresas", {}).get(empresa_id, {})
    nome_empresa = dados_cliente.get("nome", "Empresa")
    avaliacoes = dados_cliente.get("avaliacoes", [])
    documentos = dados_cliente.get("documentos", [])
    
    st.title(f"Dashboard de Maturidade BIM | {nome_empresa}")
    
    if not avaliacoes:
        st.info("Nenhuma avaliação registrada até o momento. O consultor está preparando seus dados.")
    else:
        ult_av = avaliacoes[-1]
        
        # 1. CARDS KPIS SUPERIORES
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("Índice Médio Global", f"{ult_av['media_global']} pts", "/ 40 pts")
        with kpi2:
            st.metric("Nível Predominante", ult_av['nivel'])
        with kpi3:
            st.metric("Último Ciclo", ult_av['ciclo'])
        with kpi4:
            st.metric("Total de Revisões", f"{len(avaliacoes)} ciclos")
            
        st.markdown("---")
        
        # 2. GRÁFICOS ANALÍTICOS (PLOTLY POWER BI STYLE)
        g1, g2 = st.columns(2)
        
        with g1:
            st.subheader("Equilíbrio de Competências (Radar)")
            categorias = ['Software', 'Hardware', 'Rede', 'Recursos', 'Fluxo', 'Produtos', 'Políticas']
            valores_atuais = [
                ult_av['software'], ult_av['hardware'], ult_av['rede'],
                ult_av['recursos'], ult_av['fluxo'], ult_av['produtos'], ult_av['politicas']
            ]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_atuais,
                theta=categorias,
                fill='toself',
                name=ult_av['ciclo'],
                line_color='#0284c7'
            ))
            
            # Se houver ciclo anterior, plota como linha comparativa
            if len(avaliacoes) > 1:
                penult_av = avaliacoes[-2]
                valores_ant = [
                    penult_av['software'], penult_av['hardware'], penult_av['rede'],
                    penult_av['recursos'], penult_av['fluxo'], penult_av['produtos'], penult_av['politicas']
                ]
                fig_radar.add_trace(go.Scatterpolar(
                    r=valores_ant,
                    theta=categorias,
                    name=penult_av['ciclo'],
                    line=dict(color='#94a3b8', dash='dash')
                ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 40])),
                showlegend=True,
                margin=dict(l=40, r=40, t=30, b=30),
                height=350,
                template="plotly_dark"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
        with g2:
            st.subheader("Evolução Histórica da Maturidade")
            df_hist = pd.DataFrame(avaliacoes)
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df_hist['ciclo'],
                y=df_hist['media_global'],
                mode='lines+markers+text',
                text=[f"{v} pts" for v in df_hist['media_global']],
                textposition="top center",
                line=dict(color='#38bdf8', width=3),
                marker=dict(size=8, color='#0284c7')
            ))
            fig_line.update_layout(
                yaxis=dict(range=[0, 42], title="Pontuação Média"),
                xaxis=dict(title="Ciclos de Auditoria"),
                height=350,
                margin=dict(l=40, r=40, t=30, b=30),
                template="plotly_dark"
            )
            st.plotly_chart(fig_line, use_container_width=True)

    # 3. CENTRAL DE DOWNLOADS DO CLIENTE
    st.markdown("---")
    st.subheader("📁 Central de Documentos & Entregáveis")
    if not documentos:
        st.caption("Nenhum documento disponível para download no momento.")
    else:
        for doc in documentos:
            d_col1, d_col2, d_col3 = st.columns([3, 1.5, 1.5])
            d_col1.write(f"📄 **{doc['titulo']}** (`{doc['nome_arquivo']}`)")
            d_col2.caption(f"Disponibilizado em: {doc.get('data_envio', '-')}")
            
            # Decodifica base64 para o botão de download
            bytes_bin = base64.b64decode(doc['conteudo_b64'])
            d_col3.download_button(
                label="⬇️ Baixar Arquivo",
                data=bytes_bin,
                file_name=doc['nome_arquivo'],
                use_container_width=True,
                key=doc['titulo']
            )
