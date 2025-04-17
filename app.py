import os
import streamlit as st
import pinecone
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.callbacks import get_openai_callback
import json
import uuid
from datetime import datetime
import pandas as pd

# Initialize environment variables
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_ENV = st.secrets["PINECONE_ENV"]
INDEX_NAME = st.secrets["PINECONE_INDEX_NAME"]

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_existing_index(INDEX_NAME, embeddings)

# Define prompts
retrieval_prompt = PromptTemplate(
    input_variables=["claim"],
    template="""I need to fact check the following claim:

Claim: {claim}

What specific keywords or search queries should I use to find reliable information related to this claim?
Please provide 3-5 different search queries that would help gather relevant evidence.
"""
)

analysis_prompt = PromptTemplate(
    input_variables=["claim", "retrieved_docs"],
    template="""You are an objective fact-checker. Your job is to verify the following claim using ONLY the provided evidence.

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
)

summary_prompt = PromptTemplate(
    input_variables=["analysis"],
    template="""Based on the following fact-check analysis:

{analysis}

Generate a concise summary of the fact-check that explains:
1. What was claimed
2. What the evidence shows
3. The final verdict and why

Keep your summary under 200 words and make it accessible to general audiences.
"""
)

# Initialize LLM and chains
llm = OpenAI(temperature=0, model_name="gpt-4")
retrieval_chain = LLMChain(llm=llm, prompt=retrieval_prompt)
analysis_chain = LLMChain(llm=llm, prompt=analysis_prompt)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

def generate_search_queries(claim):
    """Generate search queries for a given claim."""
    with get_openai_callback() as cb:
        result = retrieval_chain.run(claim=claim)
        st.session_state.tokens_used += cb.total_tokens
    return result

def retrieve_documents(claim):
    """Retrieve relevant documents from vector store."""
    # First generate search queries
    queries_text = generate_search_queries(claim)
    
    # Extract the queries (assuming they're listed with numbers, bullets, or lines)
    import re
    queries = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-)\s*(.+?)(?=\n|$)', queries_text)
    
    # If no structured queries found, try to split by newlines
    if not queries:
        queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
    
    # If still empty, use the original claim as fallback
    if not queries:
        queries = [claim]
    
    # Keep track of all retrieved documents
    all_docs = []
    doc_sources = {}
    
    # Retrieve documents for each query
    for query in queries[:3]:  # Limit to first 3 queries to control costs
        docs = vectorstore.similarity_search(query, k=3)
        
        for doc in docs:
            doc_id = str(uuid.uuid4())[:8]
            doc_content = doc.page_content
            doc_source = doc.metadata.get('source', 'Unknown')
            
            all_docs.append(f"[Document {doc_id}]\n{doc_content}\n")
            doc_sources[doc_id] = {
                'source': doc_source,
                'content': doc_content,
                'query': query
            }
    
    st.session_state.current_sources = doc_sources
    return all_docs

def analyze_claim(claim, retrieved_docs):
    """Analyze the claim using retrieved documents."""
    with get_openai_callback() as cb:
        result = analysis_chain.run(claim=claim, retrieved_docs='\n\n'.join(retrieved_docs))
        st.session_state.tokens_used += cb.total_tokens
    return result

def generate_summary(analysis):
    """Generate a concise summary of the analysis."""
    with get_openai_callback() as cb:
        result = summary_chain.run(analysis=analysis)
        st.session_state.tokens_used += cb.total_tokens
    return result

def save_fact_check(claim, analysis, summary, sources):
    """Save the fact check to the history."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Extract verdict from analysis
    import re
    verdict_match = re.search(r'VERDICT:\s*(\w+)', analysis)
    verdict = verdict_match.group(1) if verdict_match else "UNKNOWN"
    
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

# Streamlit UI
st.set_page_config(
    page_title="RAG-based Explainable Fact-Checker",
    page_icon="🔍",
    layout="wide"
)

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

col1, col2 = st.columns([1, 3])
with col1:
    check_button = st.button("🔍 Fact Check", type="primary")
with col2:
    st.markdown("*This will retrieve relevant documents, analyze the claim, and provide an explanation.*")

# Process the claim when button is clicked
if check_button and claim:
    with st.spinner("Fact checking in progress..."):
        # Store the claim
        st.session_state.current_claim = claim
        
        # Step 1: Retrieve relevant documents
        st.markdown("### 🔎 Retrieving relevant information...")
        retrieved_docs = retrieve_documents(claim)
        
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
    import re
    verdict_match = re.search(r'VERDICT:\s*(\w+)', st.session_state.current_analysis)
    verdict = verdict_match.group(1) if verdict_match else "UNKNOWN"
    
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
