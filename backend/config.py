import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_FOLDER = os.path.join(BASE_DIR, "documents")
DB_PATH = os.path.join(BASE_DIR, "db", "chroma_db")
BM25_PATH = os.path.join(BASE_DIR, "db", "bm25.pkl")

# Database Settings
COLLECTION_NAME = "council_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Search Settings
SIMILARITY_THRESHOLD = 0.3 
TOP_K = 3
CACHE_THRESHOLD = 0.1

# Model Settings (SINGLE SOURCE OF TRUTH)
MODEL_NAME = "llama3.2:1b"