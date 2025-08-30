#!/usr/bin/env python3
"""
Script pour restaurer les embeddings depuis un dump pickle
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

def load_embeddings_dump(dump_file):
    """Charger le dump des embeddings"""
    try:
        print(f"📥 Chargement du dump: {dump_file}")
        
        with open(dump_file, 'rb') as f:
            embeddings_data = pickle.load(f)
        
        print(f"✅ Dump chargé: {len(embeddings_data)} embeddings")
        
        # Vérifier la structure
        sample_key = list(embeddings_data.keys())[0]
        sample_embedding = embeddings_data[sample_key]
        print(f"   Structure: {sample_key} → {sample_embedding.shape} dimensions")
        
        return embeddings_data
    except Exception as e:
        print(f"❌ Erreur chargement dump: {e}")
        return None

def restore_embeddings_to_cassandra(session, embeddings_data):
    """Restaurer les embeddings dans Cassandra"""
    print("🔄 Restauration des embeddings dans Cassandra...")
    
    # Préparer la requête de mise à jour
    update_query = "UPDATE fact_checker_keyspace.fact_checker_docs SET vector = ? WHERE partition_id = 'None' AND row_id = ?"
    prepared_stmt = session.prepare(update_query)
    
    success_count = 0
    error_count = 0
    
    for i, (row_id, embedding) in enumerate(embeddings_data.items()):
        try:
            # Mettre à jour l'embedding
            session.execute(prepared_stmt, (embedding.tolist(), row_id))
            success_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"   ✅ {i + 1} embeddings restaurés...")
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Erreur pour {row_id}: {e}")
            continue
    
    print(f"✅ Restauration terminée: {success_count} succès, {error_count} erreurs")
    return success_count, error_count

def verify_restoration(session):
    """Vérifier que les embeddings ont été restaurés"""
    print("🔍 Vérification de la restauration...")
    
    try:
        # Compter les embeddings non-null
        count_query = "SELECT COUNT(*) FROM fact_checker_keyspace.fact_checker_docs WHERE vector IS NOT NULL ALLOW FILTERING"
        result = session.execute(count_query)
        count = result.one()[0]
        
        print(f"✅ {count} embeddings trouvés dans Cassandra")
        
        # Vérifier un exemple
        sample_query = "SELECT row_id, vector FROM fact_checker_keyspace.fact_checker_docs WHERE vector IS NOT NULL LIMIT 1 ALLOW FILTERING"
        sample_result = session.execute(sample_query)
        sample_row = sample_result.one()
        
        if sample_row:
            vector_length = len(sample_row.vector)
            print(f"   Exemple: {sample_row.row_id} → {vector_length} dimensions")
        
        return count > 0
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

def main():
    """Fonction principale"""
    if len(sys.argv) != 2:
        print("Usage: python restore_embeddings.py <fichier_dump.pkl>")
        return
    
    dump_file = sys.argv[1]
    
    if not os.path.exists(dump_file):
        print(f"❌ Fichier dump non trouvé: {dump_file}")
        return
    
    print("🚀 Restauration des embeddings depuis le dump...")
    
    # Charger le dump
    embeddings_data = load_embeddings_dump(dump_file)
    if not embeddings_data:
        return
    
    # Connexion à Cassandra
    session, cluster = connect_to_cassandra()
    if not session:
        return
    
    try:
        # Restaurer les embeddings
        success_count, error_count = restore_embeddings_to_cassandra(session, embeddings_data)
        
        if success_count > 0:
            # Vérifier la restauration
            if verify_restoration(session):
                print("")
                print("🎉 Restauration des embeddings réussie !")
                print("✅ Vous pouvez maintenant créer le modèle PCA")
                print("✅ Et recréer les circuits QASM")
            else:
                print("❌ Vérification de la restauration échouée")
        else:
            print("❌ Aucun embedding n'a pu être restauré")
            
    finally:
        # Fermer la connexion
        session.shutdown()
        cluster.shutdown()
        print("🔌 Connexion Cassandra fermée")

if __name__ == "__main__":
    main()
