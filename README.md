# 🏛️ Council of Rivals: Multi-Agent Financial Decision Support System

### 🚀 Project Overview
**Council of Rivals** is a **Financial Decision Support System** that uses **Adversarial Multi-Agent AI** to simulate an Investment Committee. Unlike standard RAG chatbots that simply retrieve text, AlphaSeeker instantiates three distinct personas—a **Strategic Advisor (Bull)**, a **Risk Auditor (Bear)**, and a **Chief Investment Officer (Judge)**—to debate financial data and render a nuanced verdict.



### 🧠 Key Features
* **Adversarial RAG Architecture:** Agents explicitly attack each other's reasoning to reduce hallucination and bias.
* **Tiered Decision Logic:** The "Judge" agent uses a hierarchical logic gate (Survival > Growth) to prevent reckless optimism.
* **Hybrid Retrieval Engine:** Combines **Vector Search** (Semantic) with **BM25** (Keyword) for precise financial lookup.
* **Session-Scoped Analysis:** Users can upload live financial PDFs (Balance Sheets, Pitch Decks) for instant, isolated analysis without retraining the DB.
* **Reasoning Transfer:** The system applies "Mental Models" from its long-term memory (e.g., Fed Reports) to analyze new, unseen user scenarios.

### 🛠️ Tech Stack
* **Engine:** Llama 3.2 (1B/3B Quantized via Ollama)
* **Orchestration:** Python, Custom Agent Logic
* **Database:** ChromaDB (Vector) + RankBM25 (Sparse)
* **Frontend:** Streamlit (Financial Dashboard UI)
* **Hardware Optimization:** Optimized for CPU inference (Iris Xe / M1) using GGUF quantization.

### ⚙️ How to Run
1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/alphaseeker.git](https://github.com/yourusername/alphaseeker.git)
    cd alphaseeker
    ```
2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Ollama & Model**
    - Download [Ollama](https://ollama.com/)
    - Run: `ollama pull llama3.2:1b`
4.  **Ingest Knowledge Base**
    ```bash
    python ingest.py
    ```
5.  **Launch the Dashboard**
    ```bash
    streamlit run app.py
    ```

### 📊 System Architecture
**1. Ingestion Layer:**
   - PDFs are chunked (500 chars) with 50-char overlap to preserve financial context.
   - Dual-indexing: Semantic Vectors (`all-MiniLM-L6-v2`) + Keyword Index (`BM25`).

**2. Reasoning Layer:**
   - **Agent A (Bull):** Focuses on Revenue CAGR, Synergies, and Moats.
   - **Agent B (Bear):** Focuses on Solvency, Debt Covenants, and Regulatory Risk.
   - **Judge (CIO):** Evaluates "Fatal Flaws" before considering "Growth Potential."

---
*Disclaimer: This tool is for academic research and demonstrates AI reasoning capabilities. It does not constitute real financial advice.*