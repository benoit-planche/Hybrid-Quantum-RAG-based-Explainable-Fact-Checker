#!/usr/bin/env python3
"""
Script simple pour réindexer tous les PDFs du dossier rapport
"""

import os
import sys

sys.path.append('system')
sys.path.append('src/quantum')

from cassandra_manager import CassandraVectorStoreManager

def reindex_all_pdfs():
    """Réindexe tous les PDFs du dossier rapport"""
    print("🚀 RÉINDEXATION COMPLÈTE DE TOUS LES PDFS")
    print("=" * 50)
    
    # Chemin du dossier rapport
    rapport_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
    
    if not os.path.exists(rapport_dir):
        print(f"❌ Dossier rapport non trouvé: {rapport_dir}")
        return False
    
    # Compter les PDFs
    pdf_files = [f for f in os.listdir(rapport_dir) if f.lower().endswith('.pdf')]
    print(f"📊 {len(pdf_files)} PDFs trouvés dans le dossier rapport")
    
    # Demander confirmation
    response = input(f"\n❓ Réindexer tous les {len(pdf_files)} PDFs ? (y/N): ")
    if response.lower() != 'y':
        print("❌ Opération annulée")
        return False
    
    # Créer le gestionnaire Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Réindexer tous les PDFs
    print(f"\n🔄 Indexation de tous les PDFs...")
    success = cassandra_manager.load_and_index_documents(rapport_dir)
    
    if success:
        print("✅ Réindexation terminée avec succès !")
        
        # Vérifier le résultat
        print(f"\n📊 Vérification...")
        session = cassandra_manager.session
        query = "SELECT COUNT(*) FROM fact_checker_keyspace.fact_checker_docs"
        result = session.execute(query)
        total_chunks = result.one()[0]
        print(f"📊 Total chunks dans Cassandra: {total_chunks}")
        
        return True
    else:
        print("❌ Erreur lors de la réindexation")
        return False

if __name__ == "__main__":
    reindex_all_pdfs() 