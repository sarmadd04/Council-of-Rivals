import streamlit as st
import time
import pandas as pd
from datetime import datetime
from backend.llm import CouncilEngine
from backend.config import MODEL_NAME
import pypdf

# --- HELPER: PDF READER ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Council of Rivals",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main Card Style */
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #30333d;
        border-radius: 8px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    
    /* Telemetry Row Style */
    .telemetry-row {
        display: flex;
        justify-content: space-around;
        align-items: center;
        text-align: center;
    }
    
    .telemetry-item {
        flex: 1;
        border-right: 1px solid #30333d;
    }
    
    .telemetry-item:last-child {
        border-right: none;
    }
    
    .telemetry-label {
        font-size: 0.85rem;
        color: #8b92a6;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    
    .telemetry-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #00e5ff; /* Cyan accent for numbers */
    }

    /* Chat Bubbles */
    .chat-bubble {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid #30333d;
        line-height: 1.5;
    }
    .user-bubble { background-color: #262730; color: #e0e0e0; }
    .bot-bubble { background-color: #0e1117; color: #ffffff; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'engine' not in st.session_state:
    st.session_state.engine = CouncilEngine()

if 'debate_results' not in st.session_state:
    st.session_state.debate_results = None 

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [] 

if 'metric_history' not in st.session_state:
    st.session_state.metric_history = []
    
if 'uploaded_text' not in st.session_state:
    st.session_state.uploaded_text = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏦 Analyst Control")
    st.markdown("---")
    
    st.markdown("### 📂 Case File (Session Only)")
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    if uploaded_file:
        with st.spinner("Processing File..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            st.session_state.uploaded_text = raw_text
        st.success("✅ File Loaded")
    else:
        st.session_state.uploaded_text = None

    st.markdown("---")
    if st.button("🔄 Start New Analysis", use_container_width=True):
        st.session_state.debate_results = None
        st.session_state.chat_history = []
        st.session_state.metric_history = [] # Clear logs on reset
        st.rerun()

# --- MAIN PAGE LOGIC ---
st.title("📈 Council of Rivals")

# 1. SHOW INPUT ONLY IF NO DEBATE EXISTS
if st.session_state.debate_results is None:
    st.markdown("### `Multi-Agent Financial Decision Support System`")
    query = st.text_area("Enter Investment Thesis or Ticker Strategy:", 
                         height=100, 
                         placeholder="e.g., Analyze the risk in the attached balance sheet.")

    if st.button("🚀 Analyze Market Position", type="primary") and query:
        with st.spinner("The Committee is in session..."):
            
            # --- START TIMER ---
            start_time = time.time()
            
            response = st.session_state.engine.run_debate(
                user_query=query,
                user_upload_text=st.session_state.uploaded_text
            )
            
            # --- END TIMER & LOG ---
            duration = round(time.time() - start_time, 2)
            
            # Record initial debate metrics
            st.session_state.metric_history.append({
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Action": "Initial Debate",
                "Latency (s)": duration,
                "Tokens Used": 4500, # Mocked (replace with real usage)
                "Cost ($)": 0.045
            })
            
            response['topic'] = query 
            st.session_state.debate_results = response
            st.rerun() 

# 2. SHOW RESULTS & CHAT IF DEBATE EXISTS
else:
    results = st.session_state.debate_results
    
    # --- DEBATE CONTENT ---
    st.markdown(f"### 🎯 Topic: {results['topic']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🐂 The Strategic Advisor")
        st.markdown(f"<div class='metric-card'>{results['agent_a']}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("### 🐻 The Risk Auditor")
        st.markdown(f"<div class='metric-card'>{results['agent_b']}</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 CIO Verdict")
    st.info(results['judge'])

    # --- CHAT INTERFACE ---
    st.markdown("---")
    st.subheader("💬 Q&A with the Chief Investment Officer")
    
    # Display Chat History
    for msg in st.session_state.chat_history:
        role = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"<div class='chat-bubble {role}'><b>{icon}:</b> {msg['content']}</div>", unsafe_allow_html=True)

    # Chat Input
    if user_input := st.chat_input("Ex: Why did you favor the Bear case?"):
        # 1. Add User to History
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # 2. Run Backend & Time it
        start_time = time.time()
        
        with st.spinner("The CIO is typing..."):
            reply = st.session_state.engine.chat_with_judge(
                user_message=user_input,
                debate_context=results,
                chat_history=st.session_state.chat_history
            )
        
        duration = round(time.time() - start_time, 2)
        
        # 3. Log Metrics for this specific turn
        st.session_state.metric_history.append({
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Action": "Chat Query",
            "Latency (s)": duration,
            "Tokens Used": 850, # Mocked
            "Cost ($)": 0.008
        })

        # 4. Add Bot to History
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    # --- FOOTER: SYSTEM TELEMETRY (UPDATED) ---
    st.markdown("---")
    st.markdown("### 🛠️ System Logs & Performance Telemetry")
    
    if st.session_state.metric_history:
        # Get the very last event for the "Big Cards"
        last_metric = st.session_state.metric_history[-1]
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="telemetry-row">
                <div class="telemetry-item">
                    <div class="telemetry-label">Last Latency</div>
                    <div class="telemetry-value">{last_metric['Latency (s)']}s</div>
                </div>
                <div class="telemetry-item">
                    <div class="telemetry-label">Est. Tokens</div>
                    <div class="telemetry-value">{last_metric['Tokens Used']}</div>
                </div>
                 <div class="telemetry-item">
                    <div class="telemetry-label">Compute Cost</div>
                    <div class="telemetry-value">${last_metric['Cost ($)']}</div>
                </div>
                <div class="telemetry-item">
                    <div class="telemetry-label">Model</div>
                    <div class="telemetry-value">Quantized GGUF</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show Full History Table
        with st.expander("📜 View Full Session Log (Latency History)", expanded=True):
            df_log = pd.DataFrame(st.session_state.metric_history)
            st.dataframe(
                df_log, 
                use_container_width=True, 
                column_config={
                    "Latency (s)": st.column_config.NumberColumn(format="%.2f s"),
                    "Cost ($)": st.column_config.NumberColumn(format="$ %.4f")
                }
            )