#!/usr/bin/env python3
"""
Script pour faire un dump UNIQUEMENT de la colonne vector (embeddings)
"""

import sys
import os
import pickle
import numpy as np
from cassandra.cluster import Cluster
import time

def connect_to_cassandra():
    """Se connecter à Cassandra"""
    try:
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect('fact_checker_keyspace')
        print("✅ Connexion Cassandra établie")
        return session, cluster
    except Exception as e:
        print(f"❌ Erreur connexion Cassandra: {e}")
        return None, None

def dump_embeddings_only(session):
    """Dumper uniquement les embeddings"""
    print("📊 Récupération des embeddings depuis Cassandra...")
    
    # Récupérer TOUS les documents (pas de filtrage sur vector)
    query = "SELECT row_id, vector FROM fact_checker_keyspace.fact_checker_docs"
    rows = session.execute(query)
    
    embeddings_data = {}
    count = 0
    total_rows = 0
    
    for row in rows:
        total_rows += 1
        
        # Filtrer côté Python pour les embeddings non-null
        if row.vector is not None and len(row.vector) > 0:
            embeddings_data[row.row_id] = np.array(row.vector)
            count += 1
            
            if count % 100 == 0:
                print(f"   📥 {count} embeddings récupérés...")
    
    print(f"✅ {count} embeddings récupérés sur {total_rows} documents totaux")
    return embeddings_data

def save_embeddings_dump(embeddings_data, output_file):
    """Sauvegarder le dump des embeddings"""
    try:
        print(f"💾 Sauvegarde dans {output_file}...")
        
        # Sauvegarder avec pickle pour préserver les types numpy
        with open(output_file, 'wb') as f:
            pickle.dump(embeddings_data, f)
        
        # Vérifier la taille du fichier
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"✅ Dump sauvegardé: {file_size:.2f} MB")
        
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False

def verify_embeddings_dump(file_path):
    """Vérifier le dump sauvegardé"""
    try:
        print("🔍 Vérification du dump...")
        
        with open(file_path, 'rb') as f:
            loaded_data = pickle.load(f)
        
        print(f"✅ Dump vérifié: {len(loaded_data)} embeddings")
        
        # Vérifier la structure d'un embedding
        sample_key = list(loaded_data.keys())[0]
        sample_embedding = loaded_data[sample_key]
        print(f"   Exemple: {sample_key} → {sample_embedding.shape} dimensions")
        
        return True
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Dump des embeddings uniquement depuis Cassandra...")
    
    # Connexion à Cassandra
    session, cluster = connect_to_cassandra()
    if not session:
        return
    
    try:
        # Dumper les embeddings
        embeddings_data = dump_embeddings_only(session)
        
        if not embeddings_data:
            print("❌ Aucun embedding trouvé")
            return
        
        # Créer le nom du fichier avec timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"embeddings_dump_{timestamp}.pkl"
        
        # Sauvegarder
        if save_embeddings_dump(embeddings_data, output_file):
            # Vérifier
            if verify_embeddings_dump(output_file):
                print("")
                print("🎉 Dump des embeddings réussi !")
                print(f"📁 Fichier: {output_file}")
                print(f"📊 Total: {len(embeddings_data)} embeddings")
                
                # Afficher quelques exemples
                print("📝 Exemples d'embeddings:")
                for i, (row_id, embedding) in enumerate(list(embeddings_data.items())[:5]):
                    print(f"   {row_id}: {embedding.shape} dimensions")
                
                print("")
                print("📋 Instructions pour le PC distant:")
                print(f"1. Copier {output_file} vers le PC distant")
                print("2. Exécuter: python restore_embeddings.py embeddings_dump_*.pkl")
            else:
                print("❌ Vérification du dump échouée")
        else:
            print("❌ Sauvegarde du dump échouée")
            
    finally:
        # Fermer la connexion
        session.shutdown()
        cluster.shutdown()
        print("🔌 Connexion Cassandra fermée")

if __name__ == "__main__":
    main()
