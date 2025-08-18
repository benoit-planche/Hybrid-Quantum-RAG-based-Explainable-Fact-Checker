#!/usr/bin/env python3
"""
Script pour réindexer les PDFs manquants dans Cassandra et créer les circuits QASM
"""

import os
import sys
import glob
from typing import Set, List

# Ajouter le chemin pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../system')))
from cassandra_manager import create_cassandra_manager
from quantum_encoder import angle_encoding
from quantum_db import save_qasm_circuit
from sklearn.decomposition import PCA
import numpy as np

# Configuration
RAPPORT_FOLDER = "../../../rapport"
DB_FOLDER = "quantum_db/"
KEYSPACE = "fact_checker_keyspace"
TABLE = "fact_checker_docs"
N_QUBITS = 16

def list_all_pdf_sources(cassandra_manager) -> Set[str]:
    """Liste tous les PDFs indexés dans Cassandra"""
    query = f"SELECT metadata_s FROM {cassandra_manager.keyspace}.{cassandra_manager.table_name};"
    sources = set()
    for row in cassandra_manager.session.execute(query):
        if row.metadata_s and 'source' in row.metadata_s:
            sources.add(row.metadata_s['source'])
    return sources

def list_all_pdfs_in_folder(folder: str) -> Set[str]:
    """Liste tous les PDFs présents dans un dossier"""
    pdfs = set([os.path.basename(f) for f in glob.glob(os.path.join(folder, '*.pdf'))])
    return pdfs

def get_missing_pdfs() -> List[str]:
    """Récupère la liste des PDFs présents dans le dossier mais pas dans Cassandra"""
    print("🔍 Analyse des PDFs manquants...")
    
    # Connexion à Cassandra
    cassandra_manager = create_cassandra_manager(table_name=TABLE, keyspace=KEYSPACE)
    
    # Lister les PDFs indexés et présents
    indexed_pdfs = list_all_pdf_sources(cassandra_manager)
    rapport_pdfs = list_all_pdfs_in_folder(RAPPORT_FOLDER)
    
    # Calculer les PDFs manquants
    missing_pdfs = rapport_pdfs - indexed_pdfs
    
    print(f"📊 PDFs indexés dans Cassandra : {len(indexed_pdfs)}")
    print(f"📁 PDFs présents dans {RAPPORT_FOLDER} : {len(rapport_pdfs)}")
    print(f"❌ PDFs manquants : {len(missing_pdfs)}")
    
    return sorted(list(missing_pdfs))

def index_pdfs_in_cassandra(pdf_list: List[str]) -> bool:
    """Indexe seulement les PDFs manquants dans Cassandra"""
    print(f"\n🔄 Indexation de {len(pdf_list)} PDFs manquants dans Cassandra...")
    
    try:
        # Créer le gestionnaire Cassandra
        cassandra_manager = create_cassandra_manager(table_name=TABLE, keyspace=KEYSPACE)
        
        # Indexer seulement les PDFs manquants
        success = cassandra_manager.load_and_index_specific_documents(RAPPORT_FOLDER, pdf_list)
        
        if success:
            print("✅ Indexation Cassandra réussie")
            return True
        else:
            print("❌ Échec de l'indexation Cassandra")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'indexation Cassandra : {e}")
        return False

def create_qasm_circuits() -> bool:
    """Convertit tous les chunks de Cassandra en circuits QASM"""
    print(f"\n🔧 Création des circuits QASM...")
    
    try:
        # Connexion à Cassandra
        cassandra_manager = create_cassandra_manager(table_name=TABLE, keyspace=KEYSPACE)
        
        # Récupérer tous les chunks avec leurs embeddings
        print("📥 Récupération des chunks depuis Cassandra...")
        all_chunks = cassandra_manager.get_all_chunks_with_embeddings()
        print(f"📊 {len(all_chunks)} chunks trouvés")
        
        if not all_chunks:
            print("❌ Aucun chunk trouvé dans Cassandra")
            return False
        
        # Préparer les embeddings pour PCA
        print("🔢 Préparation des embeddings pour PCA...")
        all_embeddings = [np.array(c['embedding'], dtype=float) for c in all_chunks]
        
        # Appliquer PCA pour réduire à N_QUBITS dimensions
        print(f"📉 Réduction PCA à {N_QUBITS} dimensions...")
        pca = PCA(n_components=N_QUBITS)
        reduced_embeddings = pca.fit_transform(all_embeddings)
        
        # Créer le dossier quantum_db s'il n'existe pas
        os.makedirs(DB_FOLDER, exist_ok=True)
        
        # Convertir chaque chunk en circuit QASM
        print("⚡ Conversion en circuits QASM...")
        success_count = 0
        error_count = 0
        
        for i, (chunk, embedding_reduced) in enumerate(zip(all_chunks, reduced_embeddings)):
            try:
                chunk_id = chunk['id']
                
                # Encoder l'embedding réduit en circuit quantique
                qc = angle_encoding(embedding_reduced)
                
                # Sauvegarder le circuit QASM
                qasm_path = os.path.join(DB_FOLDER, f"{chunk_id}.qasm")
                save_qasm_circuit(qc, qasm_path)
                
                success_count += 1
                
                # Afficher le progrès tous les 100 chunks
                if (i + 1) % 100 == 0:
                    print(f"  ✅ {i + 1}/{len(all_chunks)} circuits créés")
                    
            except Exception as e:
                print(f"  ❌ Erreur pour chunk {chunk_id}: {e}")
                error_count += 1
        
        print(f"\n📊 Résumé de la conversion QASM:")
        print(f"  ✅ Circuits créés avec succès : {success_count}")
        print(f"  ❌ Erreurs : {error_count}")
        print(f"  📁 Circuits sauvegardés dans : {DB_FOLDER}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des circuits QASM : {e}")
        return False

def main():
    """Script principal"""
    print("🚀 SCRIPT DE RÉINDEXATION DES PDFs MANQUANTS")
    print("=" * 60)
    
    # Étape 1 : Identifier les PDFs manquants
    print("\n📋 ÉTAPE 1 : Identification des PDFs manquants")
    print("-" * 40)
    missing_pdfs = get_missing_pdfs()
    
    if not missing_pdfs:
        print("✅ Tous les PDFs sont déjà indexés !")
        return
    
    print(f"\n📄 PDFs à indexer ({len(missing_pdfs)}) :")
    for pdf in missing_pdfs[:10]:  # Afficher les 10 premiers
        print(f"  - {pdf}")
    if len(missing_pdfs) > 10:
        print(f"  ... et {len(missing_pdfs) - 10} autres")
    
    # Demander confirmation
    response = input(f"\n❓ Voulez-vous indexer ces {len(missing_pdfs)} PDFs ? (y/N): ")
    if response.lower() != 'y':
        print("❌ Opération annulée")
        return
    
    # Étape 2 : Indexer dans Cassandra
    print(f"\n📋 ÉTAPE 2 : Indexation dans Cassandra")
    print("-" * 40)
    cassandra_success = index_pdfs_in_cassandra(missing_pdfs)
    
    if not cassandra_success:
        print("❌ Échec de l'indexation Cassandra. Arrêt du script.")
        return
    
    # Étape 3 : Créer les circuits QASM
    print(f"\n📋 ÉTAPE 3 : Création des circuits QASM")
    print("-" * 40)
    qasm_success = create_qasm_circuits()
    
    # Résumé final
    print(f"\n🏁 RÉSUMÉ FINAL")
    print("=" * 60)
    if cassandra_success and qasm_success:
        print("✅ RÉUSSITE COMPLÈTE !")
        print(f"  📊 {len(missing_pdfs)} PDFs indexés dans Cassandra")
        print(f"  ⚡ Circuits QASM créés dans {DB_FOLDER}")
        print(f"  🔍 Votre base quantum RAG est maintenant complète !")
    else:
        print("⚠️ RÉUSSITE PARTIELLE")
        if cassandra_success:
            print("  ✅ Indexation Cassandra réussie")
        else:
            print("  ❌ Échec indexation Cassandra")
        if qasm_success:
            print("  ✅ Création circuits QASM réussie")
        else:
            print("  ❌ Échec création circuits QASM")

if __name__ == "__main__":
    main() 