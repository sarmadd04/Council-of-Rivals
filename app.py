import streamlit as st
import time
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

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #30333d;
        border-radius: 5px;
        padding: 15px;
        color: white;
    }
    .chat-bubble {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #30333d;
    }
    .user-bubble { background-color: #262730; }
    .bot-bubble { background-color: #0e1117; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'engine' not in st.session_state:
    st.session_state.engine = CouncilEngine()

if 'debate_results' not in st.session_state:
    st.session_state.debate_results = None 

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [] 
    
if 'uploaded_text' not in st.session_state:
    st.session_state.uploaded_text = None

# --- SIDEBAR: ANALYST CONTROL ---
with st.sidebar:
    st.title("🏦 Analyst Control")
    st.markdown("---")
    
    st.markdown("### 📂 Case File (Session Only)")
    st.caption("Upload a specific document (e.g., Balance Sheet) for this analysis. It will NOT be saved to the DB.")
    
    # The Uploader
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    if uploaded_file:
        with st.spinner("Processing File..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            st.session_state.uploaded_text = raw_text
        st.success("✅ File Loaded into Context")
    else:
        st.session_state.uploaded_text = None

    st.markdown("---")
    st.caption(f"🟢 Engine: `{MODEL_NAME}`")
    
    # "New Debate" Button
    if st.button("🔄 Start New Analysis"):
        st.session_state.debate_results = None
        st.session_state.chat_history = []
        st.rerun()

# --- MAIN PAGE LOGIC ---
st.title("📈 Council of Rivals")

# 1. SHOW INPUT ONLY IF NO DEBATE EXISTS
if st.session_state.debate_results is None:
    st.markdown("### `Multi-Agent Financial Decision Support System`")
    query = st.text_area("Enter Investment Thesis or Ticker Strategy:", 
                         height=100, 
                         placeholder="e.g., Analyze the risk in the attached balance sheet.")

    if st.button("🚀 Analyze Market Position") and query:
        # RUN THE DEBATE
        with st.spinner("The Committee is in session..."):
            
            # Pass both the Query AND the Uploaded Text (if any)
            response = st.session_state.engine.run_debate(
                user_query=query,
                user_upload_text=st.session_state.uploaded_text
            )
            
            # Save Topic for context
            response['topic'] = query 
            
            # SAVE TO SESSION STATE
            st.session_state.debate_results = response
            st.rerun() 

# 2. SHOW RESULTS & CHAT IF DEBATE EXISTS
else:
    results = st.session_state.debate_results
    
    # --- DISPLAY DEBATE DASHBOARD ---
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

    # --- THE NEW CHAT INTERFACE ---
    st.markdown("---")
    st.subheader("💬 Q&A with the Chief Investment Officer")
    st.caption("Ask follow-up questions about the verdict above.")

    # Display Chat History
    for msg in st.session_state.chat_history:
        role = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"<div class='chat-bubble {role}'><b>{icon}:</b> {msg['content']}</div>", unsafe_allow_html=True)

    # Chat Input
    if user_input := st.chat_input("Ex: Why did you favor the Bear case?"):
        # 1. Add User to History
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # 2. Call the Backend Function
        with st.spinner("The CIO is typing..."):
            reply = st.session_state.engine.chat_with_judge(
                user_message=user_input,
                debate_context=results,
                chat_history=st.session_state.chat_history
            )
            
        # 3. Add Bot to History
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()