import streamlit as st
import os
import sys
from quantum_search import retrieve_top_k

# Rendre le dossier system accessible pour ollama_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../system')))
from ollama_utils import OllamaClient, format_prompt
from cassandra_manager import create_cassandra_manager
from performance_metrics import (
    start_performance_session, 
    get_performance_summary, 
    save_performance_metrics,
    time_operation_context,
    log_llm_operation,
    log_database_operation
)

st.set_page_config(page_title="Quantum RAG Fact-Checker", layout="wide")
st.title("🔬 Quantum RAG Fact-Checker")

st.header("Recherche documentaire quantique (overlap)")
db_folder = st.text_input("Dossier des circuits QASM", value="src/quantum/quantum_db/")
pdf_folder = st.text_input("Dossier PDF original", value="/home/moi/Documents/internship/climat-misinformation-detection/rapport")
n_qubits =8  # Fixé à 8 pour correspondre à l'encodage PCA

query = st.text_area("Entrez votre requête :", height=80)

# Connexion Cassandra pour retrouver le texte des chunks et le PDF d'origine
def get_chunk_info(chunk_id, cassandra_manager):
    import time
    start_time = time.time()
    partition_id, row_id = chunk_id.split('_', 1)
    query = f"SELECT body_blob, metadata_s FROM {cassandra_manager.keyspace}.{cassandra_manager.table_name} WHERE partition_id=%s AND row_id=%s;"
    row = cassandra_manager.session.execute(query, (partition_id, row_id)).one()
    chunk_text = row.body_blob if row and row.body_blob else "[Texte non trouvé pour ce chunk]"
    pdf_name = row.metadata_s['source'] if row and row.metadata_s and 'source' in row.metadata_s else "[PDF d'origine inconnu]"
    duration = time.time() - start_time
    log_database_operation("chunk_retrieval", cassandra_manager.table_name, duration)
    return chunk_text, pdf_name

# Template d'analyse amélioré, plus décisif
analysis_prompt_template = """
You are a decisive fact-checker. Your job is to verify the following claim using the provided evidence. 
You MUST take a clear position based on the available evidence.

CLAIM: {claim}

EVIDENCE (from chunks):
{retrieved_docs}

CRITICAL INSTRUCTIONS:
- Be DECISIVE and take a clear position. Do not hedge or be overly cautious.
- If the evidence supports the claim, say TRUE.
- If the evidence contradicts the claim, say FALSE.
- Only say UNVERIFIABLE if there is truly insufficient evidence.
- Look for direct statements that answer the claim.
- Quote specific text from the evidence to support your verdict.

IMPORTANT: The evidence contains scientific information about Antarctica. Look for direct statements about ice loss/gain.

Format your response as follows:
VERDICT: [TRUE/FALSE/UNVERIFIABLE]
EXPLANATION: [Your decisive reasoning with specific quotes from the evidence]
"""

def generate_llm_response(query, chunk_ids, cassandra_manager):
    import time
    start_time = time.time()
    
    with time_operation_context("document_preparation", {"n_chunks": len(chunk_ids)}):
        docs = []
        for chunk_id in chunk_ids:
            chunk_text, pdf_name = get_chunk_info(chunk_id, cassandra_manager)
            # Prendre plus de contexte pour une meilleure analyse
            excerpt = chunk_text[:1500] + ("..." if len(chunk_text) > 1500 else "")
            docs.append(f"[Source PDF: {pdf_name}]\n[Chunk ID: {chunk_id}]\n{excerpt}")
        retrieved_docs = "\n\n".join(docs)
    
    with time_operation_context("prompt_formatting"):
        prompt = format_prompt(analysis_prompt_template, claim=query, retrieved_docs=retrieved_docs)
    
    with time_operation_context("llm_generation"):
        ollama_client = OllamaClient()
        # Température plus basse pour des réponses plus décisives
        response = ollama_client.generate(prompt, temperature=0.05)
    
    total_duration = time.time() - start_time
    log_llm_operation("fact_checking", "ollama", total_duration, len(response.split()))
    
    return prompt, response

if st.button("Rechercher") and query:
    # Démarrer la session de performance
    start_performance_session()
    
    with st.spinner("Recherche quantique en cours..."):
        with time_operation_context("cassandra_connection"):
            cassandra_manager = create_cassandra_manager(table_name="fact_checker_docs", keyspace="fact_checker_keyspace")
        
        with time_operation_context("quantum_search"):
            results = retrieve_top_k(query, db_folder, k=10, n_qubits=n_qubits, cassandra_manager=cassandra_manager)
        
        st.subheader("Top 10 chunks les plus similaires :")
        chunk_ids = []
        with time_operation_context("results_display"):
            for score, qasm_path, chunk_id in results:
                chunk_text, pdf_name = get_chunk_info(chunk_id, cassandra_manager)
                excerpt = chunk_text[:300] + ("..." if len(chunk_text) > 300 else "")
                st.write(f"**{pdf_name}** — Chunk ID: {chunk_id} — Similarité (overlap): {score:.4f}")
                st.write(f"Extrait du chunk : {excerpt}")
                chunk_ids.append(chunk_id)
        
        # Générer la réponse LLM
        st.markdown("---")
        st.subheader("🧠 Prompt envoyé au LLM (debug)")
        prompt, llm_response = generate_llm_response(query, chunk_ids, cassandra_manager)
        st.text_area("Prompt LLM", prompt, height=200)
        st.subheader("🧠 Réponse générée par le LLM")
        st.text_area("Réponse LLM", llm_response, height=400)
        
        # Afficher les métriques de performance
        st.markdown("---")
        st.subheader("📊 Métriques de Performance")
        
        # Obtenir le résumé des performances
        performance_summary = get_performance_summary()
        
        if performance_summary:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("⏱️ Temps Total", f"{performance_summary['total_duration']:.2f}s")
                st.metric("📈 Nombre d'Opérations", performance_summary['metrics_count'])
            
            with col2:
                # Trouver l'opération la plus lente
                slowest_op = None
                slowest_time = 0
                for op_name, stats in performance_summary['operations'].items():
                    if stats['total_time'] > slowest_time:
                        slowest_time = stats['total_time']
                        slowest_op = op_name
                
                if slowest_op:
                    st.metric("🐌 Opération la plus lente", slowest_op)
                    st.metric("⏳ Temps de l'opération lente", f"{slowest_time:.2f}s")
            
            # Afficher le détail des opérations
            st.subheader("📋 Détail des Opérations")
            for op_name, stats in performance_summary['operations'].items():
                with st.expander(f"🔍 {op_name} ({stats['count']} exécutions)"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Temps Total", f"{stats['total_time']:.3f}s")
                    with col2:
                        st.metric("Temps Moyen", f"{stats['avg_time']:.3f}s")
                    with col3:
                        st.metric("Temps Min", f"{stats['min_time']:.3f}s")
                    with col4:
                        st.metric("Temps Max", f"{stats['max_time']:.3f}s")
            
            # Bouton pour sauvegarder les métriques
            if st.button("💾 Sauvegarder les Métriques"):
                filename = save_performance_metrics()
                st.success(f"Métriques sauvegardées dans {filename}")
        else:
            st.warning("Aucune métrique de performance disponible") 