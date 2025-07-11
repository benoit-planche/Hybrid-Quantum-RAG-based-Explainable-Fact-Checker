import os
import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import pandas as pd
import re
from ollama_config import config
from ollama_utils import OllamaClient, OllamaEmbeddings, format_prompt, extract_verdict, SimpleTextSplitter
from mmr_utils import mmr_similarity_search
from dotenv import load_dotenv
from pdf_loader import PDFDocumentLoader
from chromadb_manager import ChromaDBManager
from llamaindex_utils import LlamaIndexChromaDBManager, create_llamaindex_chromadb_manager

# Streamlit page configuration - MUST be first!
st.set_page_config(
    page_title="RAG-based Explainable Fact-Checker",
    page_icon="🔍",
    layout="wide"
)

# Load environment variables from .env file
load_dotenv()

# Initialize Ollama client
ollama_client = OllamaClient()

# Initialize ChromaDB with LlamaIndex
try:
    # Use LlamaIndex ChromaDB manager with MMR support
    chroma_manager = create_llamaindex_chromadb_manager(
        persist_directory="./chroma_db"
    )
    st.success("✅ ChromaDB avec LlamaIndex initialisé avec succès")
    
    # Afficher les informations de la collection
    collection_info = chroma_manager.get_collection_info()
    if collection_info:
        st.info(f"📊 Collection: {collection_info.get('document_count', 0)} documents indexés")
        st.info(f"🤖 Modèle d'embedding: {chroma_manager.embedding_model}")
    
except Exception as e:
    st.error(f"❌ Erreur d'initialisation ChromaDB LlamaIndex: {e}")
    chroma_manager = None

# Define prompts as templates
retrieval_prompt_template = """I need to fact check the following claim:

Claim: {claim}

What specific keywords or search queries should I use to find reliable information related to this claim?
Please provide 3-5 different search queries that would help gather relevant evidence.
"""

analysis_prompt_template = """You are an objective fact-checker. Your job is to verify the following claim using ONLY the provided evidence.

Claim: {claim}

Evidence:
{retrieved_docs}

Please analyze the claim step by step:
1. Break down the claim into its key components
2. For each component, identify supporting or contradicting evidence from the provided sources
3. Note any missing information that would be needed for a complete verification
4. Assign a verdict to the claim from the following options:
   - TRUE: The claim is completely supported by the evidence
   - MOSTLY TRUE: The claim is mostly accurate but contains minor inaccuracies
   - MIXED: The claim contains both accurate and inaccurate elements
   - MOSTLY FALSE: The claim contains some truth but is misleading overall
   - FALSE: The claim is contradicted by the evidence
   - UNVERIFIABLE: Cannot be determined from the provided evidence

Format your response as follows:
CLAIM COMPONENTS:
- [List key components]

EVIDENCE ANALYSIS:
- Component 1: [Analysis with direct quotes from sources]
- Component 2: [Analysis with direct quotes from sources]
...

MISSING INFORMATION:
- [List any info gaps]

VERDICT: [Your verdict]

EXPLANATION:
[Brief explanation of verdict]
"""

summary_prompt_template = """Based on the following fact-check analysis:

{analysis}

Generate a concise summary of the fact-check that explains:
1. What was claimed
2. What the evidence shows
3. The final verdict and why

Keep your summary under 200 words and make it accessible to general audiences.
"""

def generate_search_queries(claim):
    """Generate search queries for a given claim."""
    prompt = format_prompt(retrieval_prompt_template, claim=claim)
    result = ollama_client.generate(prompt, temperature=0.3)
    st.session_state.tokens_used += ollama_client.tokens_used
    return result

def retrieve_documents(claim, k=3, lambda_param=0.5):
    """Retrieve relevant documents from ChromaDB using LlamaIndex MMR."""
    if not chroma_manager:
        st.error("❌ ChromaDB n'est pas initialisé")
        return []
    
    # Vérifier si la collection contient des documents
    collection_info = chroma_manager.get_collection_info()
    if collection_info.get('document_count', 0) == 0:
        st.error("❌ Aucun document dans la base vectorielle. Veuillez d'abord indexer vos documents.")
        return []
    
    # Générer les requêtes de recherche
    queries_text = generate_search_queries(claim)
    queries = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-)\s*(.+?)(?=\n|$)', queries_text)
    if not queries:
        queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
    if not queries:
        queries = [claim]
    
    # Utiliser la première requête pour la recherche
    query_for_embedding = queries[0]
    
    # Utiliser LlamaIndex MMR search
    if isinstance(chroma_manager, LlamaIndexChromaDBManager):
        # Utiliser MMR intégré de LlamaIndex
        retrieved_docs = chroma_manager.search_documents_mmr(
            query_for_embedding, 
            n_results=k, 
            lambda_param=lambda_param
        )
    else:
        # Fallback vers l'ancienne méthode
        retrieved_docs = chroma_manager.search_documents(query_for_embedding, n_results=k*2)
        
        if len(retrieved_docs) > k:
            # Appliquer MMR manuel si nécessaire
            embeddings_model = OllamaEmbeddings()
            doc_embeddings = []
            
            for doc in retrieved_docs:
                doc_embedding = embeddings_model.embed_query(doc['content'])
                doc_embeddings.append(doc_embedding)
            
            query_embedding = embeddings_model.embed_query(query_for_embedding)
            selected_indices = mmr_similarity_search(doc_embeddings, query_embedding, k=k, lambda_param=lambda_param)
            retrieved_docs = [retrieved_docs[i] for i in selected_indices]
        else:
            retrieved_docs = retrieved_docs[:k]
    
    if not retrieved_docs:
        st.warning("Aucun document pertinent trouvé dans la base de données.")
        return []
    
    # Formater les documents pour l'affichage/traitement
    all_docs = []
    doc_sources = {}
    for i, doc in enumerate(retrieved_docs):
        doc_id = str(uuid.uuid4())[:8]
        doc_content = doc['content']
        doc_source = doc['metadata'].get('source', 'Unknown')
        all_docs.append(f"[Document {doc_id}]\n{doc_content}\n")
        doc_sources[doc_id] = {
            'source': doc_source,
            'content': doc_content,
            'query': query_for_embedding,
            'similarity': doc.get('similarity', 0.0),
            'score': doc.get('score', 0.0)
        }
    
    st.session_state.current_sources = doc_sources
    return all_docs

def analyze_claim(claim, retrieved_docs):
    """Analyze the claim using retrieved documents."""
    prompt = format_prompt(analysis_prompt_template, claim=claim, retrieved_docs='\n\n'.join(retrieved_docs))
    result = ollama_client.generate(prompt, temperature=0.2)
    st.session_state.tokens_used += ollama_client.tokens_used
    return result

def generate_summary(analysis):
    """Generate a concise summary of the analysis."""
    prompt = format_prompt(summary_prompt_template, analysis=analysis)
    result = ollama_client.generate(prompt, temperature=0.3)
    st.session_state.tokens_used += ollama_client.tokens_used
    return result

def save_fact_check(claim, analysis, summary, sources):
    """Save the fact check to the history."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Extract verdict from analysis
    verdict = extract_verdict(analysis)
    
    fact_check = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'claim': claim,
        'analysis': analysis,
        'summary': summary,
        'verdict': verdict,
        'sources': sources
    }
    
    st.session_state.history.append(fact_check)
    return fact_check

# Initialize session state
if 'tokens_used' not in st.session_state:
    st.session_state.tokens_used = 0
if 'current_sources' not in st.session_state:
    st.session_state.current_sources = {}
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("📊 RAG-based Explainable Fact-Checker")
st.markdown("""
This tool uses RAG (Retrieval-Augmented Generation) to fact-check claims against a database of reliable sources.
It provides transparency by showing which sources were used and how the verdict was determined.
""")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This fact-checking system:
    - Breaks claims into verifiable components
    - Retrieves relevant information from trusted sources
    - Provides transparent reasoning and source attribution
    - Generates human-readable explanations
    """)
    
    st.header("ChromaDB Management")
    if chroma_manager:
        collection_info = chroma_manager.get_collection_info()
        document_count = collection_info.get('document_count', 0)
        
        if document_count > 0:
            st.success(f"✅ {document_count} documents déjà indexés")
            st.info("Votre base vectorielle est prête à être utilisée !")
            
            # Option pour ajouter plus de documents
            if st.button("📚 Ajouter plus de documents"):
                with st.spinner("Indexation en cours..."):
                    data_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
                    success = chroma_manager.load_and_index_documents(data_dir)
                    if success:
                        st.success("✅ Documents ajoutés avec succès!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Erreur lors de l'indexation")
        else:
            st.warning("⚠️ Aucun document indexé")
            st.info("Vous devez d'abord indexer vos documents PDF")
            
            # Bouton pour indexer des documents
            if st.button("📚 Indexer des documents"):
                with st.spinner("Indexation en cours..."):
                    data_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
                    success = chroma_manager.load_and_index_documents(data_dir)
                    if success:
                        st.success("✅ Documents indexés avec succès!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Erreur lors de l'indexation")
        
        # Bouton pour vider la collection (toujours disponible)
        if st.button("🗑️ Vider la base"):
            chroma_manager.clear_collection()
            st.success("✅ Base vidée!")
            st.experimental_rerun()
    else:
        st.error("❌ ChromaDB non disponible")
    
    st.header("Statistics")
    st.metric("Tokens Used", f"{st.session_state.tokens_used:,}")
    
    st.header("History")
    if st.session_state.history:
        for i, check in enumerate(reversed(st.session_state.history[-5:])):
            with st.expander(f"#{len(st.session_state.history)-i}: {check['claim'][:50]}..."):
                st.write(f"**Verdict:** {check['verdict']}")
                st.write(f"**Date:** {check['timestamp']}")
                if st.button("Load", key=f"load_{check['id']}"):
                    st.session_state.current_claim = check['claim']
                    st.session_state.current_analysis = check['analysis']
                    st.session_state.current_summary = check['summary']
                    st.session_state.current_sources = check['sources']
                    st.session_state.showing_results = True
                    st.experimental_rerun()

# Main interface
claim = st.text_area("Enter the claim to fact-check:", height=100)

# Search options
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    check_button = st.button("🔍 Fact Check", type="primary")
with col2:
    use_mmr = st.checkbox("Use MMR", value=True, help="Maximum Marginal Relevance for diverse results")
with col3:
    if use_mmr:
        lambda_param = st.slider("MMR λ", 0.0, 1.0, 0.5, 0.1, 
                                help="λ=0: Max diversity, λ=1: Max relevance")
    else:
        lambda_param = 0.5  # Default value
    st.markdown("*This will retrieve relevant documents, analyze the claim, and provide an explanation.*")

# Process the claim when button is clicked
if check_button and claim:
    with st.spinner("Fact checking in progress..."):
        # Store the claim
        st.session_state.current_claim = claim
        
        # Step 1: Retrieve relevant documents
        st.markdown("### 🔎 Retrieving relevant information...")
        if use_mmr:
            st.info(f"🔍 Using MMR with λ={lambda_param}")
        retrieved_docs = retrieve_documents(claim, lambda_param=lambda_param)
        
        # Step 2: Analyze the claim
        st.markdown("### 🧠 Analyzing claim against evidence...")
        analysis = analyze_claim(claim, retrieved_docs)
        st.session_state.current_analysis = analysis
        
        # Step 3: Generate summary
        st.markdown("### 📝 Generating summary...")
        summary = generate_summary(analysis)
        st.session_state.current_summary = summary
        
        # Save the fact check
        save_fact_check(claim, analysis, summary, st.session_state.current_sources)
        
        # Set flag to show results
        st.session_state.showing_results = True
        
        st.experimental_rerun()

# Display results if available
if 'showing_results' in st.session_state and st.session_state.showing_results:
    st.markdown("## Results")
    
    # Extract verdict for styling
    verdict = extract_verdict(st.session_state.current_analysis)
    
    # Style based on verdict
    verdict_colors = {
        "TRUE": "green",
        "MOSTLY TRUE": "lightgreen",
        "MIXED": "yellow",
        "MOSTLY FALSE": "orange",
        "FALSE": "red",
        "UNVERIFIABLE": "gray"
    }
    verdict_color = verdict_colors.get(verdict, "gray")
    
    # Display summary with verdict highlight
    st.markdown(f"""
    <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6;">
        <h3 style="margin-top: 0;">Claim:</h3>
        <p>{st.session_state.current_claim}</p>
        <h3>Verdict: <span style="color:{verdict_color}; font-weight:bold;">{verdict}</span></h3>
        <p>{st.session_state.current_summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for detailed analysis and source tracking
    tab1, tab2 = st.tabs(["📊 Detailed Analysis", "📚 Source Tracking"])
    
    with tab1:
        st.markdown("### Detailed Analysis")
        st.text_area("Full Analysis", st.session_state.current_analysis, height=400)
    
    with tab2:
        st.markdown("### Sources Used")
        
        for doc_id, doc_info in st.session_state.current_sources.items():
            with st.expander(f"Document {doc_id} - {doc_info['source']}"):
                st.markdown(f"**Query used**: {doc_info['query']}")
                st.markdown(f"**Source**: {doc_info['source']}")
                st.markdown(f"**Similarity**: {doc_info['similarity']:.3f}")
                if 'distance' in doc_info:
                    st.markdown(f"**Distance**: {doc_info['distance']:.3f}")
                st.text_area(f"Content", doc_info['content'], height=200)
        
        # Highlight where sources are referenced in analysis
        st.markdown("### Source References in Analysis")
        analysis_with_highlights = st.session_state.current_analysis
        for doc_id in st.session_state.current_sources:
            analysis_with_highlights = analysis_with_highlights.replace(
                f"Document {doc_id}",
                f"<span style='background-color: #fff2cc; padding: 2px 4px; border-radius: 3px;'>Document {doc_id}</span>"
            )
        st.markdown(analysis_with_highlights, unsafe_allow_html=True)
    
    # Reset button
    if st.button("New Fact Check"):
        st.session_state.showing_results = False
        st.experimental_rerun()
