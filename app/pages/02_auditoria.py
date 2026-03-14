"""
Logs Auditáveis — Histórico transparente de todos os ciclos aprovados.

O log não existe para vigiar; existe para proteger.
Cada registro prova, com data e nome, que um ser humano responsável
leu, revisou e assinou cada ação gerada pelo Escudo RAG.

Fonte: log_ciclos.jsonl (via carregar_ciclos)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from datetime import datetime

from core.auditoria import carregar_ciclos

# ── Cabeçalho ─────────────────────────────────────────────────────────────────

st.title("📋 Logs Auditáveis")
st.markdown(
    "Histórico completo de todos os ciclos aprovados pelo Escudo RAG. "
    "Cada entrada prova que **um humano leu, revisou e assinou** cada ação — "
    "nenhuma comunicação automatizada entra aqui sem o aval do professor e do gestor."
)
st.divider()

# ── Leitura sem cache — arquivo lido fresco a cada render ─────────────────────
# carregar_ciclos() não usa @st.cache_data intencionalmente:
# a Aba de Auditoria deve sempre refletir o estado real do arquivo em disco.

col_ctrl, col_info = st.columns([1, 3])
with col_ctrl:
    if st.button("🔄 Atualizar lista", type="secondary"):
        st.rerun()
with col_info:
    st.caption("Clique em **Atualizar lista** se acabou de aprovar um ciclo na Aba A Alavanca.")

st.divider()

todos_ciclos = carregar_ciclos(limite=100)

if not todos_ciclos:
    st.info(
        "Nenhum ciclo registrado ainda. "
        "Use **A Alavanca** para gerar, enviar e aprovar um ciclo completo.",
        icon="🗂️",
    )
else:
    st.caption(f"{len(todos_ciclos)} ciclo(s) encontrado(s) — exibindo do mais recente ao mais antigo.")

    for i, ciclo in enumerate(reversed(todos_ciclos)):
        # ── Monta o label do expander ──────────────────────────────────────────
        try:
            ts = datetime.fromisoformat(ciclo["timestamp"]).strftime("%d/%m/%Y %H:%M")
        except Exception:
            ts = ciclo.get("timestamp", "?")

        professor  = ciclo.get("professor", "?")
        aluno      = ciclo.get("aluno", "N/A")
        turma      = ciclo.get("turma", "?")
        tipo       = ciclo.get("tipo_comunicacao", "?")
        gestor     = ciclo.get("gestor_aprovador", "?")
        modo       = ciclo.get("modo_operacao", "?")

        label = (
            f"**{ts}** · {tipo} · "
            f"Aluno: _{aluno}_ · Turma: _{turma}_ · "
            f"Aprovado por: _{gestor}_"
        )

        with st.expander(label, expanded=(i == 0)):

            col_msg, col_resp = st.columns(2)

            with col_msg:
                st.markdown("**📤 Mensagem enviada pela escola**")
                st.code(ciclo.get("mensagem_professor", ""), language=None)

            with col_resp:
                st.markdown(
                    f"**💬 Resposta de: {ciclo.get('nome_responsavel', '?')}**"
                )
                st.info(ciclo.get("resposta_responsavel", ""), icon="💬")

            st.markdown("**🛡️ Raciocínio do Escudo RAG**")
            _rac = ciclo.get("raciocinio_rag", "").replace("* **", "\n\n* **").strip()
            st.markdown(_rac if _rac else "_Raciocínio não registrado._")

            fontes = ciclo.get("fontes_consultadas", [])
            if fontes:
                st.markdown("**📚 Fontes consultadas**")
                for fonte in fontes:
                    rel = fonte.get("relevancia", "?")
                    cor = "🟢" if rel == "Alta" else "🟡"
                    st.markdown(
                        f"- {cor} `{fonte.get('documento', '?')}` — "
                        f"Relevância: **{rel}**"
                    )

            st.markdown("**🔖 Metadados do ciclo**")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Professor(a)", professor)
            col_m2.metric("Aluno", aluno)
            col_m3.metric("Turma", turma)
            col_m4.metric("Modo", modo)
            st.caption(f"Timestamp ISO: `{ciclo.get('timestamp', '?')}`")

            with st.expander("🔍 Ver JSON bruto deste ciclo"):
                st.json(ciclo)
