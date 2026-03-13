"""
Auditoria — Registro imutável de todas as ações do sistema.

Dois tipos de log:
  log_acoes.jsonl  — ações simples (legado, mantido para compatibilidade).
  log_ciclos.jsonl — ciclo completo de comunicação:
                     professor → mensagem gerada pelo RAG → resposta da família
                     → aprovação do gestor. É o coração da transparência.

O log protege o professor e a escola, não os vigia.
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List

from config.settings import DIR_LOGS


# ── Estruturas de dados ───────────────────────────────────────────────────────

@dataclass
class EntradaLog:
    timestamp: str
    tipo_tarefa: str
    aprovado_por: str
    rascunho_aprovado: str
    raciocinio_rag: str
    fontes_consultadas: list
    contexto_entrada: str
    modo_operacao: str


# ── Log simples (legado) ──────────────────────────────────────────────────────

def registrar_aprovacao(
    tipo_tarefa: str,
    aprovado_por: str,
    rascunho_aprovado: str,
    raciocinio_rag: str,
    fontes_consultadas: list,
    contexto_entrada: str,
    modo_operacao: str = "mock",
) -> str:
    entrada = EntradaLog(
        timestamp=datetime.now().isoformat(),
        tipo_tarefa=tipo_tarefa,
        aprovado_por=aprovado_por,
        rascunho_aprovado=rascunho_aprovado,
        raciocinio_rag=raciocinio_rag,
        fontes_consultadas=[
            {"documento": f.documento, "trecho": f.trecho, "relevancia": f.relevancia}
            if hasattr(f, "documento") else f
            for f in fontes_consultadas
        ],
        contexto_entrada=contexto_entrada,
        modo_operacao=modo_operacao,
    )
    nome_arquivo = os.path.join(DIR_LOGS, "log_acoes.jsonl")
    with open(nome_arquivo, "a", encoding="utf-8") as arq:
        arq.write(json.dumps(asdict(entrada), ensure_ascii=False) + "\n")
    return nome_arquivo


def carregar_logs() -> List[dict]:
    nome_arquivo = os.path.join(DIR_LOGS, "log_acoes.jsonl")
    if not os.path.exists(nome_arquivo):
        return []
    with open(nome_arquivo, "r", encoding="utf-8") as arq:
        return [json.loads(linha) for linha in arq if linha.strip()]


# ── Log de ciclo completo (Capítulos 3 e 4 do Manifesto) ─────────────────────

def registrar_ciclo_completo(
    professor: str,
    aluno: str,
    turma: str,
    status_aluno: str,
    tipo_comunicacao: str,
    mensagem_professor: str,
    raciocinio_rag: str,
    fontes_consultadas: list,
    resposta_responsavel: str,
    nome_responsavel: str,
    gestor_aprovador: str,
    modo_operacao: str = "mock",
) -> str:
    """
    Grava o ciclo completo de comunicação escola-família no log auditável.
    Este é o registro definitivo que prova que não existe caixa-preta:
    toda decisão, toda fonte consultada e toda resposta humana está aqui.
    """
    entrada = {
        "timestamp": datetime.now().isoformat(),
        "tipo": "ciclo_comunicacao",
        "professor": professor,
        "aluno": aluno,
        "turma": turma,
        "status_aluno": status_aluno,
        "tipo_comunicacao": tipo_comunicacao,
        "mensagem_professor": mensagem_professor,
        "raciocinio_rag": raciocinio_rag,
        "fontes_consultadas": [
            {"documento": f.documento, "trecho": f.trecho, "relevancia": f.relevancia}
            if hasattr(f, "documento") else f
            for f in fontes_consultadas
        ],
        "resposta_responsavel": resposta_responsavel,
        "nome_responsavel": nome_responsavel,
        "gestor_aprovador": gestor_aprovador,
        "modo_operacao": modo_operacao,
    }
    nome_arquivo = os.path.join(DIR_LOGS, "log_ciclos.jsonl")
    with open(nome_arquivo, "a", encoding="utf-8") as arq:
        arq.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    return nome_arquivo


def carregar_ciclos(limite: int = 5) -> List[dict]:
    """Retorna os últimos N ciclos completos para exibição na tabela de auditoria."""
    nome_arquivo = os.path.join(DIR_LOGS, "log_ciclos.jsonl")
    if not os.path.exists(nome_arquivo):
        return []
    with open(nome_arquivo, "r", encoding="utf-8") as arq:
        todos = [json.loads(linha) for linha in arq if linha.strip()]
    return todos[-limite:]
