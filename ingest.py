import os
import pickle
import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
from backend.config import DOCS_FOLDER, DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, BM25_PATH

def main():
    print("🚀 Starting Advanced Ingestion...")
    
    # 1. Setup Chroma
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=DB_PATH)
    # Reset DB
    try: client.delete_collection(COLLECTION_NAME)
    except: pass
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    # 2. Process PDFs
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        print(f"⚠️ Created {DOCS_FOLDER}. Put your PDFs there and run again!")
        return

    files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith('.pdf')]
    all_chunks = []
    
    for file in files:
        print(f"📄 Processing {file}...")
        loader = PyPDFLoader(os.path.join(DOCS_FOLDER, file))
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        for chunk in chunks:
            all_chunks.append(chunk.page_content)

    if not all_chunks:
        print("❌ No text found. Add PDFs!")
        return

    # 3. Store Vectors
    print(f"💾 Vectorizing {len(all_chunks)} chunks...")
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        ids = [f"id_{j}" for j in range(i, i+len(batch))]
        collection.add(documents=batch, ids=ids)

    # 4. Build & Save BM25 Index (The "Hybrid" Part)
    print("🔍 Building BM25 Keyword Index...")
    tokenized_corpus = [doc.lower().split() for doc in all_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Save index + raw text (needed for retrieval)
    with open(BM25_PATH, "wb") as f:
        pickle.dump({"index": bm25, "corpus": all_chunks}, f)

    print("✅ System Ready. Run 'streamlit run app.py'")

if __name__ == "__main__":
    main()