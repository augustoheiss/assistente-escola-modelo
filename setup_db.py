"""
setup_db.py -- Ingestao resiliente dos documentos da escola no ChromaDB.

Comportamento padrao (retomada inteligente):
    python setup_db.py
    -> Consulta o ChromaDB, pula os PDFs ja indexados e processa apenas os pendentes.

Para reindexar tudo do zero:
    python setup_db.py --forcar
"""

import sys
import os

# Garante saida UTF-8 no Windows para nomes de arquivo com caracteres especiais
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.escudo_rag import EscudoRAG

forcar = "--forcar" in sys.argv

print("=" * 60)
print("  Escudo RAG -- Ingestao de Documentos")
print("=" * 60, flush=True)

escudo = EscudoRAG()

# Relatorio de estado atual
ja_indexados = escudo._arquivos_ja_indexados()
chunks_atuais = escudo.contar_chunks()

print(f"\n[ESTADO] {len(ja_indexados)} arquivo(s) ja indexados | {chunks_atuais} chunks na base")

pdfs_dir = os.path.join(os.path.dirname(__file__), "data", "documentos_escola")
todos_pdfs = sorted(f for f in os.listdir(pdfs_dir) if f.lower().endswith(".pdf"))
pendentes = [p for p in todos_pdfs if p not in ja_indexados]

if forcar:
    print(f"[MODO]   --forcar: apagando base e reiniciando do zero ({len(todos_pdfs)} PDFs)")
elif not pendentes:
    print(f"\n[OK] Todos os {len(todos_pdfs)} PDFs ja estao indexados.")
    print(f"     Use --forcar para re-indexar tudo do zero.\n")
    sys.exit(0)
else:
    print(f"[MODO]   Retomada: {len(ja_indexados)} prontos, {len(pendentes)} pendentes")
    print(f"\n[PENDENTES]")
    for p in pendentes:
        print(f"  - {p}")

print(f"\n[INICIO] Processando PDFs pendentes...\n", flush=True)

erros_totais = []


def progresso(nome_pdf, n_chunks, atual, total, erro=False):
    nome_safe = nome_pdf.encode("ascii", "replace").decode("ascii")
    if erro:
        print(f"  [ERRO {atual}/{total}] {nome_safe} -> falhou, pulado.", flush=True)
    else:
        print(f"  [{atual}/{total}] {nome_safe} -> {n_chunks} chunks indexados.", flush=True)


resultado = escudo.ingerir_documentos(forcar=forcar, callback=progresso)

print()
print("-" * 60)

if resultado["status"] == "ok":
    novos = len(resultado.get("documentos_ingeridos", []))
    print(f"[OK] Ingestao concluida!")
    print(f"     Novos PDFs indexados : {novos}")
    print(f"     Novos chunks         : {resultado.get('total_chunks_novos', 0)}")
    print(f"     Total na base agora  : {resultado.get('total_chunks_base', 0)}")
    erros = resultado.get("erros", [])
    if erros:
        print(f"\n[AVISOS] {len(erros)} arquivo(s) com problema:")
        for e in erros:
            print(f"  - {e[:100]}")
elif resultado["status"] == "ja_indexado":
    print(resultado["mensagem"])
else:
    print(f"[ERRO] {resultado.get('mensagem', 'Erro desconhecido.')}")
    for e in resultado.get("erros", []):
        print(f"  - {e[:100]}")
    sys.exit(1)

print("-" * 60)
chunks_finais = escudo.contar_chunks()
print(f"\n[FIM] Base de conhecimento: {chunks_finais} chunks em data/base_conhecimento/")
print("      Inicie o app com: streamlit run app/main.py\n")
