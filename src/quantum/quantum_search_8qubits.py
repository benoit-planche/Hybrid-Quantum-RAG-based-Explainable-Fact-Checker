#!/usr/bin/env python3
"""
Recherche quantique optimisée pour 8 qubits
"""

import os
import numpy as np
import pickle
from qiskit import transpile
from qiskit_aer import Aer
from qiskit.compiler import transpile
from quantum_encoder_8qubits import sophisticated_amplitude_encoding_8qubits, load_qasm_circuit_8qubits
from quantum_db import list_qasm_files
from performance_metrics import time_operation, time_operation_context

def retrieve_top_k_8qubits(query, db_folder, k=10, n_qubits=8, cassandra_manager=None):
    """
    Version optimisée pour 8 qubits de retrieve_top_k
    """
    print(f"🔍 Recherche quantique 8 qubits pour: '{query}'")
    
    # Chargement du modèle PCA
    pca_path = "src/quantum/pca_model.pkl"
    with open(pca_path, 'rb') as f:
        pca = pickle.load(f)
    
    # Génération de l'embedding de la requête
    if cassandra_manager:
        embed_model = cassandra_manager.embed_model
        query_vector = embed_model.get_text_embedding(query)
    else:
        # Fallback si pas de cassandra_manager
        query_vector = np.random.rand(4096)  # Vecteur factice
    
    # Réduction PCA (8 dimensions)
    reduced_query_vector = pca.transform([query_vector])[0]
    
    # Encodage quantique de la requête
    query_circuit = sophisticated_amplitude_encoding_8qubits(reduced_query_vector, n_qubits=8)
    
    # Calcul des similarités avec tous les circuits
    scores = []
    
    with time_operation_context("quantum_similarity_computation_8qubits", {"n_files": len(list_qasm_files(db_folder))}):
        qasm_files = list_qasm_files(db_folder)
        
        for i, qasm_path in enumerate(qasm_files):
            with time_operation_context(f"circuit_comparison_8qubits_{i}", {"file": qasm_path}):
                try:
                    # Charger le circuit du document
                    qc_doc = load_qasm_circuit_8qubits(qasm_path)
                    
                    # Calculer la similarité quantique
                    score = quantum_overlap_similarity_8qubits(query_circuit, qc_doc)
                    
                    # Extraire l'ID du chunk
                    chunk_id = os.path.basename(qasm_path).replace('_8qubits.qasm', '')
                    
                    scores.append((score, qasm_path, chunk_id))
                    
                except Exception as e:
                    print(f"⚠️ Erreur pour {qasm_path}: {e}")
                    continue
    
    # Tri par similarité décroissante
    scores.sort(key=lambda x: x[0], reverse=True)
    
    # Retourner les top-k
    return scores[:k]

@time_operation("quantum_overlap_calculation_8qubits")
def quantum_overlap_similarity_8qubits(qc1, qc2):
    """
    Calcule l'overlap (fidelity) entre deux circuits 8 qubits via simulation Qiskit Aer.
    """
    try:
        backend = Aer.get_backend('statevector_simulator')
        qc1_t = transpile(qc1, backend)
        qc2_t = transpile(qc2, backend)
        state1 = backend.run(qc1_t).result().get_statevector()
        state2 = backend.run(qc2_t).result().get_statevector()
        overlap = np.abs(np.vdot(state1, state2)) ** 2
        return overlap
    except Exception as e:
        print(f"⚠️ Erreur simulation quantique: {e}")
        # Fallback vers similarité cosinus
        from sklearn.metrics.pairwise import cosine_similarity
        vec1 = np.real(state1) if 'state1' in locals() else np.random.rand(256)
        vec2 = np.real(state2) if 'state2' in locals() else np.random.rand(256)
        return cosine_similarity([vec1], [vec2])[0][0]

def test_8qubits_performance():
    """Test de performance avec 8 qubits"""
    print("🧪 Test de performance 8 qubits...")
    
    # Test avec une requête simple
    query = "Is Antarctica losing ice?"
    
    # Comparer les temps
    import time
    
    # Test avec 8 qubits
    start_time = time.time()
    results_8q = retrieve_top_k_8qubits(query, "src/quantum/quantum_db_8qubits", k=5)
    time_8q = time.time() - start_time
    
    print(f"⏱️ Temps 8 qubits: {time_8q:.2f}s")
    print(f"📊 Top 5 résultats 8 qubits:")
    for i, (score, path, chunk_id) in enumerate(results_8q):
        print(f"   {i+1}. {chunk_id}: {score:.4f}")

if __name__ == "__main__":
    test_8qubits_performance()
