"""
Ponto de entrada do Assistente Escola Modelo.
Execute com: streamlit run app/main.py
"""

import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")

sys.path.insert(0, _ROOT)

import streamlit as st
from config.settings import NOME_ESCOLA, MODO_OPERACAO, DIR_DOCUMENTOS

st.set_page_config(
    page_title=f"Assistente — {NOME_ESCOLA}",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

paginas = {
    "Início": [
        st.Page(
            os.path.join(_PAGES, "00_manifesto.py"),
            title="O Manifesto",
            icon="🏛️",
            default=True,
        ),
    ],
    "Assistente": [
        st.Page(
            os.path.join(_PAGES, "01_alavanca.py"),
            title="A Alavanca",
            icon="⚙️",
        ),
    ],
    "Governança": [
        st.Page(
            os.path.join(_PAGES, "02_auditoria.py"),
            title="Logs Auditáveis",
            icon="📋",
        ),
    ],
}

pagina_atual = st.navigation(paginas)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"### 🏫 {NOME_ESCOLA}")
    st.divider()

    if MODO_OPERACAO == "mock":
        st.warning("**Modo Simulação** — IA real desativada.", icon="🟡")
    else:
        st.success("**Modo RAG Ativo** — Escudo consultando documentos.", icon="🟢")

    st.caption("Toda ação exige aprovação humana.")

    # ── Card métrica da base (informativo — sem botões de indexação) ──────────
    if MODO_OPERACAO == "rag":
        st.divider()
        st.metric(
            label="Base Vetorial Ativa",
            value="4 Documentos Oficiais",
            delta="Latência Otimizada",
        )
        st.caption("Para re-indexar: `python setup_db.py`")

    st.divider()
    st.caption("Assistente Escola Modelo v0.3")

pagina_atual.run()
