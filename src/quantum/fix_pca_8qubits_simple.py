#!/usr/bin/env python3
"""
Script simple pour créer le modèle PCA 8 qubits
"""

import os
import sys
import pickle
import numpy as np
from pathlib import Path
from cassandra.cluster import Cluster

def create_pca_model_8qubits():
    """Crée le modèle PCA 8 qubits à partir des embeddings existants"""
    print("🔧 Création du modèle PCA 8 qubits...")
    
    try:
        # Connexion directe à Cassandra
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect()
        
        # Récupérer tous les embeddings
        print("📊 Récupération des embeddings...")
        query = "SELECT vector FROM fact_checker_keyspace.fact_checker_docs"
        rows = session.execute(query)
        
        embeddings = []
        count = 0
        
        for row in rows:
            if row.vector is not None:
                embeddings.append(row.vector)
                count += 1
                if count % 500 == 0:
                    print(f"   {count} embeddings traités...")
        
        print(f"✅ {len(embeddings)} embeddings récupérés")
        
        if len(embeddings) == 0:
            print("❌ Aucun embedding trouvé")
            return False
        
        # Convertir en numpy array
        embeddings_array = np.array(embeddings)
        print(f"📐 Forme des embeddings: {embeddings_array.shape}")
        
        # Créer le PCA pour 8 qubits
        from sklearn.decomposition import PCA
        
        print("🔧 Entraînement du PCA 8 qubits...")
        pca = PCA(n_components=8, random_state=42)
        pca.fit(embeddings_array)
        
        # Sauvegarder le modèle
        pca_path = Path("src/quantum/pca_model_8qubits.pkl")
        with open(pca_path, 'wb') as f:
            pickle.dump(pca, f)
        
        print(f"✅ Modèle PCA 8 qubits sauvegardé: {pca_path}")
        print(f"📊 Variance expliquée: {pca.explained_variance_ratio_.sum():.4f}")
        print(f"🔧 Composantes: {pca.n_components_}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    create_pca_model_8qubits()
