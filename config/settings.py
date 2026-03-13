import os
from dotenv import load_dotenv

load_dotenv()

# Suporta tanto GOOGLE_API_KEY (padrão LangChain) quanto API_KEY (alias local)
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY", "")

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
NOME_ESCOLA: str = os.getenv("NOME_ESCOLA", "Escola Modelo")
MODO_OPERACAO: str = os.getenv("MODO_OPERACAO", "mock")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DOCUMENTOS = os.path.join(BASE_DIR, "data", "documentos_escola")
DIR_BASE_CONHECIMENTO = os.path.join(BASE_DIR, "data", "base_conhecimento")
DIR_LOGS = os.path.join(BASE_DIR, "data", "logs")

for _dir in [DIR_DOCUMENTOS, DIR_BASE_CONHECIMENTO, DIR_LOGS]:
    os.makedirs(_dir, exist_ok=True)
