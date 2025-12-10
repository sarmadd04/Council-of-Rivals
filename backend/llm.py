import ollama
from .database import VectorStore
from .config import MODEL_NAME

class CouncilEngine:
    def __init__(self):
        self.db = VectorStore()

    def query_ollama(self, messages):
        """
        Helper function that uses the SINGLE global model defined in config.py.
        """
        try:
            response = ollama.chat(model=MODEL_NAME, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error connecting to Ollama: {e}"

    def run_debate(self, user_query, user_upload_text=None):
        """
        Phase 1: The Main Council Debate
        Now handles 'Session-Scoped' uploads as the primary evidence.
        """
        
        # 1. Retrieval Strategy (The "Mental Model" Fetch)
        # We search the Permanent DB for frameworks/principles relevant to the query
        # This gives the AI "General Financial Wisdom" (e.g. from Nvidia/Fed docs)
        context_list = self.db.hybrid_search(user_query)
        
        # 2. Context Construction (Combining Precedent + Evidence)
        
        # A. The "Textbook" (Permanent DB)
        db_context = "\n\n".join(context_list) if context_list else "General Financial Logic"
        
        # B. The "Case File" (User Upload)
        if user_upload_text:
            # We truncate the upload to ~6000 chars to prevent crashing the 1B model's context window
            evidence_block = f"USER UPLOADED EVIDENCE:\n{user_upload_text[:6000]}...\n(Truncated)"
            source_mode = "Direct Analysis of Uploaded Evidence"
        else:
            evidence_block = "No specific file uploaded. Relying on user query description."
            source_mode = "General Analysis"

        # --- PROMPT ENGINEERING ---
        
        # AGENT A: THE STRATEGIC ADVISOR
        sys_a = f"""
        You are a Strategic Financial Advisor.
        
        YOUR GOAL: 
        Analyze the USER'S SCENARIO using the uploaded EVIDENCE.
        Use the MENTAL MODELS from the database (Context) to guide your analysis.
        
        INSTRUCTIONS:
        1. Primary Source: Analyze the 'USER UPLOADED EVIDENCE' (if any).
        2. Framework: Apply the growth/strategy principles found in 'MENTAL MODEL'.
        3. Advice: Be optimistic. Find the growth angles in the user's file.
        """
        
        user_block = f"""
        MENTAL MODEL (Textbook Principles):
        {db_context}
        
        ---
        
        CASE EVIDENCE (User's File):
        {evidence_block}
        
        ---
        
        USER QUESTION:
        {user_query}
        
        ADVICE:
        """
        
        res_a = self.query_ollama([{"role": "system", "content": sys_a}, {"role": "user", "content": user_block}])

        # AGENT B: THE RISK AUDITOR
        sys_b = f"""
        You are a Senior Risk Auditor.
        
        YOUR GOAL: 
        Audit the 'USER UPLOADED EVIDENCE' for risks, using the frameworks in 'MENTAL MODEL'.
        
        INSTRUCTIONS:
        1. Scrutinize the user's file. Look for debt, inconsistencies, or over-optimism.
        2. Critique Agent A's analysis.
        3. Be harsh.
        """
        
        # Agent B sees A's advice too
        res_b = self.query_ollama([{"role": "system", "content": sys_b}, 
                                   {"role": "user", "content": user_block + f"\n\nAGENT A'S ADVICE:\n{res_a}"}])

        # THE JUDGE
        sys_j = """
        You are a Chief Investment Officer (CIO). 
        Make a FINAL DECISION based on the Evidence.
        
        Output Strict JSON style:
        1. **The Decision:** (Actionable Verdict).
        2. **Evidence Used:** (Did you use the upload or just general principles?).
        3. **Confidence:** (0-100%).
        4. **Action Plan:** Concrete steps.
        """
        
        verdict = self.query_ollama([{"role": "system", "content": sys_j}, 
                                     {"role": "user", "content": f"User Query: {user_query}\nAdvisor: {res_a}\nAuditor: {res_b}\nVerdict:"}])

        return {
            "context": source_mode, # Just a label for the UI
            "agent_a": res_a,
            "agent_b": res_b,
            "judge": verdict
        }

    def chat_with_judge(self, user_message, debate_context, chat_history):
        """
        Phase 2: The Follow-up Chat (Talk to the CIO)
        """
        # Construct the "Memory" of the debate
        memory_block = f"""
        PREVIOUS DEBATE CONTEXT:
        User Scenario: {debate_context.get('topic', 'Financial Scenario')}
        Advisor Argument: {debate_context['agent_a']}
        Auditor Argument: {debate_context['agent_b']}
        CIO Verdict: {debate_context['judge']}
        """

        # System Prompt for the Chat Mode
        sys_chat = """
        You are the Chief Investment Officer (The Judge) from the previous debate.
        Your Job: Answer follow-up questions from the client based strictly on the debate results.
        
        Rules:
        - Maintain your professional, balanced persona.
        - Refer back to specific points Agent A or Agent B made.
        - If the user asks "Why?", explain your verdict reasoning deeper.
        - Keep answers concise (under 3 sentences).
        """
        
        # Build Message History
        messages = [{"role": "system", "content": sys_chat + memory_block}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})
        
        return self.query_ollama(messages)