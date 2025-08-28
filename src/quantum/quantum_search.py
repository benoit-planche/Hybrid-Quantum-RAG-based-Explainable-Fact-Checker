import os
import numpy as np
from qiskit_aer import Aer
from qiskit import transpile
from quantum_encoder import text_to_vector, angle_encoding, amplitude_encoding
from quantum_db import list_qasm_files, load_qasm_circuit
from performance_metrics import time_operation, time_operation_context, log_quantum_operation

@time_operation("quantum_overlap_calculation")
def quantum_overlap_similarity(qc1, qc2):
    """Calcule l'overlap (fidelity) entre deux circuits via simulation Qiskit Aer."""
    try:
        backend = Aer.get_backend('statevector_simulator')
        qc1_t = transpile(qc1, backend)
        qc2_t = transpile(qc2, backend)
        state1 = backend.run(qc1_t).result().get_statevector()
        state2 = backend.run(qc2_t).result().get_statevector()
        
        # Calculer la fidélité (overlap) entre les deux états quantiques
        # La fidélité est |<ψ1|ψ2>|²
        overlap = np.abs(np.vdot(state1, state2)) ** 2
        
        # Amélioration: Appliquer une transformation non-linéaire pour mieux différencier
        # Cela permet d'avoir une meilleure séparation entre les similarités
        if overlap > 0.9:
            # Pour les très hautes similarités, appliquer une compression
            overlap = 0.9 + 0.1 * (overlap - 0.9) ** 2
        elif overlap < 0.1:
            # Pour les très basses similarités, appliquer une expansion
            overlap = overlap ** 0.5
        
        return overlap
    except Exception as e:
        print(f"⚠️ Erreur dans quantum_overlap_similarity: {e}")
        print(f"   Circuit 1: {qc1.name if hasattr(qc1, 'name') else 'Unknown'}")
        print(f"   Circuit 2: {qc2.name if hasattr(qc2, 'name') else 'Unknown'}")
        print(f"   Circuit 1 num_qubits: {qc1.num_qubits if hasattr(qc1, 'num_qubits') else 'Unknown'}")
        print(f"   Circuit 2 num_qubits: {qc2.num_qubits if hasattr(qc2, 'num_qubits') else 'Unknown'}")
        # Fallback vers une similarité basique
        return 0.5

@time_operation("retrieve_top_k_search")
def retrieve_top_k(query_text, db_folder, k=5, n_qubits=16, cassandra_manager=None):
    """
    Encode la requête avec embedding sémantique + PCA fixe + amplitude encoding, 
    charge tous les circuits QASM, calcule l'overlap, retourne les top-k chunks.
    """
    with time_operation_context("query_encoding", {"n_qubits": n_qubits, "query_length": len(query_text)}):
        if cassandra_manager is None:
            print("⚠️ Aucun cassandra_manager fourni, utilisation de l'encodage texte simple")
            # Fallback vers l'ancienne méthode
            vec = text_to_vector(query_text, n_qubits)
            qc_query = angle_encoding(vec)
        else:
            # Utiliser l'embedding sémantique + PCA fixe + amplitude encoding
            print("🔄 Génération de l'embedding sémantique pour la requête...")
            with time_operation_context("semantic_embedding_generation"):
                query_embedding = cassandra_manager.embed_model.get_text_embedding_batch([query_text])[0]
            
            # Charger le PCA fixe sauvegardé
            with time_operation_context("pca_loading"):
                try:
                    import joblib
                    pca_model_path = "src/quantum/pca_model.pkl"
                    if os.path.exists(pca_model_path):
                        pca = joblib.load(pca_model_path)
                        print("✅ PCA fixe chargé depuis le fichier")
                    else:
                        print("⚠️ PCA fixe non trouvé, utilisation du PCA dynamique")
                        # Fallback vers l'ancienne méthode
                        all_chunks = cassandra_manager.get_all_chunks_with_embeddings()
                        all_embeddings = [np.array(c['embedding'], dtype=float) for c in all_chunks]
                        from sklearn.decomposition import PCA
                        pca = PCA(n_components=n_qubits)
                        pca.fit(all_embeddings)
                except Exception as e:
                    print(f"❌ Erreur chargement PCA: {e}")
                    # Fallback vers l'ancienne méthode
                    all_chunks = cassandra_manager.get_all_chunks_with_embeddings()
                    all_embeddings = [np.array(c['embedding'], dtype=float) for c in all_chunks]
                    from sklearn.decomposition import PCA
                    pca = PCA(n_components=n_qubits)
                    pca.fit(all_embeddings)
            
            # Réduire l'embedding de la requête avec PCA fixe
            with time_operation_context("pca_transformation"):
                query_emb_reduced = pca.transform([query_embedding])[0]
            
            # Utiliser amplitude encoding (pas de normalisation destructive)
            with time_operation_context("amplitude_encoding"):
                qc_query = amplitude_encoding(query_emb_reduced, n_qubits)
    
    with time_operation_context("quantum_similarity_computation", {"n_files": len(list_qasm_files(db_folder))}):
        qasm_files = list_qasm_files(db_folder)
        scores = []
        for i, qasm_path in enumerate(qasm_files):
            with time_operation_context(f"circuit_comparison_{i}", {"file": qasm_path}):
                qc_doc = load_qasm_circuit(qasm_path)
                score = quantum_overlap_similarity(qc_query, qc_doc)
                # Extraire le chunk_id en gérant les suffixes _8qubits et les préfixes None_
                filename = os.path.basename(qasm_path).replace('.qasm', '')
                if filename.endswith('_8qubits'):
                    filename = filename.replace('_8qubits', '')
                if filename.startswith('None_'):
                    chunk_id = filename.replace('None_', '')  # Enlever le préfixe None_
                else:
                    chunk_id = filename
                scores.append((score, qasm_path, chunk_id))
        
        with time_operation_context("results_sorting"):
            scores.sort(reverse=True, key=lambda x: x[0])
    
    return scores[:k]

# Optionnel : fonction pour retrouver le texte original d'un chunk à partir de son id
# (à implémenter selon la façon dont tu stockes les textes)
def get_chunk_text(chunk_id, cassandra_manager):
    partition_id, row_id = chunk_id.split('_', 1)
    query = f"SELECT body_blob FROM {cassandra_manager.keyspace}.{cassandra_manager.table_name} WHERE partition_id=%s AND row_id=%s;"
    row = cassandra_manager.session.execute(query, (partition_id, row_id)).one()
    if row and row.body_blob:
        return row.body_blob
    return "[Texte non trouvé pour ce chunk]"

# Exemple d'utilisation :
# top_chunks = retrieve_top_k("ma requête", "quantum_db/", k=5, n_qubits=16, cassandra_manager=cassandra_manager)
# for score, path, chunk_id in top_chunks:
#     print(score, chunk_id, path) 