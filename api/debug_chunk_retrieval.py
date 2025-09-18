#!/usr/bin/env python3
"""
Script pour diagnostiquer le problème de récupération des chunks
"""

import sys
import os
sys.path.append('../system')
sys.path.append('../src/quantum')

from cassandra_manager import create_cassandra_manager

def debug_chunk_retrieval():
    """Diagnostiquer le problème de récupération des chunks"""
    
    print("🔍 DIAGNOSTIC DE LA RÉCUPÉRATION DES CHUNKS")
    print("=" * 60)
    
    # Connexion à Cassandra
    cassandra_manager = create_cassandra_manager()
    
    # Test avec les chunk_ids trouvés par Grover
    test_chunk_ids = ["2386", "2942", "982", "2343", "3458"]
    
    print(f"📝 Test avec les chunk_ids: {test_chunk_ids}")
    
    for chunk_id in test_chunk_ids:
        print(f"\n🔍 Test chunk_id: {chunk_id}")
        
        # Méthode 1: Avec partition_id = "None"
        print(f"   Méthode 1 (partition_id='None'):")
        try:
            query = "SELECT body_blob, metadata_s FROM fact_checker_keyspace.fact_checker_docs WHERE partition_id=%s AND row_id=%s;"
            row = cassandra_manager.session.execute(query, ("None", chunk_id)).one()
            
            if row and row.body_blob:
                text_preview = row.body_blob[:100] + "..." if len(row.body_blob) > 100 else row.body_blob
                print(f"   ✅ Trouvé: {text_preview}")
            else:
                print(f"   ❌ Pas trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Méthode 2: Avec row_id seulement
        print(f"   Méthode 2 (row_id seulement):")
        try:
            query = "SELECT body_blob, metadata_s FROM fact_checker_keyspace.fact_checker_docs WHERE row_id=%s LIMIT 1 ALLOW FILTERING;"
            row = cassandra_manager.session.execute(query, (chunk_id,)).one()
            
            if row and row.body_blob:
                text_preview = row.body_blob[:100] + "..." if len(row.body_blob) > 100 else row.body_blob
                print(f"   ✅ Trouvé: {text_preview}")
            else:
                print(f"   ❌ Pas trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Méthode 3: Avec doc_ prefix
        print(f"   Méthode 3 (doc_ prefix):")
        try:
            doc_chunk_id = f"doc_{chunk_id}"
            query = "SELECT body_blob, metadata_s FROM fact_checker_keyspace.fact_checker_docs WHERE partition_id=%s AND row_id=%s;"
            row = cassandra_manager.session.execute(query, ("None", doc_chunk_id)).one()
            
            if row and row.body_blob:
                text_preview = row.body_blob[:100] + "..." if len(row.body_blob) > 100 else row.body_blob
                print(f"   ✅ Trouvé: {text_preview}")
            else:
                print(f"   ❌ Pas trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Analyser la structure de la base
    print(f"\n📊 ANALYSE DE LA STRUCTURE DE LA BASE")
    print("=" * 40)
    
    try:
        # Compter le nombre total de chunks
        query = "SELECT COUNT(*) FROM fact_checker_keyspace.fact_checker_docs;"
        result = cassandra_manager.session.execute(query).one()
        total_chunks = result.count if hasattr(result, 'count') else 0
        print(f"📈 Total chunks dans la base: {total_chunks}")
        
        # Analyser les partition_id
        query = "SELECT DISTINCT partition_id FROM fact_checker_keyspace.fact_checker_docs LIMIT 10;"
        rows = cassandra_manager.session.execute(query)
        partition_ids = [row.partition_id for row in rows]
        print(f"📊 Partition IDs trouvés: {partition_ids}")
        
        # Analyser les row_id
        query = "SELECT row_id FROM fact_checker_keyspace.fact_checker_docs LIMIT 10;"
        rows = cassandra_manager.session.execute(query)
        row_ids = [row.row_id for row in rows]
        print(f"📊 Exemples de row_id: {row_ids}")
        
        # Vérifier si les chunks ont du contenu
        query = "SELECT row_id, body_blob FROM fact_checker_keyspace.fact_checker_docs WHERE body_blob IS NOT NULL LIMIT 5;"
        rows = cassandra_manager.session.execute(query)
        chunks_with_content = 0
        for row in rows:
            if row.body_blob and len(row.body_blob.strip()) > 0:
                chunks_with_content += 1
                print(f"   ✅ Chunk {row.row_id}: {len(row.body_blob)} caractères")
        
        print(f"📊 Chunks avec contenu: {chunks_with_content}/5")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")

if __name__ == "__main__":
    debug_chunk_retrieval()
