"""
A Alavanca — Ciclo completo de comunicação escola-família.

Fluxo em 3 abas (Capítulos 3 e 4 do Manifesto):
  Aba 1 — Professor gera comunicado com Escudo RAG e envia para o responsável.
  Aba 2 — Simulação do celular da família: responsável lê e responde.
  Aba 3 — Gestor revisa o ciclo completo, aprova e o registro auditável é gravado.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from datetime import date, datetime

from core.escudo_rag import EscudoRAG
from core.auditoria import registrar_ciclo_completo, carregar_ciclos
from config.settings import NOME_ESCOLA, MODO_OPERACAO

# ── Constantes ────────────────────────────────────────────────────────────────

TIPOS_TAREFA = {
    "comunicado_pais": "📢 Comunicado para os Responsáveis",
    "registro_ocorrencia": "📝 Registro de Ocorrência",
    "licao_de_casa": "📚 Lição de Casa",
}

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Escudo RAG ── */
.bloco-escudo {
    background-color: #eef2ff;
    border-left: 5px solid #3b5bdb;
    padding: 1.2rem 1.5rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 1rem;
}
.bloco-escudo h4 { color: #1e3a5f; margin-top: 0; }
.fonte-item {
    background: #dbe4ff;
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    margin: 0.4rem 0;
    font-size: 0.88rem;
}
/* ── Ausência ── */
.bloco-ausencia {
    background-color: #fff4e6;
    border-left: 5px solid #e8590c;
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1.2rem;
    margin-top: 0.8rem;
    font-size: 0.91rem;
    color: #7c3e00;
}
.bloco-ausencia strong { color: #c0390b; }
/* ── Supervisão ── */
.bloco-supervisao {
    background-color: #fff8e1;
    border: 2px solid #f59f00;
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1.5rem;
}
/* ── Celular / Phone frame ── */
.celular-wrap {
    display: flex;
    justify-content: center;
    margin: 0.5rem 0 1.5rem 0;
}
.celular-frame {
    background: #e5ddd5;
    border: 3px solid #222;
    border-radius: 24px;
    padding: 0;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.18);
    overflow: hidden;
}
.celular-header {
    background: #075e54;
    color: white;
    padding: 0.75rem 1.1rem;
    font-weight: bold;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.celular-body {
    padding: 0.8rem 0.8rem 0.5rem 0.8rem;
    min-height: 180px;
}
.msg-escola {
    background: #dcf8c6;
    border-radius: 0 10px 10px 10px;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 1.5rem 0.4rem 0;
    font-size: 0.86rem;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}
.msg-familia {
    background: #ffffff;
    border-radius: 10px 0 10px 10px;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0 0.4rem 1.5rem;
    font-size: 0.86rem;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}
.msg-meta {
    font-size: 0.72rem;
    color: #888;
    text-align: right;
    margin-top: 2px;
}
.celular-footer {
    background: #f0f0f0;
    padding: 0.5rem 0.8rem;
    font-size: 0.78rem;
    color: #666;
    text-align: center;
    border-top: 1px solid #ddd;
}
/* ── Gestor ── */
.bloco-gestor {
    background: #f3f0ff;
    border: 2px solid #7048e8;
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}
.bloco-gestor h4 { color: #3b1fa8; margin-top: 0; }
/* ── Confirmado ── */
.bloco-confirmado {
    background-color: #d8f3dc;
    border: 2px solid #2d6a4f;
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1rem;
    text-align: center;
}
/* ── Status pills ── */
.pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: bold;
    margin-left: 0.5rem;
}
.pill-aguardando { background: #fff3cd; color: #7c5c00; }
.pill-enviado    { background: #cce5ff; color: #003d7a; }
.pill-respondido { background: #d4edda; color: #155724; }
.pill-aprovado   { background: #d8f3dc; color: #1b5e20; }
/* ── Tag modo ── */
.tag-modo {
    display: inline-block;
    background: #ffd43b;
    color: #7c4d00;
    font-size: 0.78rem;
    font-weight: bold;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── Cabeçalho ─────────────────────────────────────────────────────────────────

st.title("⚙️ A Alavanca")

if MODO_OPERACAO == "mock":
    st.markdown(
        '<span class="tag-modo">🟡 MODO SIMULAÇÃO — IA real desativada</span>',
        unsafe_allow_html=True,
    )

# Indicador de progresso do ciclo
_enviada = bool(st.session_state.get("mensagem_enviada"))
_respondida = bool(st.session_state.get("resposta_responsavel"))
_aprovado = bool(st.session_state.get("ciclo_aprovado"))

_estado = (
    '<span class="pill pill-aprovado">✅ Ciclo aprovado</span>' if _aprovado else
    '<span class="pill pill-respondido">💬 Aguardando gestor</span>' if _respondida else
    '<span class="pill pill-enviado">📤 Mensagem enviada</span>' if _enviada else
    '<span class="pill pill-aguardando">⏳ Aguardando geração</span>'
)
st.markdown(f"**Estado do ciclo:** {_estado}", unsafe_allow_html=True)
st.divider()

# ── 3 Abas ────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    "🏫 A Alavanca (Professor)",
    "📱 Celular da Família",
    "🛡️ Mesa do Gestor & Auditoria",
])


# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 — A ALAVANCA (VISÃO DO PROFESSOR)
# ══════════════════════════════════════════════════════════════════════════════

with tab1:

    if _aprovado:
        st.success("✅ Ciclo completo aprovado pelo gestor. Clique em **Nova Comunicação** na Aba 3.")
    elif _enviada:
        st.info("📤 Mensagem enviada à família. Aguarde a resposta na **Aba 2 — Celular da Família**.")
    else:
        st.subheader("① Descreva a tarefa")

        col_tipo, col_turma = st.columns([2, 1])
        with col_tipo:
            tipo_selecionado = st.selectbox(
                "Tipo de documento ou comunicação",
                options=list(TIPOS_TAREFA.keys()),
                format_func=lambda k: TIPOS_TAREFA[k],
                key="tipo_tarefa",
            )
        with col_turma:
            turma = st.text_input("Turma (ex: 7º B)", value="7º B", key="turma")

        descricao = st.text_area(
            "Contexto ou instrução adicional",
            placeholder="Descreva o que precisa ser comunicado, o motivo da ocorrência ou os detalhes da atividade...",
            height=100,
            key="descricao",
        )

        col_data, col_aluno, col_status = st.columns([1, 2, 1])
        with col_data:
            data_ref = st.date_input("Data de referência", value=date.today(), key="data")
        with col_aluno:
            nome_aluno = st.text_input(
                "Nome do aluno (se aplicável)",
                placeholder="Deixe em branco se não for individual",
                key="aluno",
            )
        with col_status:
            status_aluno = st.radio(
                "Status na aula",
                options=["Presente", "Ausente (Faltou)"],
                key="status_aluno",
            )

        _aluno_ausente = (status_aluno == "Ausente (Faltou)") and nome_aluno.strip()
        if _aluno_ausente:
            st.markdown(
                f'<div class="bloco-ausencia"><strong>🏠 Contexto de ausência ativado: {nome_aluno.strip()}</strong><br>'
                "O Escudo RAG adaptará a mensagem para ser acolhedora, informando o conteúdo da aula e enviando a lição de casa.</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Botão Gerar ──────────────────────────────────────────────────────

        col_btn, _ = st.columns([1, 3])
        with col_btn:
            botao_gerar = st.button(
                "🛡️ Gerar com Escudo RAG",
                type="primary",
                use_container_width=True,
                disabled=not descricao.strip(),
            )
        if not descricao.strip():
            st.caption("⬆️ Preencha o campo de contexto para habilitar a geração.")

        if botao_gerar and descricao.strip():
            _nota_ausencia = ""
            if _aluno_ausente:
                _nota_ausencia = (
                    f"\n\n⚠️ NOTA DE AUSÊNCIA — {nome_aluno.strip()} faltou na aula de hoje. "
                    "Adapte a mensagem para ser acolhedora: informe o conteúdo da aula, "
                    "envie os materiais e a lição de casa. Não use tom punitivo."
                )
            contexto = {
                "turma": turma,
                "descricao": descricao + _nota_ausencia,
                "data_referencia": data_ref.strftime("%d/%m/%Y"),
                "aluno": nome_aluno.strip() or "N/A",
                "status_aluno": status_aluno,
                "nome_escola": NOME_ESCOLA,
            }
            _aviso_cota = st.empty()

            def _cb_aviso(msg: str) -> None:
                _aviso_cota.warning(msg, icon="⏳")

            with st.spinner("Escudo RAG consultando os documentos da escola..."):
                resposta = EscudoRAG().gerar(tipo_selecionado, contexto, callback_aviso=_cb_aviso)
            st.session_state["resposta_rag"] = resposta
            st.session_state["contexto_aula"] = contexto
            st.session_state["tipo_tarefa_label"] = TIPOS_TAREFA[tipo_selecionado]
            st.session_state.pop("mensagem_enviada", None)
            st.session_state.pop("resposta_responsavel", None)
            st.session_state.pop("ciclo_aprovado", None)
            st.rerun()

    # ── Rascunho + Painel Azul ────────────────────────────────────────────────

    if "resposta_rag" in st.session_state and not _enviada:
        resposta = st.session_state["resposta_rag"]

        st.subheader("② Revise o rascunho")
        col_rascunho, col_escudo = st.columns([3, 2])

        with col_rascunho:
            st.markdown("**✏️ Rascunho (editável)**")
            rascunho_editado = st.text_area(
                label="rascunho",
                value=resposta.rascunho,
                height=300,
                key="rascunho_editado",
                label_visibility="collapsed",
            )
            st.caption("Edite o texto acima se necessário. O que estiver aqui será enviado.")

        with col_escudo:
            st.markdown(
                f'<div class="bloco-escudo"><h4>🛡️ Raciocínio do Escudo RAG</h4>'
                f'<p style="font-size:0.91rem;color:#333;">{resposta.raciocinio}</p>'
                f'<hr style="border-color:#c5cae9;margin:0.8rem 0;">'
                f'<strong style="font-size:0.84rem;color:#1e3a5f;">Fontes consultadas:</strong>',
                unsafe_allow_html=True,
            )
            for fonte in resposta.fontes_consultadas:
                cor = "#2d6a4f" if fonte.relevancia == "Alta" else "#7c4d00"
                st.markdown(
                    f'<div class="fonte-item"><strong>{fonte.documento}</strong><br>'
                    f'<em style="color:#555;">"{fonte.trecho}"</em><br>'
                    f'<span style="color:{cor};font-size:0.8rem;">● Relevância: {fonte.relevancia}</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Área de envio ─────────────────────────────────────────────────────

        st.markdown(
            '<div class="bloco-supervisao">'
            '<h4 style="color:#7c4d00;margin-top:0;">③ ✍️ Supervisão Humana — Enviar para o Responsável</h4>'
            '<p style="color:#5c3d00;font-size:0.93rem;">Você revisou o rascunho e o raciocínio do Escudo RAG. '
            '<strong>Ao clicar em Enviar, você assume a responsabilidade por este conteúdo.</strong></p>'
            '</div>',
            unsafe_allow_html=True,
        )

        professor_nome = st.text_input(
            "Seu nome (aparecerá no log de auditoria)",
            placeholder="Prof(a). Nome Sobrenome",
            key="professor_nome",
        )
        confirmacao = st.checkbox(
            "Li o rascunho, revisei o raciocínio do Escudo RAG e assumo a responsabilidade por esta mensagem.",
            key="confirmacao_envio",
        )

        col_env, col_desc, _ = st.columns([1, 1, 2])
        with col_env:
            btn_enviar = st.button(
                "📤 Enviar para o Responsável",
                type="primary",
                use_container_width=True,
                disabled=(not confirmacao or not professor_nome.strip()),
            )
        with col_desc:
            btn_descartar = st.button(
                "🗑️ Descartar Rascunho",
                type="secondary",
                use_container_width=True,
            )

        if not confirmacao or not professor_nome.strip():
            st.caption("⬆️ Preencha seu nome e marque a confirmação para habilitar o envio.")

        if btn_enviar:
            st.session_state["mensagem_enviada"] = st.session_state.get("rascunho_editado", resposta.rascunho)
            st.session_state["professor_nome"] = professor_nome.strip()
            st.session_state["havia_ausencia"] = _aluno_ausente
            st.rerun()

        if btn_descartar:
            for k in ["resposta_rag", "contexto_aula", "tipo_tarefa_label", "rascunho_editado"]:
                st.session_state.pop(k, None)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 — CELULAR DA FAMÍLIA (SIMULAÇÃO)
# ══════════════════════════════════════════════════════════════════════════════

with tab2:

    if not _enviada:
        st.info("📭 Aguardando o professor gerar e enviar uma mensagem na **Aba 1 — A Alavanca**.", icon="📋")

    else:
        contexto = st.session_state.get("contexto_aula", {})
        aluno_nome = contexto.get("aluno", "Aluno")
        turma_nome = contexto.get("turma", "")
        hora_envio = datetime.now().strftime("%H:%M")

        st.subheader(f"📱 Mensagem recebida — Responsável de {aluno_nome}")
        st.caption(f"Turma: {turma_nome} · Escola: {NOME_ESCOLA}")

        # ── Phone frame ───────────────────────────────────────────────────────

        msg_texto = st.session_state.get("mensagem_enviada", "")
        st.markdown(
            f'<div class="celular-wrap"><div class="celular-frame">'
            f'<div class="celular-header">📞 {NOME_ESCOLA}</div>'
            f'<div class="celular-body">'
            f'<div class="msg-escola">{msg_texto.replace(chr(10), "<br>")}'
            f'<div class="msg-meta">{hora_envio} ✓✓</div></div>',
            unsafe_allow_html=True,
        )

        if _respondida:
            resp = st.session_state["resposta_responsavel"]
            st.markdown(
                f'<div class="msg-familia">{resp["texto"].replace(chr(10), "<br>")}'
                f'<div class="msg-meta">{resp["hora"]} · {resp["nome"]}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '</div><div class="celular-footer">💬 Canal oficial escola-família</div></div></div>',
            unsafe_allow_html=True,
        )

        # ── Formulário de resposta ────────────────────────────────────────────

        if not _respondida and not _aprovado:
            st.divider()
            st.subheader("✍️ Resposta do Responsável")
            st.caption("Simule a resposta que chegaria pelo aplicativo escolar.")

            nome_responsavel = st.text_input(
                "Nome do responsável",
                placeholder="Ex: Maria da Silva (mãe de João)",
                key="nome_responsavel",
            )
            resposta_texto = st.text_area(
                "Mensagem de resposta",
                placeholder="Ex: Boa tarde! João ficou doente hoje. Segue atestado médico. Obrigada.",
                height=120,
                key="resposta_texto",
            )

            col_resp, _ = st.columns([1, 3])
            with col_resp:
                btn_responder = st.button(
                    "💬 Responder à Escola",
                    type="primary",
                    use_container_width=True,
                    disabled=(not nome_responsavel.strip() or not resposta_texto.strip()),
                )
            if not nome_responsavel.strip() or not resposta_texto.strip():
                st.caption("⬆️ Preencha seu nome e a mensagem para responder.")

            if btn_responder:
                st.session_state["resposta_responsavel"] = {
                    "texto": resposta_texto.strip(),
                    "nome": nome_responsavel.strip(),
                    "hora": datetime.now().strftime("%H:%M"),
                }
                st.rerun()

        elif _respondida and not _aprovado:
            st.success("💬 Resposta registrada! Vá para a **Aba 3 — Mesa do Gestor** para aprovação.")

        elif _aprovado:
            st.success("✅ Ciclo aprovado pelo gestor e registrado no log auditável.")


# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 — MESA DO GESTOR & AUDITORIA
# ══════════════════════════════════════════════════════════════════════════════

with tab3:

    # ── Ciclo pendente de aprovação ───────────────────────────────────────────

    if _respondida and not _aprovado:
        st.subheader("🛡️ Ciclo aguardando aprovação do Gestor")

        resp = st.session_state["resposta_responsavel"]
        contexto = st.session_state.get("contexto_aula", {})
        resposta_rag = st.session_state.get("resposta_rag")
        professor = st.session_state.get("professor_nome", "Professor(a)")

        st.markdown(
            '<div class="bloco-gestor"><h4>📋 Resumo do Ciclo</h4>',
            unsafe_allow_html=True,
        )
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Professor(a)", professor)
        col_b.metric("Aluno", contexto.get("aluno", "N/A"))
        col_c.metric("Turma", contexto.get("turma", ""))
        st.markdown("</div>", unsafe_allow_html=True)

        col_msg, col_resp = st.columns(2)

        with col_msg:
            st.markdown("**📤 Mensagem enviada pela escola**")
            st.text_area(
                label="msg_escola",
                value=st.session_state.get("mensagem_enviada", ""),
                height=200,
                disabled=True,
                label_visibility="collapsed",
                key="preview_msg_escola",
            )

        with col_resp:
            st.markdown(f"**💬 Resposta de: {resp['nome']}** · {resp['hora']}")
            st.text_area(
                label="msg_familia",
                value=resp["texto"],
                height=200,
                disabled=True,
                label_visibility="collapsed",
                key="preview_resp_familia",
            )

        if resposta_rag:
            with st.expander("🛡️ Ver Raciocínio do Escudo RAG (fontes consultadas)"):
                st.markdown(resposta_rag.raciocinio)
                for fonte in resposta_rag.fontes_consultadas:
                    st.markdown(f"- **{fonte.documento}** — _{fonte.trecho}_")

        st.markdown(
            '<div class="bloco-supervisao">'
            '<h4 style="color:#7c4d00;margin-top:0;">✍️ Aprovação do Gestor</h4>'
            '<p style="color:#5c3d00;font-size:0.93rem;">Ao aprovar, você confirma que o ciclo '
            'escola-família foi conduzido com transparência. O registro completo — incluindo '
            'o raciocínio da IA, as fontes consultadas e esta resposta — será gravado no log auditável.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        gestor_nome = st.text_input(
            "Nome do Gestor (aparecerá no log de auditoria)",
            placeholder="Diretor(a) / Coordenador(a) Nome Sobrenome",
            key="gestor_nome",
        )
        confirm_gestor = st.checkbox(
            "Revisei o ciclo completo — a mensagem, a resposta da família e o raciocínio da IA — e aprovo este registro.",
            key="confirm_gestor",
        )

        col_apr, col_neg, _ = st.columns([1, 1, 2])
        with col_apr:
            btn_aprovar = st.button(
                "✅ Aprovar e Registrar",
                type="primary",
                use_container_width=True,
                disabled=(not confirm_gestor or not gestor_nome.strip()),
            )
        with col_neg:
            btn_cancelar = st.button(
                "↩️ Devolver ao Professor",
                type="secondary",
                use_container_width=True,
            )

        if not confirm_gestor or not gestor_nome.strip():
            st.caption("⬆️ Preencha seu nome e marque a confirmação para aprovar.")

        if btn_aprovar:
            registrar_ciclo_completo(
                professor=professor,
                aluno=contexto.get("aluno", "N/A"),
                turma=contexto.get("turma", ""),
                status_aluno=contexto.get("status_aluno", ""),
                tipo_comunicacao=st.session_state.get("tipo_tarefa_label", ""),
                mensagem_professor=st.session_state.get("mensagem_enviada", ""),
                raciocinio_rag=resposta_rag.raciocinio if resposta_rag else "",
                fontes_consultadas=resposta_rag.fontes_consultadas if resposta_rag else [],
                resposta_responsavel=resp["texto"],
                nome_responsavel=resp["nome"],
                gestor_aprovador=gestor_nome.strip(),
                modo_operacao=MODO_OPERACAO,
            )
            st.session_state["ciclo_aprovado"] = True
            st.session_state["gestor_nome_final"] = gestor_nome.strip()
            st.rerun()

        if btn_cancelar:
            st.session_state.pop("resposta_responsavel", None)
            st.rerun()

    elif _aprovado:
        gestor_final = st.session_state.get("gestor_nome_final", "Gestor(a)")
        professor_final = st.session_state.get("professor_nome", "Professor(a)")
        contexto = st.session_state.get("contexto_aula", {})
        st.markdown(
            f'<div class="bloco-confirmado">'
            f'<h3 style="color:#2d6a4f;margin-top:0;">✅ Ciclo registrado com sucesso</h3>'
            f'<p style="color:#1b4332;">Aprovado por <strong>{gestor_final}</strong> · '
            f'Professor(a): <strong>{professor_final}</strong> · '
            f'Aluno: <strong>{contexto.get("aluno","N/A")}</strong><br>'
            f'<em style="font-size:0.88rem;">O registro completo está no log abaixo.</em></p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("⚙️ Nova Comunicação", type="primary"):
            for k in [
                "resposta_rag", "contexto_aula", "tipo_tarefa_label", "rascunho_editado",
                "mensagem_enviada", "professor_nome", "resposta_responsavel",
                "ciclo_aprovado", "gestor_nome_final", "havia_ausencia",
                "confirmacao_envio", "confirm_gestor",
            ]:
                st.session_state.pop(k, None)
            st.rerun()

    elif not _enviada:
        st.info("📭 Aguardando o professor enviar uma mensagem na **Aba 1**.", icon="🏫")
    elif not _respondida:
        st.info("📭 Aguardando a resposta da família na **Aba 2 — Celular da Família**.", icon="📱")

    # ── Tabela de Auditoria (sempre visível) ──────────────────────────────────

    st.divider()
    st.subheader("📋 Histórico de Transparência")
    st.caption("Últimas 5 comunicações aprovadas pelo gestor — ciclos completos escola-família.")

    ciclos = carregar_ciclos(limite=5)

    if not ciclos:
        st.info("Nenhum ciclo registrado ainda. Complete o fluxo para ver os registros aqui.", icon="🗂️")
    else:
        linhas = []
        for c in reversed(ciclos):
            ts = datetime.fromisoformat(c["timestamp"]).strftime("%d/%m/%Y %H:%M")
            fontes = ", ".join(
                f.get("documento", "?") for f in c.get("fontes_consultadas", [])
            )
            linhas.append({
                "Data/Hora": ts,
                "Professor(a)": c.get("professor", ""),
                "Aluno": c.get("aluno", ""),
                "Turma": c.get("turma", ""),
                "Tipo": c.get("tipo_comunicacao", ""),
                "Fontes RAG": fontes[:60] + "..." if len(fontes) > 60 else fontes,
                "Responsável": c.get("nome_responsavel", ""),
                "Gestor Aprovador": c.get("gestor_aprovador", ""),
                "Modo": c.get("modo_operacao", ""),
            })
        st.dataframe(linhas, use_container_width=True)

        with st.expander("🔍 Ver último ciclo completo (JSON)"):
            st.json(ciclos[-1])
