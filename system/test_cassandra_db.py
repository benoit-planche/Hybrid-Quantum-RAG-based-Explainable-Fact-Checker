#!/usr/bin/env python3
"""
Script pour tester et vérifier le contenu de la base de données Cassandra
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cassandra_manager import create_cassandra_manager

def test_cassandra_connection():
    """Tester la connexion à Cassandra"""
    print("🔍 Test de connexion à Cassandra...")
    
    try:
        manager = create_cassandra_manager()
        print("✅ Connexion réussie")
        return manager
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def check_table_content(manager):
    """Vérifier le contenu de la table"""
    print("\n📊 Vérification du contenu de la table...")
    
    try:
        # Obtenir les informations de la collection
        info = manager.get_collection_info()
        print(f"📋 Informations de la table: {info}")
        
        # Tester une recherche simple
        print("\n🔍 Test de recherche simple...")
        results = manager.search_documents_simple("climate change", n_results=3)
        
        if results:
            print(f"✅ {len(results)} résultats trouvés:")
            for i, doc in enumerate(results, 1):
                print(f"\n--- Document {i} ---")
                print(f"Contenu: {doc['content'][:200]}...")
                print(f"Métadonnées: {doc['metadata']}")
                print(f"Score: {doc['score']}")
        else:
            print("❌ Aucun résultat trouvé")
            
        # Tester une recherche MMR
        print("\n🔍 Test de recherche MMR...")
        mmr_results = manager.search_documents_mmr("global warming", n_results=3, lambda_param=0.5)
        
        if mmr_results:
            print(f"✅ {len(mmr_results)} résultats MMR trouvés:")
            for i, doc in enumerate(mmr_results, 1):
                print(f"\n--- Document MMR {i} ---")
                print(f"Contenu: {doc['content'][:200]}...")
                print(f"Métadonnées: {doc['metadata']}")
                print(f"Score: {doc['score']}")
        else:
            print("❌ Aucun résultat MMR trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

def query_cassandra_directly():
    """Interroger Cassandra directement avec CQL"""
    print("\n🔍 Requête directe Cassandra...")
    
    try:
        from cassandra.cluster import Cluster
        
        # Connexion directe
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect('fact_checker_keyspace')
        
        # Compter les lignes dans la table
        result = session.execute(f"SELECT COUNT(*) FROM fact_checker_docs")
        count = result.one()[0]
        print(f"📊 Nombre de documents dans la table: {count}")
        
        # Afficher quelques exemples
        result = session.execute(f"SELECT * FROM fact_checker_docs LIMIT 3")
        rows = list(result)
        
        if rows:
            print(f"\n📄 Exemples de documents:")
            for i, row in enumerate(rows, 1):
                print(f"\n--- Ligne {i} ---")
                print(f"ID: {row.row_id}")
                print(f"Contenu: {row.body_blob[:200]}..." if row.body_blob else "Pas de contenu")
                print(f"Métadonnées: {row.metadata}")
        else:
            print("❌ Aucune donnée trouvée dans la table")
            
    except Exception as e:
        print(f"❌ Erreur lors de la requête directe: {e}")

def main():
    """Fonction principale"""
    print("🔍 Test de la base de données Cassandra")
    print("=" * 50)
    
    # Test de connexion
    manager = test_cassandra_connection()
    
    if manager:
        # Vérifier le contenu
        check_table_content(manager)
        
        # Requête directe
        query_cassandra_directly()
    
    print("\n✅ Test terminé")

if __name__ == "__main__":
    main() 