"""
Logs Auditáveis — Histórico transparente de todas as ações aprovadas.

O log não existe para vigiar; existe para proteger.
Cada registro prova, com data e nome, que um ser humano responsável
leu, revisou e assinou cada ação gerada pelo Escudo RAG.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from datetime import datetime

from core.auditoria import carregar_logs


st.title("📋 Logs Auditáveis")
st.markdown(
    "Histórico completo de todas as ações geradas pelo Escudo RAG e **aprovadas por um humano**. "
    "Nenhuma ação automatizada entra neste registro sem a assinatura do professor responsável."
)
st.divider()

logs = carregar_logs()

if not logs:
    st.info(
        "Nenhuma ação registrada ainda. Use **A Alavanca** para gerar e aprovar documentos.",
        icon="🗂️",
    )
else:
    st.caption(f"{len(logs)} registro(s) encontrado(s).")

    for i, entrada in enumerate(reversed(logs)):
        ts = datetime.fromisoformat(entrada["timestamp"])
        label = f"**{ts.strftime('%d/%m/%Y %H:%M')}** — {entrada['tipo_tarefa']} — Aprovado por: _{entrada['aprovado_por']}_"

        with st.expander(label, expanded=(i == 0)):
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown("**Documento aprovado:**")
                st.code(entrada["rascunho_aprovado"], language=None)

            with col2:
                st.markdown("**Raciocínio do Escudo RAG:**")
                st.info(entrada["raciocinio_rag"], icon="🛡️")

                st.markdown("**Fontes consultadas:**")
                for fonte in entrada.get("fontes_consultadas", []):
                    st.markdown(
                        f"- `{fonte['documento']}` — Relevância: **{fonte['relevancia']}**"
                    )

                st.markdown("**Metadados:**")
                st.caption(f"Timestamp: `{entrada['timestamp']}`")
                st.caption(f"Modo de operação: `{entrada['modo_operacao']}`")
