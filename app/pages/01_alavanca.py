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

/* ══════════════════════════════════════════════════════
   HERO BANNER
══════════════════════════════════════════════════════ */
.hero-banner {
    background: linear-gradient(135deg, #1a237e 0%, #3b5bdb 65%, #5c7cfa 100%);
    border-radius: 18px;
    padding: 2.4rem 2rem 2rem;
    margin-bottom: 1.4rem;
    text-align: center;
    box-shadow: 0 8px 40px rgba(59,91,219,0.28);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; right: -8%;
    width: 340px; height: 340px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
    pointer-events: none;
}
.hero-banner::after {
    content: '';
    position: absolute;
    bottom: -40%; left: -6%;
    width: 240px; height: 240px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
    pointer-events: none;
}
.hero-icon { font-size: 2.8rem; line-height: 1; margin-bottom: 0.4rem; }
.hero-title {
    color: #ffffff !important;
    font-size: 2.3rem !important;
    font-weight: 800 !important;
    margin: 0.1rem 0 0.5rem !important;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: #c5cae9;
    font-size: 0.97rem;
    margin: 0 auto;
    max-width: 520px;
    line-height: 1.55;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.28);
    color: #e8eaff;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 13px;
    border-radius: 20px;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.hero-badge-mock {
    background: rgba(255,193,7,0.2);
    border-color: rgba(255,193,7,0.45);
    color: #ffd43b;
}

/* ══════════════════════════════════════════════════════
   CYCLE STATUS BAR
══════════════════════════════════════════════════════ */
.ciclo-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f8f9ff;
    border: 1px solid #dde3ff;
    border-radius: 10px;
    padding: 0.65rem 1.2rem;
    margin-bottom: 1.4rem;
}
.ciclo-bar-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #7783a0;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ══════════════════════════════════════════════════════
   STEP HEADERS
══════════════════════════════════════════════════════ */
.step-header {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin: 1.1rem 0 0.8rem;
}
.step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px; height: 30px;
    background: #3b5bdb;
    color: #fff;
    font-size: 0.82rem;
    font-weight: 800;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(59,91,219,0.35);
}
.step-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a237e;
    margin: 0;
}

/* ══════════════════════════════════════════════════════
   ESCUDO RAG CARD (premium)
══════════════════════════════════════════════════════ */
.bloco-escudo {
    background-color: #f5f7ff;
    border: 1px solid #c5cae9;
    border-radius: 12px;
    padding: 0 1.2rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(59,91,219,0.10);
    overflow: hidden;
}
.escudo-topbar {
    background: linear-gradient(90deg, #3b5bdb 0%, #5c7cfa 100%);
    margin: 0 -1.2rem 1rem;
    padding: 0.55rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.escudo-topbar-title {
    color: #fff !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    letter-spacing: 0.03em;
}
.fonte-item {
    background: #dbe4ff;
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    margin: 0.4rem 0;
    font-size: 0.86rem;
    border-left: 3px solid #4c6ef5;
}

/* ══════════════════════════════════════════════════════
   AUSÊNCIA
══════════════════════════════════════════════════════ */
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

/* ══════════════════════════════════════════════════════
   SUPERVISÃO HUMANA
══════════════════════════════════════════════════════ */
.bloco-supervisao {
    background: linear-gradient(135deg, #fffde7, #fff8e1);
    border: 2px solid #f59f00;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    box-shadow: 0 3px 14px rgba(245,159,0,0.12);
}

/* ══════════════════════════════════════════════════════
   CELULAR / PHONE FRAME
══════════════════════════════════════════════════════ */
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
    box-shadow: 0 8px 32px rgba(0,0,0,0.22);
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
    box-shadow: 0 1px 3px rgba(0,0,0,0.09);
}
.msg-familia {
    background: #ffffff;
    border-radius: 10px 0 10px 10px;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0 0.4rem 1.5rem;
    font-size: 0.86rem;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.09);
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

/* ══════════════════════════════════════════════════════
   GESTOR
══════════════════════════════════════════════════════ */
.bloco-gestor {
    background: #f3f0ff;
    border: 2px solid #7048e8;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 3px 14px rgba(112,72,232,0.10);
}
.bloco-gestor h4 { color: #3b1fa8; margin-top: 0; }

/* ══════════════════════════════════════════════════════
   CONFIRMADO
══════════════════════════════════════════════════════ */
.bloco-confirmado {
    background: linear-gradient(135deg, #d8f3dc, #b7e4c7);
    border: 2px solid #2d6a4f;
    border-radius: 12px;
    padding: 1.8rem;
    margin-top: 1rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(45,106,79,0.12);
}

/* ══════════════════════════════════════════════════════
   STATUS PILLS
══════════════════════════════════════════════════════ */
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


# ── Estado do ciclo (calculado antes do hero para uso no badge) ───────────────
_enviada   = bool(st.session_state.get("mensagem_enviada"))
_respondida = bool(st.session_state.get("resposta_responsavel"))
_aprovado  = bool(st.session_state.get("ciclo_aprovado"))

# ── Hero Banner ───────────────────────────────────────────────────────────────
_badge_modo = (
    '<span class="hero-badge hero-badge-mock">🟡 Modo Simulação</span>'
    if MODO_OPERACAO == "mock"
    else '<span class="hero-badge">🟢 Escudo RAG Ativo</span>'
)
st.markdown(
    f'<div class="hero-banner">'
    f'{_badge_modo}'
    f'<div class="hero-icon">⚙️</div>'
    f'<h1 class="hero-title">A Alavanca</h1>'
    f'<p class="hero-subtitle">O fim da religião da burocracia.<br>'
    f'Automação com a Ética do Segundo Atual.</p>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Barra de status do ciclo ──────────────────────────────────────────────────
_estado = (
    '<span class="pill pill-aprovado">✅ Ciclo aprovado</span>' if _aprovado else
    '<span class="pill pill-respondido">💬 Aguardando gestor</span>' if _respondida else
    '<span class="pill pill-enviado">📤 Mensagem enviada</span>' if _enviada else
    '<span class="pill pill-aguardando">⏳ Aguardando geração</span>'
)
st.markdown(
    f'<div class="ciclo-bar">'
    f'<span class="ciclo-bar-label">Estado do ciclo</span>'
    f'{_estado}'
    f'</div>',
    unsafe_allow_html=True,
)

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
        st.markdown(
            '<div class="step-header">'
            '<span class="step-num">1</span>'
            '<span class="step-title">Descreva a tarefa</span>'
            '</div>',
            unsafe_allow_html=True,
        )

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

            try:
                with st.spinner("Escudo RAG consultando os documentos da escola..."):
                    resposta = EscudoRAG().gerar(tipo_selecionado, contexto, callback_aviso=_cb_aviso)
                st.session_state["resposta_rag"] = resposta
                st.session_state["contexto_aula"] = contexto
                st.session_state["tipo_tarefa_label"] = TIPOS_TAREFA[tipo_selecionado]
                st.session_state.pop("mensagem_enviada", None)
                st.session_state.pop("resposta_responsavel", None)
                st.session_state.pop("ciclo_aprovado", None)
                st.rerun()
            except Exception as e:
                import traceback
                traceback.print_exc()
                st.error(
                    f"⚠️ Erro capturado pelo sistema: {str(e)}\n\n"
                    "O servidor continua ativo. Verifique o terminal para o traceback completo."
                )

    # ── Rascunho + Painel Azul ────────────────────────────────────────────────

    if "resposta_rag" in st.session_state and not _enviada:
        resposta = st.session_state["resposta_rag"]

        st.markdown(
            '<div class="step-header">'
            '<span class="step-num">2</span>'
            '<span class="step-title">Revise o rascunho</span>'
            '</div>',
            unsafe_allow_html=True,
        )
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
                '<div class="bloco-escudo">'
                '<div class="escudo-topbar">'
                '<span style="font-size:1.1rem;">🛡️</span>'
                '<span class="escudo-topbar-title">Raciocínio do Escudo RAG</span>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p style="font-size:0.91rem;color:#2c3060;line-height:1.55;">'
                f'{resposta.raciocinio}</p>'
                f'<hr style="border-color:#c5cae9;margin:0.8rem 0;">'
                f'<strong style="font-size:0.82rem;color:#1e3a5f;text-transform:uppercase;'
                f'letter-spacing:0.05em;">Fontes consultadas</strong>',
                unsafe_allow_html=True,
            )
            for fonte in resposta.fontes_consultadas:
                cor = "#2d6a4f" if fonte.relevancia == "Alta" else "#7c4d00"
                icone = "🟢" if fonte.relevancia == "Alta" else "🟡"
                st.markdown(
                    f'<div class="fonte-item">'
                    f'<strong style="color:#1a237e;">{fonte.documento}</strong><br>'
                    f'<em style="color:#555;font-size:0.83rem;">"{fonte.trecho}"</em><br>'
                    f'<span style="color:{cor};font-size:0.79rem;">'
                    f'{icone} Relevância: {fonte.relevancia}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Área de envio ─────────────────────────────────────────────────────

        st.markdown(
            '<div class="step-header" style="margin-top:1.4rem;">'
            '<span class="step-num">3</span>'
            '<span class="step-title">Supervisão Humana — Enviar ao Responsável</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="bloco-supervisao">'
            '<p style="color:#5c3d00;font-size:0.93rem;margin:0;">Você revisou o rascunho e o '
            'raciocínio do Escudo RAG. '
            '<strong>Ao clicar em Enviar, você assume a responsabilidade por este conteúdo.</strong></p>'
            '</div>',
            unsafe_allow_html=True,
        )

        professor_nome = st.text_input(
            "Seu nome (aparecerá no log de auditoria)",
            placeholder="Prof(a). Nome Sobrenome",
            key="professor_nome",
        )

        _nome_incompleto = bool(
            professor_nome.strip() and len(professor_nome.strip().split()) < 2
        )
        if _nome_incompleto:
            st.info(
                "Por favor, insira Nome e Sobrenome para registro no sistema "
                "(ex: *Prof. Sérgio Oliveira*).",
                icon="ℹ️",
            )

        confirmacao = st.checkbox(
            "Li o rascunho, revisei o raciocínio do Escudo RAG e assumo a responsabilidade por esta mensagem.",
            key="confirmacao_envio",
        )

        _envio_bloqueado = not confirmacao or not professor_nome.strip() or _nome_incompleto
        col_env, col_desc, _ = st.columns([1, 1, 2])
        with col_env:
            btn_enviar = st.button(
                "📤 Enviar para o Responsável",
                type="primary",
                use_container_width=True,
                disabled=_envio_bloqueado,
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
