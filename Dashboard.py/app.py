# ============================================================
#  Dashboard — Secretaria de Educação da Paraíba (SEE-PB)
#  Desenvolvido com Streamlit + Plotly + Folium
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
import time
import requests
import warnings
warnings.filterwarnings("ignore")

# ── Configuração da página ──────────────────────────────────
st.set_page_config(
    page_title="Dashboard SEE-PB",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta de cores SEE-PB ──────────────────────────────────
AZUL       = "#0b5fa5"
AZUL2      = "#1e88e5"
AMARELO    = "#ffcc00"
VERMELHO   = "#e53935"
VERDE      = "#00c853"
CINZA      = "#f4f6f8"
CINZA_BORDA= "#e0e0e0"

SEQ_COLORS = [AZUL, AZUL2, "#42a5f5", "#90caf9", "#1565c0", "#0d47a1",
              "#4fc3f7", "#81d4fa", "#b3e5fc", "#e1f5fe"]
QUAL_COLORS = [AZUL, AMARELO, VERDE, VERMELHO, "#9c27b0", "#ff9800",
               "#009688", "#795548", "#607d8b", "#e91e63"]

# ── CSS Global ──────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    color: #2b303a;
  }

  /* Sidebar styling (Light and clean) */
  [data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
    border-right: 1px solid #dee2e6;
  }
  [data-testid="stSidebar"] * {
    color: #212529 !important;
  }
  [data-testid="stSidebar"] .stRadio label {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    cursor: pointer;
    transition: all .2s;
    display: block;
    font-weight: 500;
    font-size: 0.95rem;
  }
  [data-testid="stSidebar"] .stRadio label:hover {
    background-color: #e3f0fb !important;
    border-color: #0b5fa5 !important;
    color: #0b5fa5 !important;
  }
  [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
    background-color: #e3f0fb !important;
    border-color: #0b5fa5 !important;
    color: #0b5fa5 !important;
    font-weight: 600;
  }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiselect label {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: .05em;
    text-transform: uppercase;
    color: #495057 !important;
  }
  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stMultiselect > div > div {
    background-color: #ffffff !important;
    border: 1px solid #ced4da !important;
    color: #212529 !important;
    border-radius: 8px !important;
  }

  /* Main header styling */
  .main-header {
    background: linear-gradient(135deg, #0b5fa5 0%, #1e88e5 60%, #0d47a1 100%);
    border-radius: 16px;
    padding: 30px 40px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 30px rgba(11,95,165,0.15);
  }
  .main-header h1 {
    color: white !important;
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    line-height: 1.2 !important;
  }
  .main-header p {
    color: rgba(255,255,255,0.9) !important;
    margin: 6px 0 0 !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
  }
  .badge {
    background: #ffcc00;
    color: #0b5fa5;
    font-weight: 800;
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 0.95rem;
    white-space: nowrap;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  }

  /* KPI Cards styling (larger and more readable) */
  .kpi-card {
    background: white;
    border-radius: 14px;
    padding: 24px 26px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    border-left: 6px solid #0b5fa5;
    transition: transform .2s, box-shadow .2s;
    position: relative;
    overflow: hidden;
  }
  .kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  }
  .kpi-card::after {
    content: '';
    position: absolute;
    top: -20px; right: -20px;
    width: 80px; height: 80px;
    border-radius: 50%;
    background: rgba(11,95,165,0.03);
  }
  .kpi-title {
    font-size: 0.88rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .07em;
    color: #495057;
    margin-bottom: 8px;
  }
  .kpi-value {
    font-size: 2.4rem;
    font-weight: 800;
    color: #0b5fa5;
    line-height: 1.1;
  }
  .kpi-sub {
    font-size: 0.95rem;
    color: #6c757d;
    margin-top: 6px;
    font-weight: 500;
  }
  .kpi-icon {
    font-size: 2rem;
    float: right;
    margin-top: -6px;
  }
  .kpi-yellow  { border-left-color: #ffcc00; }
  .kpi-green   { border-left-color: #00c853; }
  .kpi-red     { border-left-color: #e53935; }
  .kpi-purple  { border-left-color: #9c27b0; }

  /* Section headers */
  .section-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: #0b5fa5;
    border-bottom: 3px solid #ffcc00;
    padding-bottom: 6px;
    margin: 28px 0 18px;
    display: inline-block;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #f0f4f8;
    border-radius: 12px;
    padding: 6px;
    gap: 6px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 10px 16px;
  }
  .stTabs [aria-selected="true"] {
    background: #0b5fa5 !important;
    color: white !important;
  }

  /* Dataframes */
  .dataframe-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  }

  /* Filter bar */
  .filter-bar {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
    border: 1px solid #dee2e6;
  }

  /* Page divider */
  .page-divider {
    height: 4px;
    background: linear-gradient(90deg, #0b5fa5, #ffcc00, #00c853);
    border-radius: 2px;
    margin: 30px 0;
  }

  /* Contact cards (larger text) */
  .contact-card {
    background: white;
    border-radius: 12px;
    padding: 20px 22px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
    margin-bottom: 14px;
    border-top: 5px solid #0b5fa5;
    transition: transform .15s;
  }
  .contact-card:hover { transform: translateY(-2px); }
  .contact-card h4 { color: #0b5fa5; font-size: 1.15rem; margin-bottom: 6px; font-weight: 700; }
  .contact-card p { color: #333333; font-size: 0.95rem; margin: 4px 0; line-height: 1.4; }
  .contact-tag {
    display: inline-block;
    background: #e3f0fb;
    color: #0b5fa5;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 10px;
    margin-bottom: 8px;
  }

  /* Footer */
  .footer {
    text-align: center;
    padding: 24px;
    color: #6c757d;
    font-size: 0.9rem;
    border-top: 1px solid #dee2e6;
    margin-top: 48px;
  }
  
  /* Metric override */
  [data-testid="stMetricValue"] {
    color: #0b5fa5 !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
  }
  
  /* Chips */
  .chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.82rem;
    font-weight: 700;
    margin: 2px;
  }
  .chip-blue   { background: #e3f0fb; color: #0b5fa5; }
  .chip-yellow { background: #fff8e1; color: #b8860b; }
  .chip-green  { background: #e8f5e9; color: #2e7d32; }
  .chip-red    { background: #fce4ec; color: #c62828; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  CARREGAMENTO E LIMPEZA DOS DADOS
# ════════════════════════════════════════════════════════════

BASE = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE, "ESCOLAS 2026 - ESCOLAS.csv")):
    DATA = BASE
else:
    DATA = os.path.dirname(BASE)


@st.cache_data(show_spinner="Carregando dados…")
def load_all():
    """Carrega todos os CSVs e retorna DataFrames limpos."""

    def read(name):
        return pd.read_csv(
            os.path.join(DATA, name),
            encoding="utf-8",
            low_memory=False
        )

    def normalize_columns(df):
        df.columns = df.columns.str.strip()
        for col in list(df.columns):
            u = col.upper().strip()
            if u in ["INEP", "CODIGO INEP", "CÓDIGO INEP", "COD_INEP", "CODIGO_INEP"]:
                df = df.rename(columns={col: "CODIGO_INEP"})
            elif u in ["TOTAL DE MATRÍCULAS", "TOTAL DE MATRICULAS", "TOTAL_MATRICULAS", "TOTAL_MAT", "MATRICULAS_TOTAL", "TOTAL MATRICULAS"]:
                df = df.rename(columns={col: "TOTAL"})
            elif u in ["GERENCIA", "GERÊNCIA", "GERENCIA REGIONAL", "GRE REGIONAL", "REGIONAL DE ENSINO"]:
                df = df.rename(columns={col: "GRE"})
        return df

    # ── Escolas principal ────────────────────────────────────
    escolas = read("ESCOLAS 2026 - ESCOLAS.csv")
    escolas = normalize_columns(escolas)
    
    # Renomeia para evitar conflito com a coluna de matrículas do GEDRA
    escolas = escolas.rename(columns={"ENSINO MÉDIO": "ENSINO_MÉDIO_OFERTA"})
    
    escolas["CODIGO_INEP"] = pd.to_numeric(escolas["CODIGO_INEP"], errors="coerce")
    escolas = escolas.dropna(subset=["CODIGO_INEP"]).copy()
    escolas["CODIGO_INEP"] = escolas["CODIGO_INEP"].astype(int)

    # Coordenadas limpas
    def parse_coord(s):
        try:
            return float(str(s).replace(",", ".").strip())
        except Exception:
            return np.nan

    escolas["LAT"] = escolas["Latitude"].apply(parse_coord)
    escolas["LON"] = escolas["Longitude"].apply(parse_coord)

    # IDEB numérico (corrigindo vírgula decimal)
    ideb_cols = [c for c in escolas.columns if "IDEB" in c]
    for c in ideb_cols:
        escolas[c] = pd.to_numeric(escolas[c].astype(str).str.replace(",", "."), errors="coerce")

    # Ano implantação
    escolas["Ano de Implatação"] = pd.to_numeric(
        escolas["Ano de Implatação"], errors="coerce"
    )

    # ── Gestão ───────────────────────────────────────────────
    gestao = read("ESCOLAS 2026 - ACOMPANHAMENTO - GESTÃO.csv")
    gestao = normalize_columns(gestao)
    gestao["CODIGO_INEP"] = pd.to_numeric(gestao["CODIGO_INEP"], errors="coerce")
    gestao = gestao.dropna(subset=["CODIGO_INEP"])
    gestao["CODIGO_INEP"] = gestao["CODIGO_INEP"].astype(int)

    # ── Setor / Equipe ───────────────────────────────────────
    setor = read("ESCOLAS 2026 - ACOMPANHAMENTO - SETOR.csv")
    setor.columns = setor.columns.str.strip()

    # ── Contatos ─────────────────────────────────────────────
    contatos = read("ESCOLAS 2026 - CONTATOS.csv")
    contatos = normalize_columns(contatos)
    contatos["CODIGO_INEP"] = pd.to_numeric(
        contatos["CODIGO_INEP"], errors="coerce"
    )
    contatos = contatos.dropna(subset=["CODIGO_INEP"])
    contatos["CODIGO_INEP"] = contatos["CODIGO_INEP"].astype(int)

    # ── ECI/ECIT (base maior de matrículas) ─────────────────
    eci = read("ESCOLAS 2026 - ECI_ECIT.csv")
    eci = normalize_columns(eci)
    eci["CODIGO_INEP"] = pd.to_numeric(eci["CODIGO_INEP"], errors="coerce")
    eci = eci.dropna(subset=["CODIGO_INEP"])
    eci["CODIGO_INEP"] = eci["CODIGO_INEP"].astype(int)
    num_cols_eci = ["1º ANO","2º ANO","3º ANO","4º ANO","5º ANO",
                    "6º ANO","7º ANO","8º ANO","9º ANO",
                    "1ª SÉRIE","2ª SÉRIE","3ª SÉRIE"]
    for c in num_cols_eci:
        if c in eci.columns:
            eci[c] = pd.to_numeric(eci[c], errors="coerce")
    if "TOTAL" in eci.columns:
        eci["TOTAL"] = pd.to_numeric(eci["TOTAL"], errors="coerce")
    else:
        eci["TOTAL"] = 0

    # ── Escolas do Amanhã ────────────────────────────────────
    amanha = read("ESCOLAS 2026 - ESCOLAS DO AMANHÃ.csv")
    amanha = normalize_columns(amanha)
    amanha["CODIGO_INEP"] = pd.to_numeric(amanha["CODIGO_INEP"], errors="coerce")
    amanha = amanha.dropna(subset=["CODIGO_INEP"])
    amanha["CODIGO_INEP"] = amanha["CODIGO_INEP"].astype(int)
    amanha["Matrículas"] = pd.to_numeric(amanha["Matrículas"], errors="coerce")

    # ── Matrículas GEDRA ─────────────────────────────────────
    matriculas = read("ESCOLAS 2026 - MATRICULAS- GEDRA 09_06_2026.csv")
    matriculas = normalize_columns(matriculas)
    matriculas["CODIGO_INEP"] = pd.to_numeric(
        matriculas["CODIGO_INEP"], errors="coerce"
    )
    matriculas = matriculas.dropna(subset=["CODIGO_INEP"])
    matriculas["CODIGO_INEP"] = matriculas["CODIGO_INEP"].astype(int)
    num_cols_mat = ["1º ANO","2º ANO","3º ANO","4º ANO","5º ANO",
                    "6º ANO","7º ANO","8º ANO","9º ANO",
                    "1ª SÉRIE","2ª SÉRIE","3ª SÉRIE",
                    "ENSINO FUNDAMENTAL (ANOS INICIAIS)",
                    "ENSINO FUNDAMENTAL (ANOS FINAIS)","ENSINO MÉDIO","TOTAL"]
    for c in num_cols_mat:
        if c in matriculas.columns:
            matriculas[c] = pd.to_numeric(matriculas[c], errors="coerce")

    # Garantir que a coluna TOTAL exista em matriculas
    if "TOTAL" not in matriculas.columns:
        sum_cols = [c for c in num_cols_mat if c in matriculas.columns and c != "TOTAL"]
        if sum_cols:
            matriculas["TOTAL"] = matriculas[sum_cols].sum(axis=1)
        else:
            matriculas["TOTAL"] = 0
    else:
        sum_cols = [c for c in num_cols_mat if c in matriculas.columns and c != "TOTAL"]
        if sum_cols:
            calc_tot = matriculas[sum_cols].sum(axis=1)
            matriculas["TOTAL"] = matriculas["TOTAL"].fillna(calc_tot)

    # ── Merge principal: escolas + gestão ────────────────────
    escolas_full = escolas.merge(
        gestao[["CODIGO_INEP","Funcionamento atual",
                "Situação do Plano de Contigência",
                "Consultores de gestão","Período/semana",
                "Data do alinhamento","Observações e encaminhamentos"]],
        on="CODIGO_INEP", how="left"
    )

    # ── Merge: escolas_full + matriculas GEDRA ───────────────
    # Evita conflitos de colunas repetidas (ex: GRE, MUNICIPIO, TIPO) entre escolas_full e matriculas
    cols_to_merge = [c for c in matriculas.columns if c == "CODIGO_INEP" or c not in escolas_full.columns]
    escolas_mat = escolas_full.merge(
        matriculas[cols_to_merge],
        on="CODIGO_INEP", how="left"
    )

    if "GRE" not in escolas_mat.columns and "GRE_x" in escolas_mat.columns:
        escolas_mat["GRE"] = escolas_mat["GRE_x"]

    if "TOTAL" not in escolas_mat.columns:
        escolas_mat["TOTAL"] = 0
    else:
        escolas_mat["TOTAL"] = pd.to_numeric(escolas_mat["TOTAL"], errors="coerce").fillna(0)

    return {
        "escolas":     escolas,
        "gestao":      gestao,
        "setor":       setor,
        "contatos":    contatos,
        "eci":         eci,
        "amanha":      amanha,
        "matriculas":  matriculas,
        "escolas_full":escolas_full,
        "escolas_mat": escolas_mat,
    }


# ── Helpers ─────────────────────────────────────────────────

def kpi(title, value, sub="", color="", icon=""):
    cls = f"kpi-card kpi-{color}" if color else "kpi-card"
    st.markdown(f"""
    <div class="{cls}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<div class="page-divider"></div>', unsafe_allow_html=True)


def header(title, subtitle, badge=""):
    b = f'<span class="badge">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="main-header">
      <div>
        <h1>📚 {title}</h1>
        <p>{subtitle}</p>
      </div>
      {b}
    </div>""", unsafe_allow_html=True)


def fmt_num(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return "—"


def plotly_defaults(fig, height=400):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12, color="#333"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=CINZA_BORDA,
            borderwidth=1,
        ),
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        tickfont=dict(size=11)
    )
    fig.update_yaxes(
        gridcolor="#f0f0f0", zeroline=False,
        tickfont=dict(size=11)
    )
    return fig


# ════════════════════════════════════════════════════════════
#  SIDEBAR — Navegação
# ════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px">
      <div style="font-size:2.8rem">📚</div>
      <div style="font-weight:800;font-size:1.1rem;letter-spacing:.03em">SEE-PB</div>
      <div style="font-size:.75rem;opacity:.7;margin-top:2px">Secretaria de Educação<br>da Paraíba</div>
      <div style="background:#ffcc00;color:#0b5fa5;font-weight:700;font-size:.72rem;
                  padding:3px 10px;border-radius:10px;display:inline-block;margin-top:8px">
        Dashboard 2026
      </div>
    </div>
    <hr style="border-color:rgba(255,255,255,.15);margin:12px 0">
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "🗂️ **NAVEGAÇÃO**",
        options=[
            "🏠  Visão Geral",
            "📚  Matrículas",
            "📈  IDEB & Qualidade",
            "🗺️  Gestão & Acompanhamento",
            "🏫  Escolas do Amanhã",
            "📞  Contatos & Equipe",
            "🔍  Explorador de Escolas",
        ],
        label_visibility="visible"
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,.15);margin:12px 0'>", unsafe_allow_html=True)

    # ── Botão de sincronização ───────────────────────────────
    st.markdown("""
    <div style="font-size:.75rem;font-weight:600;opacity:.85;margin-bottom:6px;text-align:center">
      🔄 Sincronização de Dados
    </div>
    """, unsafe_allow_html=True)

    DEFAULT_APPS_SCRIPT_URL   = "https://script.google.com/macros/s/AKfycbwaKfFbLRLUCQyHSiws2jX43FKw3j2xRmxKcWns3q950dP3_VZsTvUg-oYbAtWUlpWe/exec"
    DEFAULT_APPS_SCRIPT_TOKEN = "edu-pb-sync-2026-secretaria"

    if st.button("⚡ Sincronizar Agora", use_container_width=True):
        try:
            try:
                script_url   = st.secrets.get("APPS_SCRIPT_URL", DEFAULT_APPS_SCRIPT_URL)
                script_token = st.secrets.get("APPS_SCRIPT_TOKEN", DEFAULT_APPS_SCRIPT_TOKEN)
            except Exception:
                script_url   = DEFAULT_APPS_SCRIPT_URL
                script_token = DEFAULT_APPS_SCRIPT_TOKEN

            with st.spinner("Enviando dados da planilha para o GitHub…"):
                resp = requests.get(
                    script_url,
                    params={"token": script_token},
                    timeout=60
                )
            resultado = resp.json()
            if resultado.get("status") == "ok":
                st.success("✅ Sincronizado! O dashboard será recarregado em instantes.")
                st.cache_data.clear()
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"Erro: {resultado.get('mensagem')}")
        except Exception as e:
            st.error(f"Falha: {e}")

    st.markdown("""
    <div style="font-size:.68rem;opacity:.5;text-align:center;padding:4px 0;margin-top:4px">
      Atualiza os CSVs direto do Google Sheets
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,.15);margin:12px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:.72rem;opacity:.6;text-align:center;padding:4px 0">
      Dados: ESCOLAS 2026 • GEDRA<br>Atualizado: Junho/2026
    </div>
    """, unsafe_allow_html=True)


# ── Carrega dados ────────────────────────────────────────────
D = load_all()
escolas      = D["escolas"]
gestao       = D["gestao"]
setor        = D["setor"]
contatos     = D["contatos"]
eci          = D["eci"]
amanha       = D["amanha"]
matriculas   = D["matriculas"]
escolas_full = D["escolas_full"]
escolas_mat  = D["escolas_mat"]

GRE_LIST  = sorted(escolas["GRE"].dropna().unique())
MUN_LIST  = sorted(escolas["MUNICIPIO"].dropna().unique())
TIPO_LIST = sorted(escolas["TIPO"].dropna().unique())


# ════════════════════════════════════════════════════════════
#  PÁGINA 1 — VISÃO GERAL
# ════════════════════════════════════════════════════════════

if pagina.startswith("🏠"):
    header(
        "Dashboard Educacional — Paraíba",
        "Monitoramento das Escolas Cidadãs Integrais · 2026",
        badge="16 GREs · 113 Municípios"
    )

    # ── Filtros ──────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fi1, fi2, fi3, fi4 = st.columns(4)
        with fi1:
            f_gre = st.multiselect("GRE", GRE_LIST, placeholder="Todas", key="vg_gre")
        with fi2:
            muns_filtered = MUN_LIST
            if f_gre:
                muns_filtered = sorted(escolas[escolas["GRE"].isin(f_gre)]["MUNICIPIO"].dropna().unique())
            f_mun = st.multiselect("Município", muns_filtered, placeholder="Todos", key="vg_mun")
        with fi3:
            f_tipo = st.multiselect("Tipo de Escola", TIPO_LIST, placeholder="Todos", key="vg_tipo")
        with fi4:
            schools_filtered = escolas
            if f_gre:
                schools_filtered = schools_filtered[schools_filtered["GRE"].isin(f_gre)]
            if f_mun:
                schools_filtered = schools_filtered[schools_filtered["MUNICIPIO"].isin(f_mun)]
            if f_tipo:
                schools_filtered = schools_filtered[schools_filtered["TIPO"].isin(f_tipo)]
            
            schools_filtered = schools_filtered.copy()
            schools_filtered["Label"] = schools_filtered["NOME_ESCOLA"] + " (" + schools_filtered["CODIGO_INEP"].astype(str) + ")"
            labels_list = sorted(schools_filtered["Label"].dropna().unique())
            f_escolas_labels = st.multiselect("Escola (Nome / INEP)", labels_list, placeholder="Todas", key="vg_escola")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Filtragem dos DataFrames ─────────────────────────────
    df_esc = escolas.copy()
    df_esc_full = escolas_full.copy()
    df_esc_mat = escolas_mat.copy()

    if f_gre:
        df_esc = df_esc[df_esc["GRE"].isin(f_gre)]
        df_esc_full = df_esc_full[df_esc_full["GRE"].isin(f_gre)]
        df_esc_mat = df_esc_mat[df_esc_mat["GRE"].isin(f_gre)]
    if f_mun:
        df_esc = df_esc[df_esc["MUNICIPIO"].isin(f_mun)]
        df_esc_full = df_esc_full[df_esc_full["MUNICIPIO"].isin(f_mun)]
        df_esc_mat = df_esc_mat[df_esc_mat["MUNICIPIO"].isin(f_mun)]
    if f_tipo:
        df_esc = df_esc[df_esc["TIPO"].isin(f_tipo)]
        df_esc_full = df_esc_full[df_esc_full["TIPO"].isin(f_tipo)]
        df_esc_mat = df_esc_mat[df_esc_mat["TIPO"].isin(f_tipo)]
    if f_escolas_labels:
        selected_ineps = []
        for lbl in f_escolas_labels:
            try:
                inep = int(lbl.split("(")[-1].replace(")", "").strip())
                selected_ineps.append(inep)
            except ValueError:
                pass
        df_esc = df_esc[df_esc["CODIGO_INEP"].isin(selected_ineps)]
        df_esc_full = df_esc_full[df_esc_full["CODIGO_INEP"].isin(selected_ineps)]
        df_esc_mat = df_esc_mat[df_esc_mat["CODIGO_INEP"].isin(selected_ineps)]

    # ── KPIs ─────────────────────────────────────────────────
    total_escolas = len(df_esc)
    total_mat     = df_esc_mat["TOTAL"].sum() if "TOTAL" in df_esc_mat.columns else 0
    total_munic   = df_esc["MUNICIPIO"].nunique()
    total_gre     = df_esc["GRE"].nunique()
    pct_presencial = (
        df_esc_full["Funcionamento atual"]
        .str.contains("Presencial", na=False).mean() * 100
    ) if len(df_esc_full) > 0 else 0.0
    pct_mec = (df_esc["MEC"] == "Sim").mean() * 100 if len(df_esc) > 0 else 0.0
    total_ai = df_esc_mat["ENSINO FUNDAMENTAL (ANOS INICIAIS)"].sum() if "ENSINO FUNDAMENTAL (ANOS INICIAIS)" in df_esc_mat.columns else 0
    total_af = df_esc_mat["ENSINO FUNDAMENTAL (ANOS FINAIS)"].sum() if "ENSINO FUNDAMENTAL (ANOS FINAIS)" in df_esc_mat.columns else 0
    total_em = df_esc_mat["ENSINO MÉDIO"].sum() if "ENSINO MÉDIO" in df_esc_mat.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total de Escolas", fmt_num(total_escolas), "ECIs/ECITs", icon="🏫")
    with c2: kpi("Total de Matrículas", fmt_num(total_mat), "Rede ECI/ECIT", "yellow", "👩‍🎓")
    with c3: kpi("Municípios Atendidos", fmt_num(total_munic), "de 223 no estado", "green", "📍")
    with c4: kpi("GREs", fmt_num(total_gre), "Regionais de Ensino", icon="🗺️")

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5: kpi("Presencial", f"{pct_presencial:.0f}%", "das escolas", icon="✅")
    with c6: kpi("Com MEC", f"{pct_mec:.0f}%", "convênio federal", "green", "🏛️")
    with c7: kpi("Ensino Médio", fmt_num(total_em), "alunos matriculados", "yellow", "🎓")
    with c8: kpi("Anos Finais", fmt_num(total_af), "alunos matriculados", "purple", "📖")

    divider()

    # ── Gráficos ──────────────────────────────────────────────
    col_l, col_r = st.columns([3, 2])

    with col_l:
        section("🗂️ Escolas por GRE")
        gre_cnt = df_esc.groupby("GRE").size().reset_index(name="Escolas")
        fig = px.bar(
            gre_cnt.sort_values("Escolas", ascending=True),
            x="Escolas", y="GRE", orientation="h",
            color="Escolas",
            color_continuous_scale=[[0, "#c8ddf5"], [1, AZUL]],
            text="Escolas",
            title="Distribuição por GRE",
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        plotly_defaults(fig, height=480)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        section("🏷️ Distribuição por Tipo")
        tipo_cnt = df_esc["TIPO"].value_counts().reset_index()
        tipo_cnt.columns = ["Tipo", "Qtd"]
        tipo_cnt["Tipo"] = tipo_cnt["Tipo"].str.replace("ECI ", "", regex=False)
        fig2 = px.pie(
            tipo_cnt, values="Qtd", names="Tipo",
            color_discrete_sequence=QUAL_COLORS,
            hole=0.5,
            title="Por tipo de escola",
        )
        fig2.update_traces(
            textposition="outside",
            textinfo="percent+label",
            pull=[0.04] * len(tipo_cnt)
        )
        plotly_defaults(fig2, height=350)
        st.plotly_chart(fig2, use_container_width=True)

        section("🏛️ Convênio MEC")
        mec_cnt = df_esc["MEC"].value_counts().reset_index()
        mec_cnt.columns = ["MEC", "Qtd"]
        fig3 = px.bar(
            mec_cnt, x="MEC", y="Qtd",
            color="MEC",
            color_discrete_map={"Sim": VERDE, "Não": CINZA_BORDA},
            text="Qtd",
            title="",
        )
        fig3.update_traces(textposition="outside", marker_line_width=0)
        plotly_defaults(fig3, height=200)
        fig3.update_layout(showlegend=False, margin=dict(t=10))
        st.plotly_chart(fig3, use_container_width=True)

    divider()

    col_a, col_b = st.columns(2)

    with col_a:
        section("📅 Expansão da Rede — Ano de Implantação")
        ano_cnt = df_esc.dropna(subset=["Ano de Implatação"])
        ano_cnt = ano_cnt.groupby("Ano de Implatação").size().reset_index(name="Escolas")
        ano_cnt["Acumulado"] = ano_cnt["Escolas"].cumsum()
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(
            go.Bar(
                x=ano_cnt["Ano de Implatação"].astype(int).astype(str),
                y=ano_cnt["Escolas"],
                name="Novas escolas",
                marker_color=AZUL,
                text=ano_cnt["Escolas"],
                textposition="outside",
            ), secondary_y=False
        )
        fig4.add_trace(
            go.Scatter(
                x=ano_cnt["Ano de Implatação"].astype(int).astype(str),
                y=ano_cnt["Acumulado"],
                name="Acumulado",
                line=dict(color=AMARELO, width=3),
                mode="lines+markers+text",
                text=ano_cnt["Acumulado"],
                textposition="top center",
                marker=dict(size=8),
            ), secondary_y=True
        )
        fig4.update_layout(
            title="Novas escolas por ano",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", size=12),
            margin=dict(l=10, r=10, t=40, b=10),
            height=360,
            legend=dict(bgcolor="rgba(255,255,255,0.9)"),
        )
        fig4.update_yaxes(title_text="Novas Escolas", secondary_y=False, gridcolor="#f0f0f0")
        fig4.update_yaxes(title_text="Total Acumulado", secondary_y=True)
        st.plotly_chart(fig4, use_container_width=True)

    with col_b:
        section("📊 Matrículas por Segmento e GRE")
        if "GRE" in df_esc_mat.columns and len(df_esc_mat) > 0:
            agg_dict = {}
            for col, seg_name in [("ENSINO FUNDAMENTAL (ANOS INICIAIS)", "AI"), 
                                  ("ENSINO FUNDAMENTAL (ANOS FINAIS)", "AF"), 
                                  ("ENSINO MÉDIO", "EM")]:
                if col in df_esc_mat.columns:
                    agg_dict[seg_name] = (col, "sum")
            
            if agg_dict:
                mat_gre = df_esc_mat.groupby("GRE").agg(**agg_dict).reset_index()
                if "EM" in mat_gre.columns:
                    mat_gre = mat_gre.sort_values("EM", ascending=False)
                
                value_vars = [c for c in ["AI", "AF", "EM"] if c in mat_gre.columns]
                mat_long = mat_gre.melt(
                    id_vars="GRE",
                    value_vars=value_vars,
                    var_name="Segmento",
                    value_name="Matrículas"
                )
                seg_map = {"AI": "Anos Iniciais", "AF": "Anos Finais", "EM": "Ensino Médio"}
                mat_long["Segmento"] = mat_long["Segmento"].map(seg_map)
                fig5 = px.bar(
                    mat_long, x="GRE", y="Matrículas",
                    color="Segmento",
                    color_discrete_map={
                        "Anos Iniciais": AZUL2,
                        "Anos Finais":   AZUL,
                        "Ensino Médio":  AMARELO,
                    },
                    barmode="stack",
                    title="Matrículas por GRE e segmento",
                )
                fig5.update_traces(marker_line_width=0)
                plotly_defaults(fig5, height=360)
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("Dados de matrículas por segmento indisponíveis.")
        else:
            st.info("Dados por GRE indisponíveis para os filtros atuais.")

    divider()

    # ── Mapa ─────────────────────────────────────────────────
    section("🗺️ Mapa de Distribuição Geográfica das Escolas")
    map_df = df_esc_mat.dropna(subset=["LAT","LON"]).copy()
    map_df["TOTAL_MAT"] = map_df["TOTAL"].fillna(0)
    map_df["Tooltip"] = (
        map_df["NOME_ESCOLA"] + "<br>" +
        map_df["GRE"] + " — " + map_df["MUNICIPIO"] +
        "<br>Tipo: " + map_df["TIPO"] +
        "<br>Matrículas: " + map_df["TOTAL_MAT"].astype(int).astype(str)
    )

    if len(map_df) > 0:
        fig_map = px.scatter_mapbox(
            map_df,
            lat="LAT", lon="LON",
            hover_name="NOME_ESCOLA",
            hover_data={
                "LAT": False, "LON": False,
                "GRE": True, "MUNICIPIO": True,
                "TIPO": True, "TOTAL_MAT": True,
            },
            color="GRE",
            size="TOTAL_MAT",
            size_max=20,
            zoom=6.5,
            center={"lat": -7.2, "lon": -36.8},
            mapbox_style="carto-positron",
            title="",
            color_discrete_sequence=px.colors.qualitative.Bold,
            opacity=0.8,
        )
        plotly_defaults(fig_map, height=500)
        fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Dados de coordenadas não disponíveis para o mapa.")


# ════════════════════════════════════════════════════════════
#  PÁGINA 2 — MATRÍCULAS
# ════════════════════════════════════════════════════════════

elif pagina.startswith("📚"):
    header(
        "Matrículas — Rede ECI/ECIT",
        "Distribuição de alunos por segmento, GRE e município",
        badge="Dados GEDRA · Jun/2026"
    )

    # ── Filtros ───────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_gre = st.multiselect("GRE", GRE_LIST, placeholder="Todas as GREs", key="m_gre")
        with fc2:
            munic_list_m = sorted(escolas["MUNICIPIO"].dropna().unique())
            f_mun = st.multiselect("Município", munic_list_m, placeholder="Todos", key="m_mun")
        with fc3:
            f_tipo = st.multiselect("Tipo", TIPO_LIST, placeholder="Todos os tipos", key="m_tipo")
        st.markdown('</div>', unsafe_allow_html=True)

    # Filtro aplicado
    df_m = escolas_mat.copy()
    if f_gre:  df_m = df_m[df_m["GRE"].isin(f_gre)]
    if f_mun:  df_m = df_m[df_m["MUNICIPIO"].isin(f_mun)]
    if f_tipo: df_m = df_m[df_m["TIPO"].isin(f_tipo)]

    total_m = df_m["TOTAL"].sum()
    ai_m = df_m["ENSINO FUNDAMENTAL (ANOS INICIAIS)"].sum()
    af_m = df_m["ENSINO FUNDAMENTAL (ANOS FINAIS)"].sum()
    em_m = df_m["ENSINO MÉDIO"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Total Matrículas", fmt_num(total_m), "na seleção atual", icon="👩‍🎓")
    with c2: kpi("Anos Iniciais", fmt_num(ai_m), f"{ai_m/total_m*100:.0f}% do total" if total_m else "—", "green", "📗")
    with c3: kpi("Anos Finais", fmt_num(af_m), f"{af_m/total_m*100:.0f}% do total" if total_m else "—", "yellow", "📘")
    with c4: kpi("Ensino Médio", fmt_num(em_m), f"{em_m/total_m*100:.0f}% do total" if total_m else "—", "red", "🎓")
    with c5: kpi("Escolas", fmt_num(len(df_m)), "na seleção", icon="🏫")

    divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Por GRE", "🏫 Por Escola", "📋 Por Série", "📄 Tabela"
    ])

    with tab1:
        col_l, col_r = st.columns(2)
        with col_l:
            gre_mat = df_m.groupby("GRE").agg(
                AI=("ENSINO FUNDAMENTAL (ANOS INICIAIS)", "sum"),
                AF=("ENSINO FUNDAMENTAL (ANOS FINAIS)", "sum"),
                EM=("ENSINO MÉDIO", "sum"),
            ).reset_index()
            gre_mat["Total"] = gre_mat["AI"] + gre_mat["AF"] + gre_mat["EM"]
            gre_mat = gre_mat.sort_values("Total", ascending=True)
            gre_long = gre_mat.melt(
                id_vars="GRE", value_vars=["AI","AF","EM"],
                var_name="Segmento", value_name="Matrículas"
            )
            gre_long["Segmento"] = gre_long["Segmento"].map(
                {"AI":"Anos Iniciais","AF":"Anos Finais","EM":"Ensino Médio"}
            )
            fig = px.bar(
                gre_long, x="Matrículas", y="GRE", color="Segmento",
                orientation="h", barmode="stack",
                color_discrete_map={"Anos Iniciais": AZUL2,"Anos Finais": AZUL,"Ensino Médio": AMARELO},
                title="Matrículas por GRE e Segmento",
            )
            fig.update_traces(marker_line_width=0)
            plotly_defaults(fig, 520)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            mun_mat = df_m.groupby("MUNICIPIO")["TOTAL"].sum().reset_index()
            mun_mat = mun_mat.sort_values("TOTAL", ascending=False).head(20)
            fig2 = px.bar(
                mun_mat.sort_values("TOTAL"),
                x="TOTAL", y="MUNICIPIO", orientation="h",
                color="TOTAL",
                color_continuous_scale=[[0,"#c8ddf5"],[1,AZUL]],
                text="TOTAL",
                title="Top 20 Municípios por Matrículas",
            )
            fig2.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig2.update_coloraxes(showscale=False)
            plotly_defaults(fig2, 520)
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        top_n = st.slider("Exibir top N escolas", 10, 50, 25, key="top_esc_mat")
        df_top = df_m[["NOME_ESCOLA","GRE","MUNICIPIO","TIPO","TOTAL",
                        "ENSINO FUNDAMENTAL (ANOS INICIAIS)",
                        "ENSINO FUNDAMENTAL (ANOS FINAIS)","ENSINO MÉDIO"]].copy()
        df_top = df_top.dropna(subset=["TOTAL"]).sort_values("TOTAL", ascending=False).head(top_n)
        df_top.columns = ["Escola","GRE","Município","Tipo","Total","An. Iniciais","An. Finais","Ens. Médio"]
        fig3 = px.bar(
            df_top.sort_values("Total"),
            x="Total", y="Escola", orientation="h",
            color="GRE",
            color_discrete_sequence=QUAL_COLORS,
            text="Total",
            title=f"Top {top_n} escolas por total de matrículas",
        )
        fig3.update_traces(textposition="outside", marker_line_width=0)
        plotly_defaults(fig3, max(400, top_n * 22))
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        series_cols = ["1º ANO","2º ANO","3º ANO","4º ANO","5º ANO",
                       "6º ANO","7º ANO","8º ANO","9º ANO",
                       "1ª SÉRIE","2ª SÉRIE","3ª SÉRIE"]
        series_sums = []
        for col in series_cols:
            if col in df_m.columns:
                series_sums.append({"Série": col, "Matrículas": df_m[col].sum()})
        df_series = pd.DataFrame(series_sums).dropna()

        c_bar, c_pie = st.columns(2)
        with c_bar:
            fig4 = px.bar(
                df_series, x="Série", y="Matrículas",
                color="Matrículas",
                color_continuous_scale=[[0,"#c8ddf5"],[1,AZUL]],
                text="Matrículas",
                title="Matrículas por série",
            )
            fig4.update_traces(
                texttemplate="%{text:,.0f}", textposition="outside",
                marker_line_width=0
            )
            fig4.update_coloraxes(showscale=False)
            plotly_defaults(fig4, 380)
            st.plotly_chart(fig4, use_container_width=True)

        with c_pie:
            segmentos = {
                "Anos Iniciais (1-5)": df_series[df_series["Série"].str.contains("ANO")
                    & df_series["Série"].str.extract(r"(\d+)")[0].astype(float).le(5)]["Matrículas"].sum(),
                "Anos Finais (6-9)": df_series[df_series["Série"].str.contains("ANO")
                    & df_series["Série"].str.extract(r"(\d+)")[0].astype(float).ge(6)]["Matrículas"].sum(),
                "Ensino Médio (1-3ª)": df_series[df_series["Série"].str.contains("SÉRIE")]["Matrículas"].sum(),
            }
            df_seg = pd.DataFrame(list(segmentos.items()), columns=["Segmento","Matrículas"])
            fig5 = px.pie(
                df_seg, values="Matrículas", names="Segmento",
                color_discrete_sequence=[AZUL2, AZUL, AMARELO],
                hole=0.55,
                title="Proporção por segmento",
            )
            fig5.update_traces(textposition="outside", textinfo="percent+label")
            plotly_defaults(fig5, 380)
            st.plotly_chart(fig5, use_container_width=True)

    with tab4:
        section("📄 Dados de Matrículas — Tabela Completa")
        df_show = df_m[["NOME_ESCOLA","GRE","MUNICIPIO","TIPO","TOTAL",
                         "ENSINO FUNDAMENTAL (ANOS INICIAIS)",
                         "ENSINO FUNDAMENTAL (ANOS FINAIS)","ENSINO MÉDIO"]].copy()
        df_show.columns = ["Escola","GRE","Município","Tipo","Total","Anos Iniciais","Anos Finais","Ensino Médio"]
        df_show = df_show.dropna(subset=["Total"]).sort_values("Total", ascending=False)
        st.dataframe(
            df_show.reset_index(drop=True),
            use_container_width=True, height=420
        )
        csv_export = df_show.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv_export, "matriculas_filtradas.csv", "text/csv")


# ════════════════════════════════════════════════════════════
#  PÁGINA 3 — IDEB & QUALIDADE
# ════════════════════════════════════════════════════════════

elif pagina.startswith("📈"):
    header(
        "IDEB & Qualidade da Educação",
        "Indicadores históricos de desempenho 2017, 2019, 2021 e 2023",
        badge="Ensino Médio (EM) · Anos Finais (AF) · Anos Iniciais (AI)"
    )

    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fi1, fi2 = st.columns(2)
        with fi1:
            f_gre_i = st.multiselect("GRE", GRE_LIST, placeholder="Todas", key="i_gre")
        with fi2:
            f_mun_i = st.multiselect("Município", MUN_LIST, placeholder="Todos", key="i_mun")
        st.markdown('</div>', unsafe_allow_html=True)

    df_i = escolas_mat.copy()
    if f_gre_i: df_i = df_i[df_i["GRE"].isin(f_gre_i)]
    if f_mun_i: df_i = df_i[df_i["MUNICIPIO"].isin(f_mun_i)]

    ANOS_IDEB = ["2017", "2019", "2021", "2023"]
    SEGS = {
        "EM": "Ensino Médio (EM)",
        "AI": "Anos Iniciais (AI)",
        "AF": "Anos Finais (AF)",
    }

    def safe_mean(df, col):
        if col not in df.columns: return None
        v = pd.to_numeric(df[col], errors="coerce").dropna()
        return round(v.mean(), 2) if len(v) > 0 else None

    def safe_count(df, col):
        if col not in df.columns: return 0
        return int(pd.to_numeric(df[col], errors="coerce").dropna().__len__())

    # ── KPIs: melhor ano disponível por segmento ─────────────
    def best_val(df, seg):
        """Return mean and year for the most recent year with data for a segment."""
        for ano in reversed(ANOS_IDEB):
            v = safe_mean(df, f"IDEB {seg} {ano}")
            if v:
                return v, ano
        return None, None

    c1, c2, c3 = st.columns(3)
    with c1:
        v, ano_v = best_val(df_i, "EM")
        kpi(
            f"IDEB Ensino Médio (EM) {ano_v or ''}",
            f"{v:.2f}" if v else "—",
            f"{safe_count(df_i, f'IDEB EM {ano_v}')} escolas com dado" if ano_v else "Sem dados",
            icon="🎓"
        )
    with c2:
        v2, ano_v2 = best_val(df_i, "AF")
        kpi(
            f"IDEB Anos Finais (AF) {ano_v2 or ''}",
            f"{v2:.2f}" if v2 else "—",
            f"{safe_count(df_i, f'IDEB AF {ano_v2}')} escolas com dado" if ano_v2 else "Sem dados",
            "green", "📘"
        )
    with c3:
        v3, ano_v3 = best_val(df_i, "AI")
        kpi(
            f"IDEB Anos Iniciais (AI) {ano_v3 or ''}",
            f"{v3:.2f}" if v3 else "—",
            f"{safe_count(df_i, f'IDEB AI {ano_v3}')} escolas com dado" if ano_v3 else "Sem dados",
            "yellow", "📗"
        )

    divider()

    tab_evo, tab_gre, tab_scatter, tab_rank = st.tabs([
        "📊 Evolução Temporal", "🗂️ Por GRE", "🔗 Cruzamento Dados", "🏆 Ranking"
    ])

    with tab_evo:
        # ── Linha do tempo: todos os anos por segmento ──────
        section("📈 Evolução do IDEB médio por Segmento (2017–2023)")
        evo_data = []
        for cod, label in SEGS.items():
            for ano in ANOS_IDEB:
                v = safe_mean(df_i, f"IDEB {cod} {ano}")
                if v:
                    cnt = safe_count(df_i, f"IDEB {cod} {ano}")
                    evo_data.append({"Ano": ano, "IDEB Médio": v, "Segmento": label, "Escolas": cnt})

        if evo_data:
            df_evo = pd.DataFrame(evo_data)
            fig_line = px.line(
                df_evo, x="Ano", y="IDEB Médio", color="Segmento",
                markers=True,
                color_discrete_map={
                    "Ensino Médio (EM)": AZUL,
                    "Anos Finais (AF)": AMARELO,
                    "Anos Iniciais (AI)": VERDE,
                },
                text="IDEB Médio",
                hover_data={"Escolas": True},
                title="Evolução do IDEB médio — todos os segmentos",
            )
            fig_line.update_traces(texttemplate="%{text:.2f}", textposition="top center", line_width=3)
            plotly_defaults(fig_line, height=420)
            st.plotly_chart(fig_line, use_container_width=True)

            # Variação percentual entre primeiro e último ano com dado
            section("📊 Variação IDEB: primeiro → último ano disponível")
            delta_rows = []
            for cod, label in SEGS.items():
                vals = [(ano, safe_mean(df_i, f"IDEB {cod} {ano}")) for ano in ANOS_IDEB]
                vals = [(a, v) for a, v in vals if v]
                if len(vals) >= 2:
                    a_ini, v_ini = vals[0]
                    a_fim, v_fim = vals[-1]
                    delta = round(v_fim - v_ini, 2)
                    delta_pct = round((v_fim - v_ini) / v_ini * 100, 1)
                    delta_rows.append({
                        "Segmento": label,
                        f"IDEB {a_ini}": v_ini,
                        f"IDEB {a_fim}": v_fim,
                        "Variação": delta,
                        "Variação %": f"{'+' if delta >= 0 else ''}{delta_pct}%"
                    })
            if delta_rows:
                st.dataframe(pd.DataFrame(delta_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Sem dados suficientes para gerar o comparativo temporal.")

        divider()

        # ── Histograma distribuição — segmento/ano selecionável ──
        section("📉 Distribuição do IDEB por Segmento e Ano")
        hcol1, hcol2 = st.columns(2)
        with hcol1:
            h_seg = st.selectbox("Segmento", list(SEGS.keys()),
                                 format_func=lambda k: SEGS[k], key="h_seg")
        with hcol2:
            anos_disp = [a for a in ANOS_IDEB if safe_count(df_i, f"IDEB {h_seg} {a}") > 0]
            h_ano = st.selectbox("Ano", anos_disp if anos_disp else ANOS_IDEB, key="h_ano")

        ideb_dist = pd.to_numeric(df_i.get(f"IDEB {h_seg} {h_ano}"), errors="coerce").dropna()
        if len(ideb_dist) > 0:
            fig_hist = px.histogram(
                ideb_dist, nbins=15,
                title=f"Distribuição IDEB {SEGS[h_seg]} {h_ano}",
                labels={"value": "IDEB", "count": "Escolas"},
                color_discrete_sequence=[AZUL],
            )
            fig_hist.update_traces(marker_line_color="white", marker_line_width=1)
            plotly_defaults(fig_hist, 320)
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info(f"Sem dados de IDEB {SEGS[h_seg]} {h_ano} para a seleção atual.")

    with tab_gre:
        # ── Por GRE: segmento e ano selecionáveis ───────────
        gcol1, gcol2 = st.columns(2)
        with gcol1:
            g_seg = st.selectbox("Segmento", list(SEGS.keys()),
                                 format_func=lambda k: SEGS[k], key="g_seg")
        with gcol2:
            g_ano = st.selectbox("Ano", ANOS_IDEB[::-1], key="g_ano")

        col_gre_ideb = f"IDEB {g_seg} {g_ano}"
        gre_ideb = (
            df_i.groupby("GRE")[col_gre_ideb]
            .apply(lambda x: pd.to_numeric(x, errors="coerce").mean())
            .dropna()
            .reset_index()
            .rename(columns={col_gre_ideb: "IDEB_Médio"})
            .sort_values("IDEB_Médio", ascending=False)
        )

        if len(gre_ideb) > 0:
            fig_gre = px.bar(
                gre_ideb, x="GRE", y="IDEB_Médio",
                color="IDEB_Médio",
                color_continuous_scale=[[0, "#c8ddf5"], [1, AZUL]],
                text=gre_ideb["IDEB_Médio"].round(2),
                title=f"IDEB médio — {SEGS[g_seg]} {g_ano} por GRE",
            )
            fig_gre.update_traces(textposition="outside", marker_line_width=0)
            fig_gre.update_coloraxes(showscale=False)
            plotly_defaults(fig_gre, 430)
            st.plotly_chart(fig_gre, use_container_width=True)

            # Evolução por GRE — segmento selecionado
            section(f"📈 Evolução {SEGS[g_seg]} por GRE (todos os anos disponíveis)")
            gre_ev = []
            for gre_val in df_i["GRE"].dropna().unique():
                sub = df_i[df_i["GRE"] == gre_val]
                for ano in ANOS_IDEB:
                    m = safe_mean(sub, f"IDEB {g_seg} {ano}")
                    if m:
                        gre_ev.append({"GRE": gre_val, "Ano": ano, "IDEB": m})
            if gre_ev:
                df_gre_ev = pd.DataFrame(gre_ev)
                fig_gev = px.line(
                    df_gre_ev, x="Ano", y="IDEB", color="GRE",
                    markers=True,
                    color_discrete_sequence=QUAL_COLORS,
                    title=f"Evolução IDEB {SEGS[g_seg]} por GRE",
                )
                plotly_defaults(fig_gev, 420)
                st.plotly_chart(fig_gev, use_container_width=True)
        else:
            st.info(f"Sem dados de IDEB {SEGS[g_seg]} {g_ano} para a seleção atual.")

    with tab_scatter:
        # ── Cruzamento: IDEB vs Matrículas ─────────────────
        sc1, sc2 = st.columns(2)
        with sc1:
            sc_seg = st.selectbox("Segmento", list(SEGS.keys()),
                                  format_func=lambda k: SEGS[k], key="sc_seg")
        with sc2:
            sc_ano = st.selectbox("Ano", ANOS_IDEB[::-1], key="sc_ano")

        sc_col = f"IDEB {sc_seg} {sc_ano}"
        section(f"🔗 Cruzamento: {SEGS[sc_seg]} {sc_ano} × Total de Matrículas")

        cols_needed = ["NOME_ESCOLA", "GRE", "MUNICIPIO", "TIPO", sc_col, "TOTAL"]
        sc_df = df_i[[c for c in cols_needed if c in df_i.columns]].dropna()
        if len(sc_df) > 0 and sc_col in sc_df.columns and "TOTAL" in sc_df.columns:
            fig_sc = px.scatter(
                sc_df,
                x="TOTAL", y=sc_col,
                color="GRE",
                hover_name="NOME_ESCOLA",
                hover_data={"MUNICIPIO": True, "TIPO": True},
                size=sc_col,
                size_max=20,
                color_discrete_sequence=QUAL_COLORS,
                title=f"IDEB {SEGS[sc_seg]} {sc_ano} vs. Matrículas",
                labels={"TOTAL": "Total de Matrículas", sc_col: f"IDEB {SEGS[sc_seg]}"},
            )
            plotly_defaults(fig_sc, 460)
            st.plotly_chart(fig_sc, use_container_width=True)
        else:
            st.info("Dados insuficientes para o cruzamento com os filtros atuais.")

    with tab_rank:
        ANOS_IDEB_RANK = ["2017", "2019", "2021", "2023"]
        seg_opts = [f"IDEB {cod} {ano}" for cod in ["EM", "AI", "AF"] for ano in ANOS_IDEB_RANK]
        col_seg = st.selectbox(
            "Segmento / Ano",
            seg_opts,
            format_func=lambda c: c.replace("EM", "Ensino Médio").replace("AI", "Anos Iniciais").replace("AF", "Anos Finais"),
            key="rank_seg"
        )
        n_rank = st.slider("Número de escolas", 5, 30, 15, key="n_rank")

        rank_df = df_i[["NOME_ESCOLA", "GRE", "MUNICIPIO", col_seg]].copy()
        rank_df.columns = ["Escola", "GRE", "Município", "IDEB"]
        rank_df["IDEB"] = pd.to_numeric(rank_df["IDEB"], errors="coerce")
        rank_df = rank_df.dropna(subset=["IDEB"])

        col_best, col_worst = st.columns(2)
        with col_best:
            section("🏆 Melhores Desempenhos")
            best = rank_df.nlargest(n_rank, "IDEB").reset_index(drop=True)
            best.index += 1
            fig_best = px.bar(
                best.sort_values("IDEB"),
                x="IDEB", y="Escola", orientation="h",
                color="IDEB",
                color_continuous_scale=[[0, "#c8f5d5"], [1, VERDE]],
                text="IDEB",
                title="",
            )
            fig_best.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_best.update_coloraxes(showscale=False)
            plotly_defaults(fig_best, max(300, n_rank * 26))
            st.plotly_chart(fig_best, use_container_width=True)

        with col_worst:
            section("⚠️ Menores Desempenhos")
            worst = rank_df.nsmallest(n_rank, "IDEB").reset_index(drop=True)
            worst.index += 1
            fig_worst = px.bar(
                worst.sort_values("IDEB", ascending=False),
                x="IDEB", y="Escola", orientation="h",
                color="IDEB",
                color_continuous_scale=[[0, VERMELHO], [1, "#ffcdd2"]],
                text="IDEB",
                title="",
            )
            fig_worst.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_worst.update_coloraxes(showscale=False)
            plotly_defaults(fig_worst, max(300, n_rank * 26))
            st.plotly_chart(fig_worst, use_container_width=True)

# ════════════════════════════════════════════════════════════
#  PÁGINA 4 — GESTÃO & ACOMPANHAMENTO
# ════════════════════════════════════════════════════════════

elif pagina.startswith("🗺️"):
    header(
        "Gestão & Acompanhamento",
        "Funcionamento, planos de contingência e consultores",
        badge="Painel de Controle"
    )

    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fg1, fg2 = st.columns(2)
        with fg1:
            f_gre_g = st.multiselect("GRE", GRE_LIST, placeholder="Todas", key="g_gre")
        with fg2:
            func_list = sorted(escolas_full["Funcionamento atual"].dropna().unique())
            f_func = st.multiselect("Funcionamento", func_list, placeholder="Todos", key="g_func")
        st.markdown('</div>', unsafe_allow_html=True)

    df_g = escolas_full.copy()
    if f_gre_g:  df_g = df_g[df_g["GRE"].isin(f_gre_g)]
    if f_func:   df_g = df_g[df_g["Funcionamento atual"].isin(f_func)]

    # KPIs
    n_pres  = (df_g["Funcionamento atual"] == "Presencial").sum()
    n_hibr  = (df_g["Funcionamento atual"] == "Híbrido (remoto e presencial)").sum()
    n_elaborado = df_g["Situação do Plano de Contigência"].str.contains(
        "Elaborado", na=False).sum()
    n_em_elab = df_g["Situação do Plano de Contigência"].str.contains(
        "elaboração", na=False).sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Presencial", fmt_num(n_pres), "escolas", "green", "✅")
    with c2: kpi("Híbrido", fmt_num(n_hibr), "escolas", "yellow", "🔄")
    with c3: kpi("Plano Elaborado", fmt_num(n_elaborado), "e em execução", icon="📋")
    with c4: kpi("Em Elaboração", fmt_num(n_em_elab), "plano pendente", "red", "⏳")

    divider()

    col_l, col_r = st.columns(2)

    with col_l:
        section("🔄 Funcionamento por GRE")
        func_gre = df_g.groupby(["GRE","Funcionamento atual"]).size().reset_index(name="Escolas")
        fig_f = px.bar(
            func_gre, x="GRE", y="Escolas", color="Funcionamento atual",
            color_discrete_map={
                "Presencial": VERDE,
                "Híbrido (remoto e presencial)": AMARELO,
            },
            barmode="stack",
            title="Funcionamento por GRE",
        )
        fig_f.update_traces(marker_line_width=0)
        plotly_defaults(fig_f, 400)
        st.plotly_chart(fig_f, use_container_width=True)

    with col_r:
        section("📋 Plano de Contingência por GRE")
        plan_gre = df_g.groupby(["GRE","Situação do Plano de Contigência"]).size().reset_index(name="Escolas")
        plan_gre["Situação"] = plan_gre["Situação do Plano de Contigência"].fillna("Não informado")
        fig_p = px.bar(
            plan_gre, x="GRE", y="Escolas", color="Situação",
            color_discrete_map={
                "Elaborado e em execução": VERDE,
                "Em elaboração": AMARELO,
                "Não informado": "#ccc",
            },
            barmode="stack",
            title="Status do Plano por GRE",
        )
        fig_p.update_traces(marker_line_width=0)
        plotly_defaults(fig_p, 400)
        st.plotly_chart(fig_p, use_container_width=True)

    divider()

    section("👥 Consultores de Gestão por Escola")
    df_g_show = df_g[[
        "NOME_ESCOLA","GRE","MUNICIPIO","TIPO",
        "Funcionamento atual","Situação do Plano de Contigência",
        "Consultores de gestão","Período/semana",
        "Data do alinhamento","Observações e encaminhamentos"
    ]].copy()
    df_g_show.columns = [
        "Escola","GRE","Município","Tipo",
        "Funcionamento","Plano de Contingência",
        "Consultores","Período","Alinhamento","Observações"
    ]

    search_g = st.text_input("🔎 Buscar escola ou consultor", key="search_g")
    if search_g:
        mask = df_g_show.apply(
            lambda r: r.astype(str).str.contains(search_g, case=False).any(), axis=1
        )
        df_g_show = df_g_show[mask]

    st.dataframe(df_g_show.reset_index(drop=True), use_container_width=True, height=420)

    csv_g = df_g_show.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar CSV", csv_g, "gestao_filtrada.csv", "text/csv")


# ════════════════════════════════════════════════════════════
#  PÁGINA 5 — ESCOLAS DO AMANHÃ
# ════════════════════════════════════════════════════════════

elif pagina.startswith("🏫"):
    header(
        "Escolas do Amanhã",
        "Programa de expansão e modernização das ECIs e ECITs",
        badge="Programa Estratégico"
    )

    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fa1, fa2, fa3 = st.columns(3)
        gre_amanha = sorted(amanha["GRE"].dropna().unique())
        mun_amanha = sorted(amanha["Município"].dropna().unique())
        with fa1:
            f_gre_a = st.multiselect("GRE", gre_amanha, placeholder="Todas", key="a_gre")
        with fa2:
            f_mun_a = st.multiselect("Município", mun_amanha, placeholder="Todos", key="a_mun")
        with fa3:
            mec_filter = st.selectbox("Convênio MEC", ["Todos","Sim","Não"], key="a_mec")
        st.markdown('</div>', unsafe_allow_html=True)

    df_a = amanha.copy()
    if f_gre_a: df_a = df_a[df_a["GRE"].isin(f_gre_a)]
    if f_mun_a: df_a = df_a[df_a["Município"].isin(f_mun_a)]
    if mec_filter != "Todos": df_a = df_a[df_a["MEC"] == mec_filter]

    total_a = df_a["Matrículas"].sum()
    maker_count = (df_a["MAKER"] == "SIM").sum() if "MAKER" in df_a else 0
    eti1_count = df_a["ETI 1"].notna().sum()
    mec_count = (df_a["MEC"] == "Sim").sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Escolas no Programa", fmt_num(len(df_a)), "selecionadas", icon="🏫")
    with c2: kpi("Total Matrículas", fmt_num(total_a), "alunos", "yellow", "👩‍🎓")
    with c3: kpi("Com Convênio MEC", fmt_num(mec_count), "escolas", "green", "🏛️")
    with c4: kpi("Com ETI", fmt_num(eti1_count), "escolas", icon="⏰")

    divider()

    tab_vis, tab_mat, tab_tab = st.tabs(["📊 Visualizações", "📈 Matrículas", "📄 Tabela"])

    with tab_vis:
        col_l, col_r = st.columns(2)
        with col_l:
            gre_a_cnt = df_a.groupby("GRE").size().reset_index(name="Escolas")
            fig_a1 = px.bar(
                gre_a_cnt.sort_values("Escolas"),
                x="Escolas", y="GRE", orientation="h",
                color="Escolas",
                color_continuous_scale=[[0,"#c8ddf5"],[1,AZUL]],
                text="Escolas",
                title="Escolas do Amanhã por GRE",
            )
            fig_a1.update_traces(textposition="outside", marker_line_width=0)
            fig_a1.update_coloraxes(showscale=False)
            plotly_defaults(fig_a1, 420)
            st.plotly_chart(fig_a1, use_container_width=True)

        with col_r:
            tipo_a = df_a["Tipo"].value_counts().reset_index()
            tipo_a.columns = ["Tipo","Qtd"]
            fig_a2 = px.pie(
                tipo_a, values="Qtd", names="Tipo",
                color_discrete_sequence=QUAL_COLORS,
                hole=0.5,
                title="Distribuição por tipo",
            )
            fig_a2.update_traces(textposition="outside", textinfo="percent+label")
            plotly_defaults(fig_a2, 350)
            st.plotly_chart(fig_a2, use_container_width=True)

            mec_a = df_a["MEC"].value_counts().reset_index()
            mec_a.columns = ["MEC","Qtd"]
            fig_a3 = px.pie(
                mec_a, values="Qtd", names="MEC",
                color_discrete_map={"Sim": VERDE,"Não": "#ccc"},
                hole=0.5,
                title="Convênio MEC",
            )
            plotly_defaults(fig_a3, 250)
            st.plotly_chart(fig_a3, use_container_width=True)

    with tab_mat:
        top_a = st.slider("Top N escolas por matrículas", 10, 50, 25, key="top_a")
        mat_a = df_a.nlargest(top_a, "Matrículas")

        fig_a4 = px.bar(
            mat_a.sort_values("Matrículas"),
            x="Matrículas", y="Escola", orientation="h",
            color="GRE",
            color_discrete_sequence=QUAL_COLORS,
            text="Matrículas",
            title=f"Top {top_a} escolas por matrículas — Escolas do Amanhã",
        )
        fig_a4.update_traces(textposition="outside", marker_line_width=0)
        plotly_defaults(fig_a4, max(400, top_a * 22))
        st.plotly_chart(fig_a4, use_container_width=True)

        # Matrículas por município
        mun_a_mat = df_a.groupby("Município")["Matrículas"].sum().reset_index()
        mun_a_mat = mun_a_mat.sort_values("Matrículas", ascending=False).head(20)
        fig_a5 = px.bar(
            mun_a_mat, x="Município", y="Matrículas",
            color="Matrículas",
            color_continuous_scale=[[0,"#c8ddf5"],[1,AZUL]],
            title="Matrículas por município — top 20",
        )
        fig_a5.update_traces(marker_line_width=0)
        fig_a5.update_coloraxes(showscale=False)
        plotly_defaults(fig_a5, 380)
        st.plotly_chart(fig_a5, use_container_width=True)

    with tab_tab:
        section("📄 Lista Completa — Escolas do Amanhã")
        df_a_show = df_a[["Escola","GRE","Município","Tipo","MEC","Matrículas","Modalidades","ETI 1","ETI 2","MAKER"]].copy()
        st.dataframe(df_a_show.reset_index(drop=True), use_container_width=True, height=430)
        csv_a = df_a_show.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv_a, "escolas_amanha_filtradas.csv", "text/csv")


# ════════════════════════════════════════════════════════════
#  PÁGINA 6 — CONTATOS & EQUIPE
# ════════════════════════════════════════════════════════════

elif pagina.startswith("📞"):
    header(
        "Contatos & Equipe",
        "Diretores, coordenadores, CAF e equipe da secretaria",
        badge="Diretório 2026"
    )

    tab_dir, tab_cp, tab_equipe = st.tabs([
        "👔 Diretores", "📚 Coord. Pedagógico & CAF", "🏢 Equipe Interna"
    ])

    with tab_dir:
        section("🔎 Busca por Escola ou Diretor")
        with st.container():
            st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
            cd1, cd2 = st.columns(2)
            with cd1:
                f_gre_c = st.multiselect("GRE", GRE_LIST, placeholder="Todas", key="c_gre")
            with cd2:
                search_dir = st.text_input("Buscar nome ou escola", key="search_dir")
            st.markdown('</div>', unsafe_allow_html=True)

        df_c = contatos.copy()
        if f_gre_c: df_c = df_c[df_c["GRE"].isin(f_gre_c)]
        if search_dir:
            mask = (
                df_c["NOME_ESCOLA"].str.contains(search_dir, case=False, na=False) |
                df_c["DIRETOR(A) ESCOLAR"].str.contains(search_dir, case=False, na=False)
            )
            df_c = df_c[mask]

        kpi("Diretores localizados", fmt_num(len(df_c)), "escolas na seleção", icon="👔")
        st.markdown("<br>", unsafe_allow_html=True)

        for _, row in df_c.head(80).iterrows():
            st.markdown(f"""
            <div class="contact-card">
              <span class="contact-tag">{row['GRE']}</span>
              <h4>🏫 {row['NOME_ESCOLA']}</h4>
              <p>👔 <strong>Diretor(a):</strong> {row.get('DIRETOR(A) ESCOLAR','—')}</p>
              <p>📧 {row.get('E-MAIL DO DIRETOR(A) ESCOLAR','—')}</p>
              <p>📱 {row.get('CONTATO DO DIRETOR(A) ESCOLAR','—')}</p>
            </div>""", unsafe_allow_html=True)

        if len(df_c) > 80:
            st.info(f"Exibindo 80 de {len(df_c)} resultados. Use os filtros para refinar.")

    with tab_cp:
        section("📋 Coordenadores Pedagógicos e CAF")
        df_cp = contatos[["GRE","NOME_ESCOLA",
                           "COORDENADOR PEDAGÓGICO (CP)","E-MAIL DO COORDENADOR PEDAGÓGICO (CP)",
                           "CONTATO DO COORDENADOR PEDAGÓGICO (CP)",
                           "COORDENADOR ADMINISTRATIVO  FINANCEIRO (CAF)",
                           "E-MAIL DO  COORDENADOR  ADMINISTRATIVO  FINANCEIRO (CAF)",
                           "CONTATO DO  COORDENADOR  ADMINISTRATIVO  FINANCEIRO (CAF)",
                           "SECRETÁRIO ESCOLAR","E-MAIL DO SECRETÁRIO ESCOLAR",
                           "CONTATO DO SECRETÁRIO ESCOLAR"]].copy()
        df_cp.columns = ["GRE","Escola","Coord. Pedagógico","E-mail CP","Contato CP",
                         "CAF","E-mail CAF","Contato CAF",
                         "Secretário Escolar","E-mail Sec.","Contato Sec."]

        search_cp = st.text_input("🔎 Buscar", key="search_cp")
        if search_cp:
            mask = df_cp.apply(lambda r: r.astype(str).str.contains(search_cp, case=False).any(), axis=1)
            df_cp = df_cp[mask]

        st.dataframe(df_cp.reset_index(drop=True), use_container_width=True, height=450)
        st.download_button("⬇️ Exportar", df_cp.to_csv(index=False).encode(), "coordenadores.csv", "text/csv")

    with tab_equipe:
        section("🏢 Equipe Interna da Secretaria")

        pasta_list = sorted(setor["PASTA"].dropna().unique()) if "PASTA" in setor.columns else []
        f_pasta = st.multiselect("Filtrar por setor/pasta",
                                  pasta_list if pasta_list else [], key="f_pasta")

        df_eq = setor.copy()
        if f_pasta and "PASTA" in df_eq.columns:
            df_eq = df_eq[df_eq["PASTA"].isin(f_pasta)]

        # Cards por pasta
        col_names = list(setor.columns)
        pasta_col = "PASTA" if "PASTA" in col_names else col_names[1]
        nome_col = "NOME" if "NOME" in col_names else col_names[2]
        cargo_col = "CARGO/FUNÇÃO" if "CARGO/FUNÇÃO" in col_names else col_names[0]
        dem_col = "DEMANDAS FIXAS" if "DEMANDAS FIXAS" in col_names else (col_names[3] if len(col_names) > 3 else None)

        # Treemap de equipe por pasta
        if pasta_col in df_eq.columns:
            pasta_cnt = df_eq[pasta_col].value_counts().reset_index()
            pasta_cnt.columns = ["Setor","Membros"]
            fig_eq = px.treemap(
                pasta_cnt, path=["Setor"], values="Membros",
                color="Membros",
                color_continuous_scale=[[0,"#c8ddf5"],[1,AZUL]],
                title="Membros por setor interno",
            )
            plotly_defaults(fig_eq, 320)
            st.plotly_chart(fig_eq, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        pastas = df_eq[pasta_col].dropna().unique() if pasta_col in df_eq.columns else []
        for pasta in pastas:
            sub_eq = df_eq[df_eq[pasta_col] == pasta]
            with st.expander(f"📁 {pasta}  ({len(sub_eq)} membros)"):
                for _, row in sub_eq.iterrows():
                    dem = str(row.get(dem_col, "")) if dem_col else ""
                    st.markdown(f"""
                    <div class="contact-card">
                      <span class="contact-tag">{row.get(pasta_col,'')}</span>
                      <h4>👤 {row.get(nome_col,'—')}</h4>
                      <p>🏷️ <strong>Cargo:</strong> {row.get(cargo_col,'—')}</p>
                      {'<p>📌 ' + dem + '</p>' if dem and dem != 'nan' else ''}
                    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  PÁGINA 7 — EXPLORADOR DE ESCOLAS
# ════════════════════════════════════════════════════════════

elif pagina.startswith("🔍"):
    header(
        "Explorador de Escolas",
        "Ficha completa por escola — busque por nome ou INEP",
        badge="Consulta Rápida"
    )

    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fe1, fe2, fe3 = st.columns(3)
        with fe1:
            f_gre_e = st.multiselect("GRE", GRE_LIST, placeholder="Todas", key="e_gre")
        with fe2:
            f_mun_e = st.multiselect("Município", MUN_LIST, placeholder="Todos", key="e_mun")
        with fe3:
            f_tipo_e = st.multiselect("Tipo", TIPO_LIST, placeholder="Todos os tipos", key="e_tipo")
        search_e = st.text_input("🔎 Buscar por nome ou código INEP", key="search_e")
        st.markdown('</div>', unsafe_allow_html=True)

    # Merge completo
    df_exp = escolas_mat.merge(
        contatos[["CODIGO_INEP","DIRETOR(A) ESCOLAR",
                   "CONTATO DO DIRETOR(A) ESCOLAR","E-MAIL DO DIRETOR(A) ESCOLAR",
                   "COORDENADOR PEDAGÓGICO (CP)","CONTATO DO COORDENADOR PEDAGÓGICO (CP)"]],
        on="CODIGO_INEP", how="left"
    )

    if f_gre_e:  df_exp = df_exp[df_exp["GRE"].isin(f_gre_e)]
    if f_mun_e:  df_exp = df_exp[df_exp["MUNICIPIO"].isin(f_mun_e)]
    if f_tipo_e: df_exp = df_exp[df_exp["TIPO"].isin(f_tipo_e)]
    if search_e:
        mask = (
            df_exp["NOME_ESCOLA"].str.contains(search_e, case=False, na=False) |
            df_exp["CODIGO_INEP"].astype(str).str.contains(search_e, na=False)
        )
        df_exp = df_exp[mask]

    st.markdown(f"**{len(df_exp)} escola(s)** encontrada(s)")

    # Seleção de escola individual
    if len(df_exp) == 1:
        escola_sel = df_exp.iloc[0]
    else:
        opts = df_exp["NOME_ESCOLA"].tolist()
        if opts:
            selected_name = st.selectbox("Selecione uma escola para ver a ficha completa",
                                          ["— Ver todas —"] + opts, key="sel_escola")
        else:
            st.warning("Nenhuma escola encontrada com os filtros aplicados.")
            st.stop()

    if len(df_exp) > 0 and (len(df_exp) == 1 or (len(df_exp) > 1 and selected_name != "— Ver todas —")):
        if len(df_exp) > 1:
            escola_sel = df_exp[df_exp["NOME_ESCOLA"] == selected_name].iloc[0]

        divider()
        st.markdown(f"### 🏫 {escola_sel['NOME_ESCOLA']}")

        c_info, c_ideb = st.columns([2, 1])
        with c_info:
            section("📋 Informações Cadastrais")
            info_data = {
                "INEP": escola_sel.get("CODIGO_INEP","—"),
                "GRE": escola_sel.get("GRE","—"),
                "Município": escola_sel.get("MUNICIPIO","—"),
                "Tipo": escola_sel.get("TIPO","—"),
                "Modelo": escola_sel.get("MODELO","—"),
                "Convênio MEC": escola_sel.get("MEC","—"),
                "Anos Iniciais": escola_sel.get("ANOS INICIAIS","—"),
                "Anos Finais": escola_sel.get("ANOS FINAIS","—"),
                "Ensino Médio": escola_sel.get("ENSINO_MÉDIO_OFERTA","—"),
                "Ano Implantação": escola_sel.get("Ano de Implatação","—"),
                "Endereço": escola_sel.get("Endereço","—"),
                "CEP": escola_sel.get("CEP","—"),
                "Funcionamento": escola_sel.get("Funcionamento atual","—"),
                "Plano Contingência": escola_sel.get("Situação do Plano de Contigência","—"),
                "Consultores": escola_sel.get("Consultores de gestão","—"),
            }
            df_info = pd.DataFrame(list(info_data.items()), columns=["Campo","Valor"])
            st.table(df_info.set_index("Campo"))

        with c_ideb:
            section("📈 IDEB Histórico")
            ideb_hist = {}
            for seg, label in [("EM","Ens. Médio"),("AI","An. Iniciais"),("AF","An. Finais")]:
                row = {}
                for ano in ["2017","2019","2021","2023"]:
                    col_k = f"IDEB {seg} {ano}"
                    val = escola_sel.get(col_k, None)
                    if val and str(val) not in ["-","nan","None",""]:
                        try:
                            row[ano] = float(str(val))
                        except Exception:
                            row[ano] = None
                    else:
                        row[ano] = None
                if any(v is not None for v in row.values()):
                    ideb_hist[label] = row

            if ideb_hist:
                df_ideb = pd.DataFrame(ideb_hist).T.reset_index()
                df_ideb.columns = ["Segmento"] + [c for c in df_ideb.columns if c != "Segmento"]
                st.dataframe(df_ideb.set_index("Segmento"), use_container_width=True)

                # Mini gráfico IDEB
                ideb_lines = []
                for seg_label, row in ideb_hist.items():
                    for ano, val in row.items():
                        if val is not None:
                            ideb_lines.append({"Ano": ano, "IDEB": val, "Segmento": seg_label})
                if ideb_lines:
                    df_il = pd.DataFrame(ideb_lines)
                    fig_il = px.line(
                        df_il, x="Ano", y="IDEB", color="Segmento",
                        markers=True,
                        color_discrete_map={
                            "Ens. Médio": AZUL,
                            "An. Iniciais": VERDE,
                            "An. Finais": AMARELO,
                        },
                        title="",
                    )
                    plotly_defaults(fig_il, 250)
                    fig_il.update_layout(margin=dict(t=10))
                    st.plotly_chart(fig_il, use_container_width=True)
            else:
                st.info("Sem dados IDEB para esta escola.")

            section("🎓 Matrículas")
            mat_info = {
                "Anos Iniciais": escola_sel.get("ENSINO FUNDAMENTAL (ANOS INICIAIS)","—"),
                "Anos Finais": escola_sel.get("ENSINO FUNDAMENTAL (ANOS FINAIS)","—"),
                "Ensino Médio": escola_sel.get("ENSINO MÉDIO","—"),
                "Total": escola_sel.get("TOTAL","—"),
            }
            for k, v in mat_info.items():
                v_str = fmt_num(v) if str(v) not in ["—","nan","None",""] else "—"
                st.markdown(f"**{k}:** {v_str}")

        divider()
        section("📞 Contatos da Escola")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(f"""
            <div class="contact-card">
              <span class="contact-tag">Direção</span>
              <h4>👔 {escola_sel.get('DIRETOR(A) ESCOLAR','—')}</h4>
              <p>📧 {escola_sel.get('E-MAIL DO DIRETOR(A) ESCOLAR','—')}</p>
              <p>📱 {escola_sel.get('CONTATO DO DIRETOR(A) ESCOLAR','—')}</p>
            </div>""", unsafe_allow_html=True)
        with cc2:
            st.markdown(f"""
            <div class="contact-card">
              <span class="contact-tag">Coord. Pedagógico</span>
              <h4>📚 {escola_sel.get('COORDENADOR PEDAGÓGICO (CP)','—')}</h4>
              <p>📱 {escola_sel.get('CONTATO DO COORDENADOR PEDAGÓGICO (CP)','—')}</p>
            </div>""", unsafe_allow_html=True)

    elif len(df_exp) > 1:
        divider()
        section("📄 Resultados da Busca")
        cols_show = ["NOME_ESCOLA","GRE","MUNICIPIO","TIPO","TOTAL",
                     "Funcionamento atual","Situação do Plano de Contigência"]
        cols_show = [c for c in cols_show if c in df_exp.columns]
        df_res = df_exp[cols_show].copy()
        df_res.columns = [c.replace("NOME_ESCOLA","Escola")
                           .replace("MUNICIPIO","Município")
                           .replace("Funcionamento atual","Funcionamento")
                           .replace("Situação do Plano de Contigência","Plano")
                           for c in df_res.columns]
        st.dataframe(df_res.reset_index(drop=True), use_container_width=True, height=420)
        csv_exp = df_res.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv_exp, "escolas_resultado.csv", "text/csv")


# ── Footer ───────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Secretaria de Educação do Estado da Paraíba — SEE-PB &nbsp;|&nbsp;
  Dashboard de Monitoramento 2026 &nbsp;|&nbsp;
  Desenvolvido com Streamlit &amp; Plotly
</div>
""", unsafe_allow_html=True)
