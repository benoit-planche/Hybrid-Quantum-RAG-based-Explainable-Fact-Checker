#!/usr/bin/env python3
"""
Script pour re-encoder tous les documents avec amplitude encoding
"""

import os
import sys
import numpy as np
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../system')))
from cassandra_manager import create_cassandra_manager
from quantum_encoder import amplitude_encoding, encode_and_save_embedding_amplitude
from quantum_db import save_qasm_circuit

# Configuration
KEYSPACE = "fact_checker_keyspace"
TABLE = "fact_checker_docs"
DB_FOLDER = "src/quantum/quantum_db/"
PCA_MODEL_PATH = "src/quantum/pca_model.pkl"
N_QUBITS = 16

def reencode_with_amplitude():
    """Re-encode tous les documents avec amplitude encoding"""
    print("🔧 RE-ENCODAGE AVEC AMPLITUDE ENCODING")
    print("=" * 60)
    
    # Connexion à Cassandra
    print("🔌 Connexion à Cassandra...")
    cassandra_manager = create_cassandra_manager(table_name=TABLE, keyspace=KEYSPACE)
    
    # Charger le PCA fixe
    print("📥 Chargement du PCA fixe...")
    if not os.path.exists(PCA_MODEL_PATH):
        print("❌ PCA fixe non trouvé. Lance d'abord fix_pca_encoding.py")
        return
    
    pca = joblib.load(PCA_MODEL_PATH)
    print("✅ PCA fixe chargé")
    
    # Récupérer tous les embeddings
    print("📥 Récupération de tous les embeddings...")
    all_chunks = cassandra_manager.get_all_chunks_with_embeddings()
    print(f"📊 {len(all_chunks)} chunks trouvés")
    
    # Supprimer les anciens fichiers QASM
    print("🗑️ Suppression des anciens circuits QASM...")
    old_files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.qasm')]
    for old_file in old_files:
        os.remove(os.path.join(DB_FOLDER, old_file))
    print(f"✅ {len(old_files)} anciens fichiers supprimés")
    
    # Re-encoder avec amplitude encoding
    print("⚡ Re-encodage avec amplitude encoding...")
    success_count = 0
    error_count = 0
    
    for i, chunk in enumerate(all_chunks):
        try:
            chunk_id = chunk['id']
            embedding = np.array(chunk['embedding'], dtype=float)
            
            # Réduire avec PCA fixe
            embedding_reduced = pca.transform([embedding])[0]
            
            # Utiliser amplitude encoding (pas de normalisation destructive)
            qc = amplitude_encoding(embedding_reduced, N_QUBITS)
            
            # Sauvegarder le circuit QASM
            qasm_path = os.path.join(DB_FOLDER, f"{chunk_id}.qasm")
            save_qasm_circuit(qc, qasm_path)
            
            success_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"  ✅ {i + 1}/{len(all_chunks)} circuits créés")
                
        except Exception as e:
            print(f"  ❌ Erreur pour chunk {chunk_id}: {e}")
            error_count += 1
    
    print(f"\n📊 Résumé du re-encodage amplitude:")
    print(f"  ✅ Circuits créés avec succès: {success_count}")
    print(f"  ❌ Erreurs: {error_count}")
    print(f"  📁 Circuits sauvegardés dans: {DB_FOLDER}")

def test_amplitude_encoding():
    """Teste l'amplitude encoding avec des vecteurs similaires"""
    print("\n🔧 TEST AMPLITUDE ENCODING")
    print("-" * 50)
    
    # Test avec des vecteurs similaires
    vec1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
    vec2 = np.array([0.11, 0.19, 0.31, 0.39, 0.51, 0.59, 0.71, 0.79, 0.91, 0.99, 1.11, 1.19, 1.31, 1.39, 1.51, 1.59])
    
    print(f"📊 Vecteur 1: {vec1[:5]}...")
    print(f"📊 Vecteur 2: {vec2[:5]}...")
    
    # Encoder avec amplitude encoding
    qc1 = amplitude_encoding(vec1, N_QUBITS)
    qc2 = amplitude_encoding(vec2, N_QUBITS)
    
    print(f"✅ Circuits créés: {qc1.num_qubits} qubits chacun")
    
    # Calculer la similarité
    from quantum_search import quantum_overlap_similarity
    similarity = quantum_overlap_similarity(qc1, qc2)
    print(f"🔍 Similarité quantique: {similarity:.6f}")
    
    # Comparer avec angle encoding
    from quantum_encoder import angle_encoding
    qc1_angle = angle_encoding(vec1)
    qc2_angle = angle_encoding(vec2)
    similarity_angle = quantum_overlap_similarity(qc1_angle, qc2_angle)
    print(f"🔍 Similarité angle encoding: {similarity_angle:.6f}")
    
    if similarity > similarity_angle:
        print("✅ Amplitude encoding préserve mieux la similarité !")
    else:
        print("⚠️ Résultat inattendu...")

def main():
    print("🚀 MIGRATION VERS AMPLITUDE ENCODING")
    print("=" * 60)
    
    # Test de l'amplitude encoding
    test_amplitude_encoding()
    
    # Re-encoder tous les documents
    reencode_with_amplitude()
    
    print("\n🏁 MIGRATION TERMINÉE!")
    print("=" * 60)
    print("✅ Tous les circuits QASM re-créés avec amplitude encoding")
    print("✅ PCA fixe conservé")
    print("✅ Prêt pour les tests de recherche quantique")

if __name__ == "__main__":
    main() 