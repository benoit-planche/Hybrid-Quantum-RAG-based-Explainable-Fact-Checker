#!/usr/bin/env python3
"""
Script de vérification rapide de la synchronisation entre Cassandra et QASM
"""

import sys
import os
sys.path.append('system')

from cassandra_manager import CassandraVectorStoreManager

def verify_qasm_sync():
    """Vérifie la synchronisation entre Cassandra et les fichiers QASM"""
    
    print("🔍 Vérification de la synchronisation Cassandra ↔ QASM...")
    
    # Connexion à Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Comptage des chunks dans Cassandra
    session = cassandra_manager.session
    query = "SELECT COUNT(*) as count FROM fact_checker_keyspace.fact_checker_docs"
    result = session.execute(query)
    cassandra_count = result[0].count
    
    print(f"📊 Chunks dans Cassandra: {cassandra_count}")
    
    # Comptage des fichiers QASM
    qasm_dir = "src/quantum/quantum_db"
    if os.path.exists(qasm_dir):
        qasm_files = [f for f in os.listdir(qasm_dir) if f.endswith('.qasm')]
        qasm_count = len(qasm_files)
        print(f"📁 Fichiers QASM: {qasm_count}")
    else:
        print("❌ Dossier QASM non trouvé")
        return
    
    # Vérification de la synchronisation
    if cassandra_count == qasm_count:
        print("✅ Synchronisation parfaite!")
    else:
        print(f"⚠️ Désynchronisation: {cassandra_count} chunks vs {qasm_count} QASM")
        
        # Vérification des IDs manquants
        if cassandra_count > qasm_count:
            print("🔍 Recherche des chunks sans QASM...")
            
            # Récupération des IDs Cassandra
            query = "SELECT row_id FROM fact_checker_keyspace.fact_checker_docs"
            rows = session.execute(query)
            cassandra_ids = {row.row_id for row in rows}
            
            # Récupération des IDs QASM
            qasm_ids = {f.replace('.qasm', '') for f in qasm_files}
            
            # IDs manquants
            missing_qasm = cassandra_ids - qasm_ids
            if missing_qasm:
                print(f"❌ {len(missing_qasm)} chunks sans QASM:")
                for missing_id in list(missing_qasm)[:10]:  # Afficher les 10 premiers
                    print(f"   - {missing_id}")
                if len(missing_qasm) > 10:
                    print(f"   ... et {len(missing_qasm) - 10} autres")
        
        elif qasm_count > cassandra_count:
            print("🔍 Recherche des QASM orphelins...")
            
            # Récupération des IDs Cassandra
            query = "SELECT row_id FROM fact_checker_keyspace.fact_checker_docs"
            rows = session.execute(query)
            cassandra_ids = {row.row_id for row in rows}
            
            # Récupération des IDs QASM
            qasm_ids = {f.replace('.qasm', '') for f in qasm_files}
            
            # QASM orphelins
            orphan_qasm = qasm_ids - cassandra_ids
            if orphan_qasm:
                print(f"🗑️ {len(orphan_qasm)} QASM orphelins:")
                for orphan_id in list(orphan_qasm)[:10]:  # Afficher les 10 premiers
                    print(f"   - {orphan_id}")
                if len(orphan_qasm) > 10:
                    print(f"   ... et {len(orphan_qasm) - 10} autres")

if __name__ == "__main__":
    verify_qasm_sync()
