#!/usr/bin/env python3
"""
Script pour ajouter les PDFs manquants sans écraser les chunks existants
"""

import os
import sys
import time
import random

sys.path.append('system')
sys.path.append('src/quantum')

from cassandra_manager import CassandraVectorStoreManager
from quantum_encoder import amplitude_encoding
from quantum_db import save_qasm_circuit
import joblib
import numpy as np

def get_existing_chunk_ids():
    """Récupère les IDs des chunks existants"""
    print("📊 Récupération des IDs existants...")
    
    cassandra_manager = CassandraVectorStoreManager()
    session = cassandra_manager.session
    
    query = "SELECT row_id FROM fact_checker_keyspace.fact_checker_docs"
    rows = session.execute(query)
    
    existing_ids = set()
    for row in rows:
        if row.row_id:
            existing_ids.add(row.row_id)
    
    print(f"✅ {len(existing_ids)} IDs existants trouvés")
    return existing_ids

def get_missing_pdfs():
    """Identifie les PDFs manquants"""
    print("🔍 Identification des PDFs manquants...")
    
    # Récupérer les PDFs indexés
    cassandra_manager = CassandraVectorStoreManager()
    session = cassandra_manager.session
    
    query = "SELECT metadata_s FROM fact_checker_keyspace.fact_checker_docs LIMIT 1000"
    rows = session.execute(query)
    
    indexed_pdfs = set()
    for row in rows:
        if hasattr(row.metadata_s, 'keys'):
            metadata_dict = dict(row.metadata_s)
            if 'source' in metadata_dict:
                indexed_pdfs.add(metadata_dict['source'])
    
    # Récupérer tous les PDFs du dossier
    rapport_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
    all_pdfs = set()
    if os.path.exists(rapport_dir):
        for file in os.listdir(rapport_dir):
            if file.lower().endswith('.pdf'):
                all_pdfs.add(file)
    
    # Calculer les PDFs manquants
    missing_pdfs = all_pdfs - indexed_pdfs
    
    print(f"📊 PDFs dans le dossier: {len(all_pdfs)}")
    print(f"📊 PDFs indexés: {len(indexed_pdfs)}")
    print(f"📊 PDFs manquants: {len(missing_pdfs)}")
    
    return list(missing_pdfs)

def add_pdfs_with_unique_ids(pdf_list, existing_ids):
    """Ajoute les PDFs avec des IDs uniques"""
    print(f"🚀 Ajout de {len(pdf_list)} PDFs avec IDs uniques...")
    
    cassandra_manager = CassandraVectorStoreManager()
    
    # Trouver le prochain ID disponible
    max_id = 0
    for existing_id in existing_ids:
        if existing_id.startswith('doc_'):
            try:
                id_num = int(existing_id[4:])
                max_id = max(max_id, id_num)
            except:
                pass
    
    next_id = max_id + 1
    print(f"🆔 Prochain ID disponible: doc_{next_id}")
    
    # Traiter chaque PDF
    success_count = 0
    error_count = 0
    
    for pdf_name in pdf_list:
        try:
            print(f"\n📄 Traitement: {pdf_name}")
            
            # Charger le PDF
            pdf_path = os.path.join("/home/moi/Documents/internship/climat-misinformation-detection/rapport", pdf_name)
            if not os.path.exists(pdf_path):
                print(f"  ❌ Fichier non trouvé: {pdf_path}")
                error_count += 1
                continue
            
            # Charger le document
            from pdf_loader import PDFDocumentLoader
            doc = PDFDocumentLoader.load_single_file(pdf_path)
            if not doc:
                print(f"  ❌ Impossible de charger: {pdf_name}")
                error_count += 1
                continue
            
            # Splitter en chunks
            from llama_index.core.node_parser import SimpleTextSplitter
            splitter = SimpleTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_documents([doc])
            
            print(f"  ✂️ {len(chunks)} chunks créés")
            
            # Préparer les données avec IDs uniques
            texts = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                texts.append(chunk['page_content'])
                metadatas.append({
                    'source': chunk['metadata'].get('source', pdf_name),
                    'file_path': chunk['metadata'].get('file_path', pdf_path),
                    'chunk_id': i
                })
                ids.append(f"doc_{next_id + i}")
            
            # Générer les embeddings
            print(f"  🔄 Génération des embeddings...")
            embeddings_list = cassandra_manager.embed_model.get_text_embedding_batch(
                texts, 
                show_progress=False
            )
            
            # Créer les nodes
            from llama_index.core.schema import Node
            nodes = []
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings_list, metadatas)):
                node = Node(
                    text=text,
                    embedding=embedding,
                    metadata=metadata,
                    id_=ids[i]
                )
                nodes.append(node)
            
            # Ajouter à Cassandra
            cassandra_manager.vector_store.add(nodes)
            
            # Ajouter le texte dans body_blob
            cassandra_manager._add_text_to_body_blob(texts, ids)
            
            # Créer les circuits QASM
            print(f"  ⚡ Création des circuits QASM...")
            create_qasm_for_chunks(ids, embeddings_list)
            
            # Mettre à jour les IDs
            next_id += len(chunks)
            success_count += 1
            
            print(f"  ✅ {pdf_name} ajouté avec succès")
            
            # Pause entre les PDFs
            time.sleep(random.randint(2, 5))
            
        except Exception as e:
            print(f"  ❌ Erreur pour {pdf_name}: {e}")
            error_count += 1
    
    # Recharger l'index
    cassandra_manager._reload_index()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"  ✅ PDFs ajoutés: {success_count}")
    print(f"  ❌ Erreurs: {error_count}")
    
    return success_count > 0

def create_qasm_for_chunks(chunk_ids, embeddings):
    """Crée les circuits QASM pour les nouveaux chunks"""
    try:
        # Charger le PCA
        pca_path = "src/quantum/pca_model.pkl"
        if os.path.exists(pca_path):
            pca = joblib.load(pca_path)
        else:
            print("⚠️ PCA non trouvé, création d'un nouveau")
            pca = None
        
        # Créer le dossier quantum_db
        db_folder = "src/quantum/quantum_db"
        os.makedirs(db_folder, exist_ok=True)
        
        # Créer les circuits
        for chunk_id, embedding in zip(chunk_ids, embeddings):
            try:
                # Réduire l'embedding si PCA disponible
                if pca is not None:
                    embedding_reduced = pca.transform([embedding])[0]
                else:
                    embedding_reduced = embedding[:16]  # Fallback
                
                # Encoder en circuit
                qc = amplitude_encoding(embedding_reduced, 16)
                
                # Sauvegarder
                qasm_path = os.path.join(db_folder, f"{chunk_id}.qasm")
                save_qasm_circuit(qc, qasm_path)
                
            except Exception as e:
                print(f"    ❌ Erreur QASM pour {chunk_id}: {e}")
                
    except Exception as e:
        print(f"❌ Erreur création QASM: {e}")

def main():
    """Script principal"""
    print("🚀 AJOUT DES PDFS MANQUANTS")
    print("=" * 50)
    
    # 1. Récupérer les IDs existants
    existing_ids = get_existing_chunk_ids()
    
    # 2. Identifier les PDFs manquants
    missing_pdfs = get_missing_pdfs()
    
    if not missing_pdfs:
        print("✅ Aucun PDF manquant")
        return
    
    # 3. Demander confirmation
    print(f"\n📋 PDFs manquants ({len(missing_pdfs)}):")
    for pdf in missing_pdfs[:10]:
        print(f"  - {pdf}")
    if len(missing_pdfs) > 10:
        print(f"  ... et {len(missing_pdfs) - 10} autres")
    
    response = input(f"\n❓ Ajouter ces {len(missing_pdfs)} PDFs ? (y/N): ")
    if response.lower() != 'y':
        print("❌ Opération annulée")
        return
    
    # 4. Ajouter les PDFs
    success = add_pdfs_with_unique_ids(missing_pdfs, existing_ids)
    
    if success:
        print("\n🎉 Opération terminée avec succès !")
    else:
        print("\n⚠️ Opération terminée avec des erreurs")

if __name__ == "__main__":
    main() 