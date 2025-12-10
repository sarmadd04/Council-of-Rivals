import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
import pickle
import os
from .config import DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, BM25_PATH

class VectorStore:
    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=self.ef)
        
        # Load BM25 Index (if exists)
        self.bm25 = None
        self.bm25_corpus = []
        if os.path.exists(BM25_PATH):
            with open(BM25_PATH, "rb") as f:
                data = pickle.load(f)
                self.bm25 = data["index"]
                self.bm25_corpus = data["corpus"]

    def check_cache(self, query):
        """Optimization: Returns cached answer if query is similar to a previous one"""
        results = self.collection.query(query_texts=[query], n_results=1)
        if results['documents'] and results['distances'][0][0] < 0.1: # Very strict similarity
            # In a real app, you'd store the ANSWER in metadata. 
            # For this demo, we just signal a 'hit' to show the logic.
            return True
        return False

    def hybrid_search(self, query, top_k=3):
        """Combines Vector Search (Semantic) + BM25 (Keyword)"""
        unique_docs = set()
        
        # 1. Vector Search
        vector_results = self.collection.query(query_texts=[query], n_results=top_k)
        if vector_results['documents']:
            for doc in vector_results['documents'][0]:
                unique_docs.add(doc)

        # 2. BM25 Search (Keyword Fallback)
        if self.bm25:
            tokenized_query = query.lower().split()
            # Get top docs from BM25
            keyword_docs = self.bm25.get_top_n(tokenized_query, self.bm25_corpus, n=top_k)
            for doc in keyword_docs:
                unique_docs.add(doc)
        
        return list(unique_docs)