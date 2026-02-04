import streamlit as st
import ollama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import graphviz
# --- SETUP ---
st.set_page_config(page_title="Cyber Kill Chain AI Analyst", layout="wide")
DB_DIR = "cyber_db"
EMBED_MODEL = "nomic-embed-text"
REASONING_MODEL = "mychen76/Fin-R1:Q5"

@st.cache_resource
def load_db():
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

db = load_db()

# --- UI ---
st.title("🛡️ Cyber Kill Chain Visualizer")
query = st.text_input("Enter a CVE or Threat Scenario (e.g., 'Log4Shell analysis'):")

if query:
    with st.spinner("Analyzing threat patterns..."):
        # 1. Retrieval
        docs = db.similarity_search(query, k=3)
        context = "\n".join([d.page_content for d in docs])
        
        # 2. Reasoning with Fin-R1
        prompt = f"""
        Context: {context}
        Task: Analyze the following query through the 7 steps of the Cyber Kill Chain.
        Query: {query}
        
        For each of the 7 steps, provide a 1-sentence description of how this threat manifests.
        Format your response as:
        Step 1: [description]
        Step 2: [description]
        ...etc.
        """
        
        response = ollama.chat(model=REASONING_MODEL, messages=[{'role': 'user', 'content': prompt}])
        full_text = response['message']['content']
        
        # 3. Visualization Logic
        st.subheader("Attack Progression Graph")
        dot = graphviz.Digraph()
        dot.attr(rankdir='LR', size='10,5')
        
        # Define the Kill Chain Nodes
        stages = [
            "Recon", "Weaponize", "Delivery", "Exploit", 
            "Install", "C2", "Actions"
        ]
        
        for i, stage in enumerate(stages):
            dot.node(stage, stage, shape="box", style="filled", color="lightblue")
            if i > 0:
                dot.edge(stages[i-1], stages[i])
        
        st.graphviz_chart(dot)
        
        # 4. Detailed Breakdown
        st.markdown("### Technical Breakdown")
        st.write(full_text)