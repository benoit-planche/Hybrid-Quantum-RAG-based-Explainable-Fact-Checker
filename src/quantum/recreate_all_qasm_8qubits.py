#!/usr/bin/env python3
"""
Script pour recréer tous les circuits QASM avec 8 qubits pour améliorer les performances
"""

import sys
import os
sys.path.append('system')
sys.path.append('src/quantum')

import pickle
import numpy as np
from cassandra_manager import CassandraVectorStoreManager
from quantum_encoder_8qubits import encode_and_save_embedding_amplitude_8qubits

def recreate_all_qasm_8qubits():
    """Recrée tous les circuits QASM avec 8 qubits pour améliorer les performances"""
    
    print("🚀 Recréation de tous les circuits QASM avec 8 qubits...")
    
    # Connexion à Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Chargement du modèle PCA existant
    pca_path = "src/quantum/pca_model.pkl"
    with open(pca_path, 'rb') as f:
        pca = pickle.load(f)
    
    print(f"📊 Modèle PCA chargé: {pca.n_components_} dimensions")
    
    # Récupération de tous les chunks
    chunks = cassandra_manager.get_all_chunks_with_embeddings()
    print(f"📈 {len(chunks)} chunks récupérés depuis Cassandra")
    
    # Dossier pour les circuits 8 qubits
    qasm_dir = "src/quantum/quantum_db_8qubits"
    os.makedirs(qasm_dir, exist_ok=True)
    
    # Suppression des anciens circuits QASM 8 qubits
    print("🗑️ Suppression des anciens circuits QASM 8 qubits...")
    old_files = [f for f in os.listdir(qasm_dir) if f.endswith('.qasm')]
    for file in old_files:
        os.remove(os.path.join(qasm_dir, file))
    
    # Recréation des circuits QASM avec 8 qubits
    print("🔧 Recréation des circuits QASM 8 qubits...")
    created_count = 0
    
    for i, chunk in enumerate(chunks):
        try:
            if chunk.get('embedding') is not None:
                # Réduction PCA (garder 8 dimensions au lieu de 16)
                reduced_vector = pca.transform([chunk['embedding']])[0]
                
                # Encodage quantique 8 qubits et sauvegarde
                qasm_path = encode_and_save_embedding_amplitude_8qubits(reduced_vector, chunk['id'], qasm_dir)
                
                created_count += 1
                
                if created_count % 100 == 0:
                    print(f"   {created_count} circuits créés...")
                    
        except Exception as e:
            print(f"❌ Erreur pour chunk {chunk.get('row_id', 'unknown')}: {e}")
    
    print(f"✅ {created_count} circuits QASM 8 qubits créés")
    
    # Vérification
    qasm_files = [f for f in os.listdir(qasm_dir) if f.endswith('.qasm')]
    print(f"📁 {len(qasm_files)} fichiers QASM dans le dossier")
    
    if len(qasm_files) == len(chunks):
        print("✅ Synchronisation parfaite entre Cassandra et QASM 8 qubits!")
    else:
        print(f"⚠️ Désynchronisation: {len(chunks)} chunks vs {len(qasm_files)} QASM")
    
    # Statistiques de performance
    print("\n📊 Amélioration des performances:")
    print(f"   Ancien: 16 qubits = 2^16 = 65,536 amplitudes")
    print(f"   Nouveau: 8 qubits = 2^8 = 256 amplitudes")
    print(f"   Gain théorique: ~256x plus rapide")
    print(f"   Mémoire: ~256x moins de mémoire")

if __name__ == "__main__":
    recreate_all_qasm_8qubits()
