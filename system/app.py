import streamlit as st
import uuid
from datetime import datetime
import re
from ollama_utils import OllamaClient, format_prompt, extract_verdict
from dotenv import load_dotenv
from cassandra_manager import create_cassandra_manager

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

# Initialize Cassandra Vector Store with MMR
try:
    # Use Cassandra Vector Store manager with MMR support
    cassandra_manager = create_cassandra_manager(
        table_name="fact_checker_docs"
    )
    st.success("✅ Cassandra Vector Store avec MMR initialisé avec succès")
    
    # Afficher les informations de la table
    collection_info = cassandra_manager.get_collection_info()
    if collection_info:
        st.info(f"📊 Table: {collection_info.get('table_name', 'Unknown')}")
        st.info(f"🤖 Modèle d'embedding: {cassandra_manager.embedding_model}")
    
except Exception as e:
    st.error(f"❌ Erreur d'initialisation Cassandra Vector Store: {e}")
    cassandra_manager = None

# Define prompts as templates
retrieval_prompt_template = """I need to fact check the following claim:

Claim: {claim}

Generate 3-5 specific and targeted search queries to find reliable scientific evidence that can definitively verify or refute this claim. 

CRITICAL: Focus on the EXACT TIME PERIODS and SPECIFIC FACTS mentioned in the claim:
- If the claim mentions a specific year (like 1998), include that year in queries
- If the claim mentions a specific phenomenon, search for that exact phenomenon
- Create queries that directly test the specific claim made
- Include both supporting and contradicting evidence searches

For example, if the claim is "Did global warming stop in 1998?", create queries like:
- "global warming temperature trend 1998"
- "global temperature data after 1998"
- "climate change hiatus 1998"
- "temperature records 1998 present"

If the claim is about "solar cycles and warming", create queries like:
- "solar cycles global temperature correlation"
- "solar activity climate change evidence"
- "sunspot cycles warming trend"

Make the queries precise and directly test the specific claim made.
"""

analysis_prompt_template = """You are a decisive fact-checker. Your job is to verify the following claim using IN PRIORITY the provided evidence. You must take a clear position based on the available evidence.

Claim: {claim}

Evidence:
{retrieved_docs}

IMPORTANT: You must be decisive and take a clear position. Do not hedge or be overly cautious. If the evidence supports the claim, say so. If it contradicts the claim, say so. If there's insufficient evidence, state that clearly.

CRITICAL VALIDATION: First, assess if the retrieved evidence actually addresses the specific claim made. Ask yourself:
- Does the evidence contain data about the specific time period mentioned in the claim?
- Does the evidence address the exact phenomenon described in the claim?
- If the claim mentions "1998", does the evidence contain data from 1998 or after?
- If the claim asks about "global warming stopping", does the evidence contain temperature data?

If the evidence is NOT relevant to the specific claim, you MUST give a FALSE verdict and explain why the evidence is insufficient.

Please analyze the claim step by step:
1. Break down the claim into its key components
2. For each component, identify supporting or contradicting evidence from the provided sources
3. Note any missing information that would be needed for a complete verification
4. Assign a verdict to the claim from the following options:
   - TRUE: The claim is supported by the evidence
   - FALSE: The claim is contradicted by the evidence or insufficient evidence

IMPORTANT: Choose the verdict that best reflects the overall truth of the claim based on the available evidence. Be decisive. If it's unclear or insufficient evidence, say FALSE.

Format your response as follows:
CLAIM COMPONENTS:
- [List key components]

EVIDENCE ANALYSIS:
- Component 1: [Analysis with direct quotes from sources]
- Component 2: [Analysis with direct quotes from sources]
...

MISSING INFORMATION:
- [List any info gaps]

VERDICT: [Your decisive verdict - TRUE or FALSE only]

EXPLANATION:
[Clear explanation of why you chose this verdict]
"""

summary_prompt_template = """Based on the following fact-check analysis:

{analysis}

Generate a clear and decisive summary that:
1. States what was claimed
2. Explains what the evidence definitively shows
3. Gives a clear verdict with strong reasoning

Be direct and confident in your assessment. If the evidence supports the claim, say so clearly. If it contradicts the claim, state this definitively. If there's insufficient evidence, explain why the claim cannot be verified.

Keep your summary under 200 words and make it accessible to general audiences.
"""

def generate_search_queries(claim):
    """Generate search queries for a given claim."""
    prompt = format_prompt(retrieval_prompt_template, claim=claim)
    result = ollama_client.generate(prompt, temperature=0.5)
    st.session_state.tokens_used += ollama_client.tokens_used
    return result

def retrieve_documents(claim, k=5, lambda_param=0.5):
    """Retrieve relevant documents from Cassandra Vector Store using MMR."""
    if not cassandra_manager:
        st.error("❌ Cassandra Vector Store n'est pas initialisé")
        return []
    
    # Vérifier si l'index contient des documents
    collection_info = cassandra_manager.get_collection_info()
    if not collection_info.get('index_loaded', False):
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
    
    # Afficher les requêtes générées pour la transparence
    st.info(f"🔍 Requêtes de recherche générées: {', '.join(queries[:3])}")
    
    # Utiliser Cassandra MMR search
    retrieved_docs = cassandra_manager.search_documents_mmr(
        query_for_embedding, 
        n_results=k, 
        lambda_param=lambda_param
    )
    
    if not retrieved_docs:
        st.warning("Aucun document pertinent trouvé dans la base de données.")
        return []
    
    # Afficher le nombre de documents récupérés
    st.info(f"📊 Documents récupérés: {len(retrieved_docs)}")
    
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
    result = ollama_client.generate(prompt, temperature=0.1)  # Lower temperature for more decisive responses
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
    
    st.header("Cassandra Vector Store Management")
    if cassandra_manager:
        collection_info = cassandra_manager.get_collection_info()
        index_loaded = collection_info.get('index_loaded', False)
        
        if index_loaded:
            st.success(f"✅ Documents déjà indexés dans Cassandra")
            st.info("Votre base vectorielle est prête à être utilisée !")
            
            # Option pour ajouter plus de documents
            if st.button("📚 Ajouter plus de documents"):
                with st.spinner("Indexation en cours..."):
                    data_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
                    success = cassandra_manager.load_and_index_documents(data_dir)
                    if success:
                        st.success("✅ Documents ajoutés avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de l'indexation")
        else:
            st.warning("⚠️ Aucun document indexé")
            st.info("Vous devez d'abord indexer vos documents PDF")
            
            # Bouton pour indexer des documents
            if st.button("📚 Indexer des documents"):
                with st.spinner("Indexation en cours..."):
                    data_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
                    success = cassandra_manager.load_and_index_documents(data_dir)
                    if success:
                        st.success("✅ Documents indexés avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de l'indexation")
        
        # Bouton pour vider la collection (toujours disponible)
        if st.button("🗑️ Vider la base"):
            cassandra_manager.clear_collection()
            st.success("✅ Base vidée!")
            st.rerun()
    else:
        st.error("❌ Cassandra Vector Store non disponible")
    
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
                    st.rerun()

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
        
        st.rerun()

# Display results if available
if 'showing_results' in st.session_state and st.session_state.showing_results:
    st.markdown("## Results")
    
    # Extract verdict for styling
    verdict = extract_verdict(st.session_state.current_analysis)
    
    # Style based on verdict
    verdict_colors = {
        "TRUE EXPLANATION": "green",
        "MOSTLY TRUE": "lightgreen",
        "MOSTLY FALSE": "orange",
        "FALSE EXPLANATION": "red",
        "UNVERIFIABLE": "gray"
    }
    verdict_color = verdict_colors.get(verdict, "black")
    
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
        st.rerun()
