#!/usr/bin/env python3
"""
Script pour recréer tous les circuits QASM après réindexation de Cassandra
"""

import sys
import os
sys.path.append('system')
sys.path.append('src/quantum')

import numpy as np
import pickle
from cassandra_manager import CassandraVectorStoreManager
from quantum_encoder import amplitude_encoding
from quantum_db import save_qasm_circuit
import time

def recreate_all_qasm():
    """Recrée tous les circuits QASM pour tous les chunks dans Cassandra"""
    
    print("🔄 Recréation de tous les circuits QASM...")
    
    # Connexion à Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Chargement du modèle PCA
    pca_path = "src/quantum/pca_model.pkl"
    if not os.path.exists(pca_path):
        print("❌ Modèle PCA non trouvé. Création d'abord...")
        from create_pca_model import create_pca_model
        create_pca_model()
    
    with open(pca_path, 'rb') as f:
        pca = pickle.load(f)
    
    print(f"✅ Modèle PCA chargé: {pca.n_components_} dimensions")
    
    # Récupération de tous les chunks
    print("📊 Récupération des chunks depuis Cassandra...")
    
    session = cassandra_manager.session
    query = "SELECT row_id, vector FROM fact_checker_keyspace.fact_checker_docs"
    rows = session.execute(query)
    
    chunks = []
    for row in rows:
        if row.vector is not None:
            chunks.append({
                'row_id': row.row_id,
                'vector': np.array(row.vector)
            })
    
    print(f"📈 {len(chunks)} chunks trouvés avec des vecteurs")
    
    # Suppression des anciens circuits QASM
    qasm_dir = "src/quantum/quantum_db"
    if os.path.exists(qasm_dir):
        print("🗑️ Suppression des anciens circuits QASM...")
        for file in os.listdir(qasm_dir):
            if file.endswith('.qasm'):
                os.remove(os.path.join(qasm_dir, file))
        print("✅ Anciens circuits supprimés")
    
    # Recréation des circuits QASM
    print("🔧 Recréation des circuits QASM...")
    
    created_count = 0
    error_count = 0
    
    for i, chunk in enumerate(chunks):
        try:
            # Réduction PCA
            reduced_vector = pca.transform([chunk['vector']])[0]
            
            # Encodage quantique et sauvegarde
            from quantum_encoder import encode_and_save_embedding_amplitude
            qasm_path = encode_and_save_embedding_amplitude(reduced_vector, chunk['row_id'], qasm_dir)
            
            created_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"📝 {i + 1}/{len(chunks)} circuits créés...")
                
        except Exception as e:
            print(f"❌ Erreur pour chunk {chunk['row_id']}: {e}")
            error_count += 1
    
    print(f"\n🎉 Récréation terminée!")
    print(f"✅ {created_count} circuits QASM créés")
    print(f"❌ {error_count} erreurs")
    
    # Vérification finale
    qasm_files = [f for f in os.listdir(qasm_dir) if f.endswith('.qasm')]
    print(f"📁 {len(qasm_files)} fichiers QASM dans le dossier")
    
    if len(qasm_files) == len(chunks):
        print("✅ Synchronisation parfaite entre Cassandra et QASM!")
    else:
        print(f"⚠️ Désynchronisation: {len(chunks)} chunks vs {len(qasm_files)} QASM")

if __name__ == "__main__":
    recreate_all_qasm()
