#!/usr/bin/env python3
"""
Script pour vérifier l'indexation des PDFs dans Cassandra
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../system')))
from cassandra_manager import create_cassandra_manager

# Configuration
KEYSPACE = "fact_checker_keyspace"
TABLE = "fact_checker_docs"

def check_pdf_indexing():
    """Vérifie quels PDFs sont indexés dans Cassandra"""
    print("🔍 VÉRIFICATION INDEXATION PDFS")
    print("=" * 60)
    
    # Connexion à Cassandra
    cassandra_manager = create_cassandra_manager(table_name=TABLE, keyspace=KEYSPACE)
    
    # Récupérer tous les chunks avec métadonnées
    session = cassandra_manager.session
    query = f"SELECT partition_id, row_id, metadata_s FROM {KEYSPACE}.{TABLE}"
    rows = session.execute(query)
    
    print(f"📊 Total chunks dans Cassandra: {len(list(rows))}")
    
    # Réexécuter la requête pour l'analyse
    rows = session.execute(query)
    
    # Analyser les sources PDF
    pdf_sources = {}
    antarctica_found = False
    
    for row in rows:
        try:
            # Extraire le nom du PDF depuis metadata_s
            metadata = row.metadata_s
            
            # Gérer les OrderedMapSerializedKey de Cassandra
            if hasattr(metadata, 'keys'):
                # C'est un OrderedMapSerializedKey
                metadata_dict = dict(metadata)
                pdf_name = metadata_dict.get('source', 'Unknown')
            elif isinstance(metadata, str):
                # Essayer de parser comme JSON
                try:
                    metadata_dict = json.loads(metadata)
                    pdf_name = metadata_dict.get('source', 'Unknown')
                except:
                    pdf_name = 'Unknown'
            else:
                pdf_name = 'Unknown'
            
            if pdf_name not in pdf_sources:
                pdf_sources[pdf_name] = 0
            pdf_sources[pdf_name] += 1
            
            # Vérifier si c'est le PDF antarctique
            if 'antarctica' in pdf_name.lower():
                antarctica_found = True
                print(f"✅ PDF antarctique trouvé: {pdf_name}")
                
        except Exception as e:
            print(f"❌ Erreur parsing metadata: {e}")
    
    # Afficher les PDFs indexés
    print(f"\n📚 PDFS INDEXÉS DANS CASSANDRA:")
    print("-" * 50)
    
    sorted_pdfs = sorted(pdf_sources.items(), key=lambda x: x[1], reverse=True)
    for pdf_name, chunk_count in sorted_pdfs[:20]:  # Top 20
        print(f"  {pdf_name}: {chunk_count} chunks")
    
    if len(sorted_pdfs) > 20:
        print(f"  ... et {len(sorted_pdfs) - 20} autres PDFs")
    
    # Vérifier le dossier rapport
    print(f"\n📁 VÉRIFICATION DOSSIER RAPPORT:")
    print("-" * 50)
    
    rapport_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
    if os.path.exists(rapport_dir):
        pdf_files = [f for f in os.listdir(rapport_dir) if f.lower().endswith('.pdf')]
        print(f"📊 PDFs dans le dossier rapport: {len(pdf_files)}")
        
        antarctica_pdfs = [f for f in pdf_files if 'antarctica' in f.lower()]
        print(f"📊 PDFs antarctiques dans le dossier: {antarctica_pdfs}")
        
        # Vérifier quels PDFs du dossier ne sont pas indexés
        indexed_pdfs = set(pdf_sources.keys())
        missing_pdfs = []
        
        for pdf_file in pdf_files:
            if pdf_file not in indexed_pdfs:
                missing_pdfs.append(pdf_file)
        
        print(f"📊 PDFs manquants dans Cassandra: {len(missing_pdfs)}")
        if missing_pdfs:
            print("  PDFs manquants:")
            for pdf in missing_pdfs[:10]:  # Top 10
                print(f"    - {pdf}")
            if len(missing_pdfs) > 10:
                print(f"    ... et {len(missing_pdfs) - 10} autres")
    else:
        print(f"❌ Dossier rapport non trouvé: {rapport_dir}")
    
    # Résumé
    print(f"\n📋 RÉSUMÉ:")
    print("-" * 50)
    print(f"✅ Total chunks indexés: {len(list(session.execute(query)))}")
    print(f"✅ Total PDFs indexés: {len(pdf_sources)}")
    print(f"❓ PDF antarctique trouvé: {antarctica_found}")
    
    if not antarctica_found:
        print("\n🚨 ACTIONS REQUISES:")
        print("1. Vérifier que antarctica-gaining-ice-basic.pdf existe dans le dossier rapport")
        print("2. Lancer reindex_missing_pdfs.py pour indexer les PDFs manquants")
        print("3. Relancer extract_embeddings_from_cassandra.py pour créer les circuits QASM")

def main():
    check_pdf_indexing()

if __name__ == "__main__":
    main() 