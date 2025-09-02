#!/usr/bin/env python3
"""Script de debug pour vérifier la structure de la base Cassandra"""

import sys
import os

# Ajouter les chemins nécessaires
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(current_dir, 'system')
sys.path.insert(0, system_dir)

from cassandra_manager import CassandraVectorStoreManager

def debug_cassandra_structure():
    """Vérifier la structure de la base Cassandra"""
    
    try:
        # Initialiser la connexion
        cassandra_manager = CassandraVectorStoreManager()
        
        # Requête pour examiner la structure
        query = "SELECT row_id, metadata_s, body_blob FROM fact_checker_keyspace.fact_checker_docs LIMIT 10"
        rows = cassandra_manager.session.execute(query)
        
        print("🔍 STRUCTURE DE LA BASE CASSANDRA:")
        print("="*80)
        
        for i, row in enumerate(rows):
            print(f"\n📄 Chunk {i+1}:")
            print(f"   row_id: {row.row_id}")
            print(f"   metadata_s: {row.metadata_s}")
            print(f"   metadata_s type: {type(row.metadata_s)}")
            
            if row.metadata_s is not None:
                print(f"   chunk_id from metadata: {row.metadata_s.get('chunk_id', 'N/A')}")
                print(f"   source from metadata: {row.metadata_s.get('source', 'N/A')}")
            else:
                print(f"   ⚠️ metadata_s est None!")
            
            print(f"   body_blob length: {len(row.body_blob) if row.body_blob else 0}")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cassandra_structure()
