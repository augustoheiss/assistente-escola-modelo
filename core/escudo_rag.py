"""
Escudo RAG — Motor de Geração com Recuperação Controlada.

Filosofia (do Manifesto):
  A máquina não alucina; ela consulta a lei interna.
  Opera dentro de um perímetro restrito e 100% transparente.

Pipeline Fase 2:
  1. ingerir_documentos() — lê PDFs, divide em chunks, gera embeddings
     com GoogleGenerativeAIEmbeddings e persiste no ChromaDB local.
  2. gerar() — busca semântica + LLM → RespostaRAG (comunicado/ocorrência/lição).
  3. analisar_diario() — AGENTIC: formaliza o relato do dia e detecta ações
     recomendadas automaticamente (faltas, ocorrências, destaques) → RespostaDiario.

Modo "mock" (Fase 1) é mantido para testes sem API key.
"""

import os
import json
import re
import time
from dataclasses import dataclass
from typing import List, Callable, Optional

from config.settings import (
    MODO_OPERACAO,
    GOOGLE_API_KEY,
    DIR_DOCUMENTOS,
    DIR_BASE_CONHECIMENTO,
    NOME_ESCOLA,
)

# ── Estruturas de dados públicas ──────────────────────────────────────────────

@dataclass
class FonteConsultada:
    documento: str
    trecho: str
    relevancia: str


@dataclass
class RespostaRAG:
    rascunho: str
    fontes_consultadas: List[FonteConsultada]
    raciocinio: str
    tipo_tarefa: str
    contexto_entrada: str


@dataclass
class AcaoRecomendada:
    """Ação pedagógica detectada automaticamente pelo pipeline Agentic."""
    tipo: str       # comunicado_familia | registro_ocorrencia | encaminhamento_coordenacao | destaque_positivo
    titulo: str
    descricao: str
    urgencia: str   # alta | media | baixa
    gatilho: str    # trecho do relato que motivou a ação


@dataclass
class RespostaDiario:
    """Resultado do pipeline Agentic: diário formalizado + ações recomendadas."""
    diario_formalizado: str
    next_actions: List[AcaoRecomendada]
    raciocinio: str
    fontes_consultadas: List[FonteConsultada]


# ── Constantes de geração ─────────────────────────────────────────────────────

_DESCRICOES_TAREFA = {
    "comunicado_pais": "comunicado oficial para os responsáveis dos alunos",
    "registro_ocorrencia": "registro formal de ocorrência disciplinar",
    "licao_de_casa": "orientação de lição de casa para os alunos",
}

_EMBEDDING_MODEL    = "models/gemini-embedding-001"
_LLM_MODEL          = "gemini-2.5-flash"
_CHROMA_COLLECTION  = "escola_modelo"

# ── Parâmetros de eficiência e respeito à cota da API ─────────────────────────
_RETRIEVAL_K        = 4    # chunks recuperados por busca (↓ reduz tamanho do prompt)
_MAX_CHARS_CHUNK    = 500  # caracteres por chunk enviados ao LLM (↓ reduz tokens)
_MAX_RETRIES        = 3    # tentativas em caso de erro 429
_RETRY_WAIT_S       = 15   # segundos de espera entre tentativas

# Singleton para o vector store: criado na primeira busca, reutilizado nas seguintes.
# Evita re-abrir a conexão ChromaDB a cada render do Streamlit (lazy loading).
_VS_CACHE: dict = {}

_PROMPT_SISTEMA = """\
Você é o Escudo RAG do Assistente Escola Modelo.
Sua ÚNICA fonte de conhecimento são os trechos dos documentos oficiais da escola fornecidos abaixo.

REGRAS INVIOLÁVEIS:
1. NÃO invente, infira ou extrapole informações que não estejam explicitamente nos documentos.
2. Se não houver base documental suficiente para algum campo, marque-o como [A PREENCHER] \
e explique no raciocínio.
3. Tom: formal, respeitoso e alinhado às diretrizes pedagógicas da escola.
4. Este texto é sempre um RASCUNHO para revisão e aprovação humana — nunca uma decisão final.

TAREFA: Gerar um {tipo_tarefa_descricao}.

DADOS FORNECIDOS PELO PROFESSOR:
- Escola: {nome_escola}
- Turma: {turma}
- Data de referência: {data_referencia}
- Aluno (se aplicável): {aluno}
- Contexto / Instrução: {descricao}

TRECHOS DOS DOCUMENTOS OFICIAIS RECUPERADOS PELO ESCUDO RAG:
{contexto_documentos}

---
Responda EXCLUSIVAMENTE em JSON válido, sem blocos de código ou texto adicional fora do JSON:
{{
  "rascunho": "texto completo do documento, use \\n para quebras de linha",
  "raciocinio": "explicação detalhada em Markdown estrito. IMPORTANTE: use obrigatoriamente uma linha em branco (\\n\\n) entre cada tópico ou bullet point para garantir legibilidade. Formato exigido: '* **Arquivo X, pág. Y:** trecho utilizado e decisão tomada.' com linha em branco separando cada bullet. Cite o nome do arquivo e a página consultada para cada decisão."
}}
"""


# ── Mapeamento ação agêntica → tipo de tarefa existente ──────────────────────
_ACAO_PARA_TAREFA: dict = {
    "comunicado_familia":         "comunicado_pais",
    "registro_ocorrencia":        "registro_ocorrencia",
    "encaminhamento_coordenacao": "comunicado_pais",
    "destaque_positivo":          "comunicado_pais",
}

# ── Prompt para pipeline Agentic (Diário de Classe) ───────────────────────────
_PROMPT_DIARIO = """\
Você é o Escudo RAG do Assistente Escola Modelo, atuando como analista proativo do Diário de Classe.

MISSÃO: formalizar o relato do professor e identificar automaticamente as ações pedagógicas necessárias.

REGRAS INVIOLÁVEIS:
1. O "diario_formalizado" deve preservar TODOS os fatos do relato — nunca omita nem invente nada.
2. Cada ação em "next_actions" deve ter evidência EXPLÍCITA no relato. Não crie ações sem evidência.
3. O "gatilho" de cada ação deve citar a frase exata do relato que a motivou.
4. Baseie as recomendações nas diretrizes dos documentos oficiais fornecidos abaixo.
5. Tom: formal e objetivo. Este é um RASCUNHO para revisão humana — nunca uma decisão final.

DADOS FORNECIDOS PELO PROFESSOR:
- Escola: {nome_escola}
- Turma: {turma}
- Data de referência: {data_referencia}
- Aluno(s) envolvido(s): {aluno}
- Relato do Professor: {relato}

TRECHOS DOS DOCUMENTOS OFICIAIS RECUPERADOS PELO ESCUDO RAG:
{contexto_documentos}

---
Responda EXCLUSIVAMENTE em JSON válido, sem blocos de código ou texto fora do JSON:
{{
  "diario_formalizado": "texto completo e formal do diário, use \\n para quebras de linha",
  "raciocinio": "explicação em Markdown. OBRIGATÓRIO: linha em branco (\\n\\n) entre cada bullet. Formato: '* **Arquivo, pág.:** decisão e evidência.'",
  "next_actions": [
    {{
      "tipo": "comunicado_familia|registro_ocorrencia|encaminhamento_coordenacao|destaque_positivo",
      "titulo": "título curto e objetivo da ação",
      "descricao": "o que fazer e por quê, baseado nos documentos oficiais",
      "urgencia": "alta|media|baixa",
      "gatilho": "frase exata do relato que motivou esta ação"
    }}
  ]
}}

Se não houver ações necessárias, retorne "next_actions": [].
"""


def _sanitize_json_literals(content: str) -> str:
    """
    Escapa caracteres de controle literais (\\n, \\r, \\t) que aparecem dentro
    de valores de string JSON.

    LLMs frequentemente retornam JSON tecnicamente inválido onde o valor de um
    campo contém quebras de linha literais em vez da sequência de escape \\\\n.
    Esta função percorre o conteúdo caractere por caractere, respeitando as
    sequências de escape já existentes, e escapa apenas os literais problemáticos
    que estão dentro de strings JSON.
    """
    result: list[str] = []
    in_string = False
    i = 0
    while i < len(content):
        c = content[i]
        if c == "\\" and in_string:
            # Consume the backslash + next char as a valid escape sequence.
            result.append(c)
            i += 1
            if i < len(content):
                result.append(content[i])
                i += 1
            continue
        if c == '"':
            result.append(c)
            in_string = not in_string
            i += 1
            continue
        if in_string:
            if c == "\n":
                result.append("\\n")
            elif c == "\r":
                result.append("\\r")
            elif c == "\t":
                result.append("\\t")
            else:
                result.append(c)
        else:
            result.append(c)
        i += 1
    return "".join(result)


# ── Classe principal ──────────────────────────────────────────────────────────

class EscudoRAG:
    """
    O Escudo RAG é o protocolo inegociável de governança da IA.
    Força a máquina a consultar os documentos oficiais da escola
    antes de gerar qualquer palavra.
    """

    # ── Pontos de entrada públicos ────────────────────────────────────────────

    def analisar_diario(
        self,
        contexto: dict,
        callback_aviso: Optional[Callable[[str], None]] = None,
    ) -> "RespostaDiario":
        """
        Pipeline Agentic: formaliza o relato do Diário de Classe e detecta
        automaticamente ações pedagógicas necessárias (faltas, ocorrências,
        destaques). Retorna RespostaDiario com diario_formalizado + next_actions.

        contexto esperado:
          turma, data_referencia, relato, aluno (opcional), nome_escola
        """
        if MODO_OPERACAO == "mock":
            return self._analisar_diario_mock(contexto)
        return self._analisar_diario_rag(contexto, callback_aviso)

    def gerar(
        self,
        tipo_tarefa: str,
        contexto: dict,
        callback_aviso: Optional[Callable[[str], None]] = None,
    ) -> RespostaRAG:
        """
        callback_aviso: função opcional chamada com uma mensagem de texto
        quando o motor aguarda renovação de cota (erro 429). Permite que
        a UI Streamlit exiba um st.warning sem importar streamlit no core.
        """
        if MODO_OPERACAO == "mock":
            return self._gerar_mock(tipo_tarefa, contexto)
        return self._gerar_rag(tipo_tarefa, contexto, callback_aviso)

    # ── Ingestão de documentos ────────────────────────────────────────────────

    def ingerir_documentos(self, forcar: bool = False, callback=None) -> dict:
        """
        Lê os PDFs de DIR_DOCUMENTOS, gera embeddings com a API do Google
        e persiste os vetores no ChromaDB em DIR_BASE_CONHECIMENTO.

        Estratégia resiliente:
        - Consulta o ChromaDB para descobrir quais arquivos já foram indexados.
        - Pula automaticamente os já processados (retomada inteligente).
        - Se um PDF falhar, loga o erro e continua o pipeline.
        - Processa um PDF por vez para respeitar o rate limit da API.

        Parâmetros:
            forcar:   se True, apaga a coleção e re-indexa tudo do zero.
            callback: função chamada com (nome_pdf, n_chunks, idx, total_pdfs)
                      a cada documento concluído — usada pela UI Streamlit.
        """
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_chroma import Chroma
        import chromadb as _chromadb

        pdfs_disponiveis = sorted(
            f for f in os.listdir(DIR_DOCUMENTOS) if f.lower().endswith(".pdf")
        )
        if not pdfs_disponiveis:
            return {
                "status": "erro",
                "mensagem": "Nenhum PDF encontrado em data/documentos_escola/.",
            }

        # Se forçar, apaga a coleção e recomeça do zero
        if forcar:
            try:
                _cli = _chromadb.PersistentClient(path=DIR_BASE_CONHECIMENTO)
                _cli.delete_collection(_CHROMA_COLLECTION)
            except Exception:
                pass
            ja_indexados: set = set()
        else:
            # Descobre quais arquivos já estão no ChromaDB
            ja_indexados = self._arquivos_ja_indexados()

        pdfs_pendentes = [p for p in pdfs_disponiveis if p not in ja_indexados]

        if not pdfs_pendentes:
            count = self.contar_chunks()
            return {
                "status": "ja_indexado",
                "mensagem": f"Todos os {len(pdfs_disponiveis)} PDFs já estão indexados ({count} chunks).",
                "chunks_existentes": count,
                "documentos": pdfs_disponiveis,
            }

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " "],
        )

        embeddings = self._obter_embeddings()
        total_novos_chunks = 0
        indexados_agora: list = []
        erros: list = []
        total_pendentes = len(pdfs_pendentes)

        for idx, nome_pdf in enumerate(pdfs_pendentes, 1):
            caminho = os.path.join(DIR_DOCUMENTOS, nome_pdf)
            try:
                loader = PyPDFLoader(caminho)
                paginas = loader.load()

                if not paginas:
                    erros.append(f"{nome_pdf}: PDF sem páginas legíveis, pulado.")
                    if callback:
                        callback(nome_pdf, 0, idx, total_pendentes, erro=True)
                    continue

                chunks = splitter.split_documents(paginas)
                for chunk in chunks:
                    chunk.metadata["arquivo"] = nome_pdf

                Chroma.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    persist_directory=DIR_BASE_CONHECIMENTO,
                    collection_name=_CHROMA_COLLECTION,
                )

                total_novos_chunks += len(chunks)
                indexados_agora.append(nome_pdf)

                if callback:
                    callback(nome_pdf, len(chunks), idx, total_pendentes, erro=False)

            except Exception as exc:
                msg = str(exc)[:120].replace("\n", " ")
                erros.append(f"{nome_pdf}: {msg}")
                if callback:
                    callback(nome_pdf, 0, idx, total_pendentes, erro=True)

        total_final = self.contar_chunks()

        if not indexados_agora and erros:
            return {
                "status": "erro",
                "mensagem": "Nenhum PDF foi indexado com sucesso.",
                "erros": erros,
            }

        return {
            "status": "ok",
            "documentos_ingeridos": indexados_agora,
            "pulados": list(ja_indexados),
            "total_chunks_novos": total_novos_chunks,
            "total_chunks_base": total_final,
            "erros": erros,
        }

    def _arquivos_ja_indexados(self) -> set:
        """Consulta o ChromaDB e retorna o conjunto de nomes de arquivo já indexados."""
        try:
            import chromadb as _chromadb
            client = _chromadb.PersistentClient(path=DIR_BASE_CONHECIMENTO)
            col = client.get_or_create_collection(_CHROMA_COLLECTION)
            if col.count() == 0:
                return set()
            resultados = col.get(include=["metadatas"])
            return {m.get("arquivo", "") for m in resultados["metadatas"] if m.get("arquivo")}
        except Exception:
            return set()

    def contar_chunks(self) -> int:
        """
        Retorna quantos chunks estão indexados no ChromaDB.
        Usa o cliente nativo do ChromaDB — sem chamar a API de embeddings,
        o que evita latência ou travamento apenas para verificar a contagem.
        """
        try:
            import chromadb
            client = chromadb.PersistentClient(path=DIR_BASE_CONHECIMENTO)
            col = client.get_or_create_collection(_CHROMA_COLLECTION)
            return col.count()
        except Exception:
            return 0

    # ── Pipeline RAG (Fase 2) ─────────────────────────────────────────────────

    def _gerar_rag(
        self,
        tipo_tarefa: str,
        contexto: dict,
        callback_aviso: Optional[Callable[[str], None]] = None,
    ) -> RespostaRAG:
        """
        Pipeline RAG com 3 blindagens de cota:
          1. Top-K reduzido (_RETRIEVAL_K=4) — prompt menor, menos tokens.
          2. Contexto truncado (_MAX_CHARS_CHUNK=500) — cada chunk é comprimido.
          3. Retry com backoff (_MAX_RETRIES=3, _RETRY_WAIT_S=15s) — respeita 429.
        Uma única chamada ao Gemini por geração (sem múltiplos requests).
        """
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not GOOGLE_API_KEY:
            raise EnvironmentError(
                "GOOGLE_API_KEY não encontrada. "
                "Adicione API_KEY ou GOOGLE_API_KEY ao arquivo .env."
            )

        # ── Validação da base — Self-Healing automático ──────────────────────
        # Se a base estiver vazia (ex: primeiro deploy na nuvem sem ChromaDB),
        # o sistema ingere os PDFs automaticamente em vez de disparar erro.
        vs = self._obter_vector_store()
        if vs._collection.count() == 0:
            if callback_aviso:
                callback_aviso(
                    "🔧 **Primeiro acesso detectado.** A Base de Conhecimento Vetorial "
                    "está sendo construída automaticamente. "
                    "Isso levará cerca de 1–2 minutos no primeiro uso na nuvem..."
                )
            resultado = self.ingerir_documentos(forcar=False)
            if resultado.get("status") == "erro":
                raise ValueError(
                    f"Falha ao construir a base automaticamente: "
                    f"{resultado.get('mensagem', 'Erro desconhecido.')} "
                    "Verifique se há PDFs em data/documentos_escola/."
                )
            # Descarta o singleton vazio e abre a instância recém-construída
            EscudoRAG.limpar_cache_vector_store()
            vs = self._obter_vector_store()
            if vs._collection.count() == 0:
                raise ValueError(
                    "A base permanece vazia após a tentativa de construção automática. "
                    "Verifique se há PDFs em data/documentos_escola/."
                )
            if callback_aviso:
                callback_aviso(
                    "✅ **Base construída com sucesso!** Gerando a resposta do Escudo RAG..."
                )

        # ── BLINDAGEM 1: Top-K reduzido ───────────────────────────────────────
        # Apenas os _RETRIEVAL_K chunks mais relevantes chegam ao LLM.
        query = (
            f"{_DESCRICOES_TAREFA.get(tipo_tarefa, tipo_tarefa)} "
            f"turma {contexto.get('turma', '')} "
            f"{contexto.get('descricao', '')}"
        )
        docs_com_scores = vs.similarity_search_with_relevance_scores(
            query, k=_RETRIEVAL_K
        )

        # ── Fontes consultadas (agrupadas por arquivo, sem duplicatas) ─────────
        arquivos_vistos: dict = {}
        for doc, score in docs_com_scores:
            arq = doc.metadata.get("arquivo", "documento desconhecido")
            if arq not in arquivos_vistos:
                trecho = doc.page_content[:280].replace("\n", " ").strip()
                arquivos_vistos[arq] = {
                    "trecho": trecho + "...",
                    "relevancia": "Alta" if score >= 0.55 else "Média",
                }
        fontes = [
            FonteConsultada(documento=arq, trecho=d["trecho"], relevancia=d["relevancia"])
            for arq, d in arquivos_vistos.items()
        ]

        # ── BLINDAGEM 2: Contexto truncado por chunk ──────────────────────────
        # Cada chunk é limitado a _MAX_CHARS_CHUNK caracteres antes de ir ao prompt.
        # Isso reduz o tamanho do prompt de ~9.000 para ~2.000 chars de contexto.
        contexto_documentos = "\n\n---\n\n".join(
            f"[{doc.metadata.get('arquivo', '?')} | "
            f"pág.{doc.metadata.get('page', '?')} | "
            f"score:{score:.2f}]\n"
            f"{doc.page_content[:_MAX_CHARS_CHUNK]}"
            for doc, score in docs_com_scores
        )

        # ── Prompt único — 1 request para o Gemini ───────────────────────────
        prompt = _PROMPT_SISTEMA.format(
            tipo_tarefa_descricao=_DESCRICOES_TAREFA.get(tipo_tarefa, tipo_tarefa),
            nome_escola=contexto.get("nome_escola", NOME_ESCOLA),
            turma=contexto.get("turma", ""),
            data_referencia=contexto.get("data_referencia", ""),
            aluno=contexto.get("aluno", "N/A"),
            descricao=contexto.get("descricao", ""),
            contexto_documentos=contexto_documentos,
        )

        llm = ChatGoogleGenerativeAI(
            model=_LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
        )

        # ── BLINDAGEM 3: Retry com backoff exponencial em caso de erro 429 ────
        resposta_llm = None
        ultimo_erro = None
        for tentativa in range(1, _MAX_RETRIES + 1):
            try:
                resposta_llm = llm.invoke(prompt)
                break  # sucesso — sai do loop
            except Exception as exc:
                ultimo_erro = exc
                msg_exc = str(exc).lower()
                is_rate_limit = (
                    "429" in str(exc)
                    or "resourceexhausted" in msg_exc
                    or "quota exceeded" in msg_exc
                    or "rate limit" in msg_exc
                )
                if is_rate_limit and tentativa < _MAX_RETRIES:
                    aviso = (
                        f"⏳ Rate limit atingido (tentativa {tentativa}/{_MAX_RETRIES}). "
                        f"Aguardando {_RETRY_WAIT_S}s para a cota renovar..."
                    )
                    if callback_aviso:
                        callback_aviso(aviso)
                    time.sleep(_RETRY_WAIT_S)
                else:
                    raise  # erro não-recuperável ou tentativas esgotadas

        if resposta_llm is None:
            raise RuntimeError(
                f"Falha após {_MAX_RETRIES} tentativas. Último erro: {ultimo_erro}"
            )

        # ── Parseia o JSON da resposta ────────────────────────────────────────
        saida = self._parse_json_resposta(resposta_llm.content)

        # Aceita tanto "rascunho" (prompt padrão) quanto "draft"/"texto"/"conteudo"
        # (caso o LLM use sinônimos). Qualquer chave desconhecida cai no fallback.
        rascunho_val = (
            saida.get("rascunho")
            or saida.get("draft")
            or saida.get("texto")
            or saida.get("conteudo")
            or ""
        )
        raciocinio_val = (
            saida.get("raciocinio")
            or saida.get("reasoning")
            or saida.get("justificativa")
            or "⚠️ Raciocínio não retornado pela IA neste ciclo."
        )

        return RespostaRAG(
            rascunho=rascunho_val,
            fontes_consultadas=fontes,
            raciocinio=raciocinio_val,
            tipo_tarefa=tipo_tarefa,
            contexto_entrada=str(contexto),
        )

    # ── Pipeline Agentic — Diário de Classe ──────────────────────────────────

    def _analisar_diario_rag(
        self,
        contexto: dict,
        callback_aviso: Optional[Callable[[str], None]] = None,
    ) -> "RespostaDiario":
        """
        Versão RAG do pipeline Agentic.
        Reutiliza o mesmo vector store, retry e self-healing do pipeline gerar().
        """
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not GOOGLE_API_KEY:
            raise EnvironmentError(
                "GOOGLE_API_KEY não encontrada. "
                "Adicione API_KEY ou GOOGLE_API_KEY ao arquivo .env."
            )

        # ── Self-Healing idêntico ao gerar() ─────────────────────────────────
        vs = self._obter_vector_store()
        if vs._collection.count() == 0:
            if callback_aviso:
                callback_aviso(
                    "🔧 **Primeiro acesso detectado.** Construindo a Base de "
                    "Conhecimento Vetorial automaticamente..."
                )
            resultado = self.ingerir_documentos(forcar=False)
            if resultado.get("status") == "erro":
                raise ValueError(
                    f"Falha ao construir a base: {resultado.get('mensagem', '')}"
                )
            EscudoRAG.limpar_cache_vector_store()
            vs = self._obter_vector_store()
            if vs._collection.count() == 0:
                raise ValueError(
                    "Base vazia após tentativa de construção. "
                    "Verifique se há PDFs em data/documentos_escola/."
                )
            if callback_aviso:
                callback_aviso("✅ **Base construída!** Analisando o diário...")

        # ── Busca semântica com query voltada ao diário ───────────────────────
        relato = contexto.get("relato", "")
        query = (
            f"diário de classe turma {contexto.get('turma', '')} "
            f"comunicado falta ocorrência {relato[:300]}"
        )
        docs_com_scores = vs.similarity_search_with_relevance_scores(
            query, k=_RETRIEVAL_K
        )

        # ── Fontes consultadas ────────────────────────────────────────────────
        arquivos_vistos: dict = {}
        for doc, score in docs_com_scores:
            arq = doc.metadata.get("arquivo", "documento desconhecido")
            if arq not in arquivos_vistos:
                trecho = doc.page_content[:280].replace("\n", " ").strip()
                arquivos_vistos[arq] = {
                    "trecho": trecho + "...",
                    "relevancia": "Alta" if score >= 0.55 else "Média",
                }
        fontes = [
            FonteConsultada(documento=arq, trecho=d["trecho"], relevancia=d["relevancia"])
            for arq, d in arquivos_vistos.items()
        ]

        # ── Contexto truncado ─────────────────────────────────────────────────
        contexto_documentos = "\n\n---\n\n".join(
            f"[{doc.metadata.get('arquivo', '?')} | "
            f"pág.{doc.metadata.get('page', '?')} | score:{score:.2f}]\n"
            f"{doc.page_content[:_MAX_CHARS_CHUNK]}"
            for doc, score in docs_com_scores
        )

        # ── Prompt Agentic ────────────────────────────────────────────────────
        prompt = _PROMPT_DIARIO.format(
            nome_escola=contexto.get("nome_escola", NOME_ESCOLA),
            turma=contexto.get("turma", ""),
            data_referencia=contexto.get("data_referencia", ""),
            aluno=contexto.get("aluno", "N/A"),
            relato=relato,
            contexto_documentos=contexto_documentos,
        )

        llm = ChatGoogleGenerativeAI(
            model=_LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
        )

        # ── Retry com backoff (idêntico ao gerar()) ───────────────────────────
        resposta_llm = None
        ultimo_erro = None
        for tentativa in range(1, _MAX_RETRIES + 1):
            try:
                resposta_llm = llm.invoke(prompt)
                break
            except Exception as exc:
                ultimo_erro = exc
                msg_exc = str(exc).lower()
                is_rate_limit = (
                    "429" in str(exc)
                    or "resourceexhausted" in msg_exc
                    or "quota exceeded" in msg_exc
                    or "rate limit" in msg_exc
                )
                if is_rate_limit and tentativa < _MAX_RETRIES:
                    aviso = (
                        f"⏳ Rate limit atingido (tentativa {tentativa}/{_MAX_RETRIES}). "
                        f"Aguardando {_RETRY_WAIT_S}s para a cota renovar..."
                    )
                    if callback_aviso:
                        callback_aviso(aviso)
                    time.sleep(_RETRY_WAIT_S)
                else:
                    raise

        if resposta_llm is None:
            raise RuntimeError(
                f"Falha após {_MAX_RETRIES} tentativas. Último erro: {ultimo_erro}"
            )

        # ── Parsing do JSON Agentic ───────────────────────────────────────────
        saida = self._parse_json_resposta(resposta_llm.content)

        acoes = [
            AcaoRecomendada(
                tipo=a.get("tipo", "comunicado_familia"),
                titulo=a.get("titulo", "Ação sem título"),
                descricao=a.get("descricao", ""),
                urgencia=a.get("urgencia", "media"),
                gatilho=a.get("gatilho", ""),
            )
            for a in saida.get("next_actions", [])
            if isinstance(a, dict)
        ]

        return RespostaDiario(
            diario_formalizado=saida.get("diario_formalizado", ""),
            next_actions=acoes,
            raciocinio=saida.get("raciocinio", ""),
            fontes_consultadas=fontes,
        )

    def _analisar_diario_mock(self, contexto: dict) -> "RespostaDiario":
        """Versão mock do pipeline Agentic — para testes sem API key."""
        relato = contexto.get("relato", "")
        tem_falta = any(w in relato.lower() for w in ["falt", "ausent", "não veio", "nao veio"])
        tem_ocorrencia = any(w in relato.lower() for w in ["indisciplin", "conflit", "briga", "agress"])

        acoes: List[AcaoRecomendada] = []
        if tem_falta:
            acoes.append(AcaoRecomendada(
                tipo="comunicado_familia",
                titulo="Aviso de Falta à Família",
                descricao="Foi detectada ausência no relato. Recomenda-se comunicar o responsável.",
                urgencia="alta",
                gatilho="[MOCK] palavra-chave de falta detectada no relato",
            ))
        if tem_ocorrencia:
            acoes.append(AcaoRecomendada(
                tipo="registro_ocorrencia",
                titulo="Registro de Ocorrência Disciplinar",
                descricao="Foi detectada menção a conflito ou indisciplina. Recomenda-se formalizar a ocorrência.",
                urgencia="alta",
                gatilho="[MOCK] palavra-chave de indisciplina detectada no relato",
            ))
        if not acoes:
            acoes.append(AcaoRecomendada(
                tipo="destaque_positivo",
                titulo="Comunicado Positivo à Família",
                descricao="Sem ocorrências. Recomenda-se um comunicado de aula produtiva.",
                urgencia="baixa",
                gatilho="[MOCK] relato sem ocorrências negativas",
            ))

        return RespostaDiario(
            diario_formalizado=(
                f"[MODO SIMULAÇÃO] Diário formalizado da turma {contexto.get('turma', '')} "
                f"referente a {contexto.get('data_referencia', '')}.\n\n"
                f"Conteúdo registrado: {relato or '[sem relato]'}"
            ),
            next_actions=acoes,
            raciocinio=(
                "**[MODO SIMULAÇÃO]** Análise baseada em palavras-chave do relato.\n\n"
                "Ative o modo RAG no `.env` para análise real com documentos oficiais."
            ),
            fontes_consultadas=[
                FonteConsultada(
                    documento="[MOCK] Regimento Escolar",
                    trecho="Diretrizes de comunicação escola-família...",
                    relevancia="Alta",
                )
            ],
        )

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _obter_embeddings(self):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        if not GOOGLE_API_KEY:
            raise EnvironmentError(
                "GOOGLE_API_KEY não encontrada no arquivo .env."
            )
        return GoogleGenerativeAIEmbeddings(
            model=_EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY,
        )

    def _obter_vector_store(self):
        """
        Lazy singleton: abre a conexão ChromaDB apenas na primeira chamada
        e reutiliza a mesma instância em todas as buscas seguintes.
        Isso evita o overhead de re-abrir o banco a cada render do Streamlit,
        eliminando o ERR_CONNECTION_REFUSED por timeout na inicialização.
        """
        if "vs" not in _VS_CACHE:
            from langchain_chroma import Chroma
            _VS_CACHE["vs"] = Chroma(
                persist_directory=DIR_BASE_CONHECIMENTO,
                embedding_function=self._obter_embeddings(),
                collection_name=_CHROMA_COLLECTION,
            )
        return _VS_CACHE["vs"]

    @staticmethod
    def limpar_cache_vector_store() -> None:
        """Descarta a instância em cache (chame após re-indexação)."""
        _VS_CACHE.clear()

    @staticmethod
    def _parse_json_resposta(conteudo: str) -> dict:
        """
        Extrai JSON da resposta do LLM de forma robusta.

        Estratégia em 5 tentativas, da mais simples para a mais agressiva:
          1. Parse direto (LLM seguiu o prompt certinho).
          2. Remove SOMENTE o bloco de código externo (```json ... ```) sem usar
             MULTILINE, que corromperia ``` dentro do conteúdo JSON.
          3. Sanitiza quebras de linha literais dentro de valores de string e
             re-tenta o parse (erro mais comum do Gemini).
          4. Extrai entre o primeiro '{' e o último '}' do texto limpo, com e
             sem sanitização de literais.
          5. Fallback: devolve o texto bruto em "rascunho" para o frontend tratar.
        """
        conteudo = conteudo.strip()

        # Tentativa 1 — parse direto
        try:
            result = json.loads(conteudo)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        # Tentativa 2 — remove wrapper ```json ... ``` externo (sem MULTILINE)
        # Limpa APENAS a primeira linha se for ```json e a última se for ```
        linhas = conteudo.splitlines()
        if linhas and linhas[0].strip().startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        conteudo_limpo = "\n".join(linhas).strip()

        try:
            result = json.loads(conteudo_limpo)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        # Tentativa 3 — sanitiza literais de controle e re-tenta o parse direto.
        # Corrige o erro mais comum do Gemini: quebras de linha literais dentro
        # de valores de string JSON (ex: "rascunho": "linha1\nlinha2" sem escape).
        conteudo_sanitizado = _sanitize_json_literals(conteudo_limpo)
        if conteudo_sanitizado != conteudo_limpo:
            try:
                result = json.loads(conteudo_sanitizado)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

        # Tentativa 4 — extrai entre primeiro { e último } (com e sem sanitização)
        idx_abre = conteudo_limpo.find("{")
        idx_fecha = conteudo_limpo.rfind("}")
        if idx_abre != -1 and idx_fecha != -1 and idx_fecha > idx_abre:
            candidato = conteudo_limpo[idx_abre : idx_fecha + 1]
            for texto in (candidato, _sanitize_json_literals(candidato)):
                try:
                    result = json.loads(texto)
                    if isinstance(result, dict):
                        return result
                except json.JSONDecodeError:
                    pass

        # Tentativa 5 — fallback: retorna o texto bruto para o frontend renderizar
        return {
            "rascunho": conteudo_limpo or conteudo,
            "raciocinio": (
                "⚠️ O raciocínio não pôde ser extraído automaticamente. "
                "O texto acima é a resposta bruta da IA. Revise com atenção antes de aprovar."
            ),
        }

    # ── Mock (Fase 1 — mantido para testes sem API key) ───────────────────────

    MOCKS: dict = {
        "comunicado_pais": {
            "rascunho": (
                "Prezados Responsáveis,\n\n"
                "Informamos que, conforme o Calendário Escolar aprovado pelo Conselho Pedagógico "
                "(Resolução CP-2026/01), não haverá aula na próxima {data_referencia} em virtude "
                "de {descricao}.\n\n"
                "As atividades serão retomadas normalmente no dia seguinte, no horário habitual.\n\n"
                "Contamos com a compreensão de todos.\n\n"
                "Atenciosamente,\n"
                "Coordenação Pedagógica — {nome_escola}"
            ),
            "fontes": [
                FonteConsultada(
                    documento="[MOCK] Calendário Escolar 2026 — Resolução CP-2026/01",
                    trecho="Art. 4º — Os comunicados oficiais devem ser emitidos com no mínimo 48h de antecedência...",
                    relevancia="Alta",
                ),
                FonteConsultada(
                    documento="[MOCK] Manual de Comunicação Escola-Família, p. 12",
                    trecho="O tom dos comunicados deve ser cordial, objetivo e isento de julgamentos...",
                    relevancia="Média",
                ),
            ],
            "raciocinio": (
                "**[MODO SIMULAÇÃO]** Tarefa identificada como comunicado oficial. "
                "Este rascunho é gerado a partir de um template fixo, sem consulta real aos documentos. "
                "Ative o modo RAG no `.env` para usar os documentos reais da escola."
            ),
        },
        "registro_ocorrencia": {
            "rascunho": (
                "REGISTRO DE OCORRÊNCIA\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Aluno: {aluno}\n"
                "Turma: {turma}\n"
                "Data: {data_referencia}\n\n"
                "Descrição do fato:\n"
                "{descricao}\n\n"
                "Providências adotadas:\n"
                "— Conversa individual com o aluno.\n"
                "— Notificação ao responsável pendente de aprovação do(a) professor(a).\n\n"
                "Observação: Este registro é preliminar e aguarda supervisão e assinatura.\n\n"
                "Professor(a): ___________________________\n"
                "Data do registro: {data_referencia}"
            ),
            "fontes": [
                FonteConsultada(
                    documento="[MOCK] Regimento Escolar — Art. 38, § 2º",
                    trecho="Todo registro deve conter: data, identificação do aluno, descrição objetiva e providências...",
                    relevancia="Alta",
                ),
            ],
            "raciocinio": (
                "**[MODO SIMULAÇÃO]** Template fixo de registro disciplinar. "
                "Ative o modo RAG para consultar o Regimento Escolar real."
            ),
        },
        "licao_de_casa": {
            "rascunho": (
                "📚 LIÇÃO DE CASA — {turma}\n"
                "Data de entrega: {data_referencia}\n\n"
                "{descricao}\n\n"
                "Orientações:\n"
                "• Realize as atividades de forma individual.\n"
                "• Em caso de dúvidas, anote-as para perguntar em aula.\n\n"
                "— Prof(a): {nome_escola}"
            ),
            "fontes": [
                FonteConsultada(
                    documento="[MOCK] Plano de Ensino — Diretrizes de Atividades Domiciliares",
                    trecho="As atividades domiciliares devem ter prazo definido e estar alinhadas ao conteúdo...",
                    relevancia="Alta",
                ),
            ],
            "raciocinio": (
                "**[MODO SIMULAÇÃO]** Template fixo de lição de casa. "
                "Ative o modo RAG para consultar as diretrizes reais do Plano de Ensino."
            ),
        },
    }

    def _gerar_mock(self, tipo_tarefa: str, contexto: dict) -> RespostaRAG:
        template = self.MOCKS.get(tipo_tarefa, self.MOCKS["comunicado_pais"])

        class _Default(dict):
            def __missing__(self, key: str) -> str:
                return f"[{key}]"

        dados = _Default({**contexto, "nome_escola": contexto.get("nome_escola", NOME_ESCOLA)})
        rascunho = template["rascunho"].format_map(dados)
        return RespostaRAG(
            rascunho=rascunho,
            fontes_consultadas=template["fontes"],
            raciocinio=template["raciocinio"],
            tipo_tarefa=tipo_tarefa,
            contexto_entrada=str(contexto),
        )
