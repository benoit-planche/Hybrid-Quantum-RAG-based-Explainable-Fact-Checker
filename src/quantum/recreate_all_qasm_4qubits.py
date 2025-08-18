#!/usr/bin/env python3
"""
Recréer tous les circuits QASM avec encodage 4 qubits
"""

import sys
import os
sys.path.append('../../system')
sys.path.append('src/quantum')

import numpy as np
from sklearn.decomposition import PCA
from cassandra_manager import CassandraVectorStoreManager
from quantum_encoder_4qubits import encode_and_save_embedding_amplitude_4qubits, create_qasm_directory_4qubits

def recreate_all_qasm_4qubits():
    """Recréer tous les circuits QASM avec encodage 4 qubits"""
    
    print("🔬 Recréation de tous les circuits QASM avec 4 qubits")
    print("=" * 60)
    
    # Connexion à Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Récupération de tous les chunks
    chunks = cassandra_manager.get_all_chunks_with_embeddings()
    print(f"📈 {len(chunks)} chunks récupérés depuis Cassandra")
    
    if len(chunks) == 0:
        print("❌ Aucun chunk trouvé dans Cassandra")
        return
    
    # Créer le répertoire pour les circuits QASM
    qasm_dir = create_qasm_directory_4qubits()
    
    # Initialiser PCA pour réduire à 4 dimensions
    print("🔧 Initialisation PCA pour 4 dimensions...")
    all_embeddings = []
    for chunk in chunks:
        if chunk.get('embedding') is not None:
            all_embeddings.append(chunk['embedding'])
    
    if len(all_embeddings) == 0:
        print("❌ Aucun embedding trouvé")
        return
    
    # Ajuster PCA sur tous les embeddings
    pca = PCA(n_components=4)
    pca.fit(all_embeddings)
    print(f"✅ PCA ajusté sur {len(all_embeddings)} embeddings")
    
    # Compteurs
    circuits_crees = 0
    erreurs = 0
    
    print("\n🔄 Création des circuits QASM...")
    
    for i, chunk in enumerate(chunks):
        if i % 100 == 0:
            print(f"   Progression: {i}/{len(chunks)} chunks traités")
        
        try:
            if chunk.get('embedding') is not None:
                # Réduction PCA (garder 4 dimensions au lieu de 8)
                reduced_vector = pca.transform([chunk['embedding']])[0]
                
                # Encodage quantique 4 qubits et sauvegarde
                qasm_path = encode_and_save_embedding_amplitude_4qubits(reduced_vector, chunk['id'], qasm_dir)
                circuits_crees += 1
                
                if circuits_crees % 50 == 0:
                    print(f"   ✅ {circuits_crees} circuits créés")
                    
        except Exception as e:
            print(f"   ❌ Erreur pour chunk {chunk.get('id', 'unknown')}: {e}")
            erreurs += 1
    
    print("\n📊 Résumé de la création des circuits")
    print("-" * 40)
    print(f"📈 Chunks traités: {len(chunks)}")
    print(f"✅ Circuits créés: {circuits_crees}")
    print(f"❌ Erreurs: {erreurs}")
    print(f"📁 Répertoire: {qasm_dir}")
    
    if circuits_crees > 0:
        print(f"🎯 Taux de succès: {(circuits_crees / len(chunks)) * 100:.1f}%")
        print("✅ Recréation des circuits QASM 4 qubits terminée avec succès!")
    else:
        print("❌ Aucun circuit n'a été créé")

if __name__ == "__main__":
    recreate_all_qasm_4qubits()
