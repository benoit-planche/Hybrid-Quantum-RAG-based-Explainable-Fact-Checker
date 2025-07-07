#!/usr/bin/env python3
"""
Script pour indexer les documents PDF dans ChromaDB
"""

import os
import sys
from chromadb_manager import ChromaDBManager

def main():
    """Indexer les documents PDF dans ChromaDB"""
    
    # Configuration
    data_dir = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
    persist_dir = "./chroma_db"
    embedding_model = "llama2:7b"  # Modèle d'embedding explicite
    
    print("🔍 Indexation des documents PDF dans ChromaDB")
    print(f"📁 Dossier source: {data_dir}")
    print(f"💾 Dossier de persistance: {persist_dir}")
    print(f"🤖 Modèle d'embedding: {embedding_model}")
    print("-" * 50)
    
    # Vérifier que le dossier source existe
    if not os.path.exists(data_dir):
        print(f"❌ Le dossier {data_dir} n'existe pas")
        print("Veuillez créer le dossier et y ajouter vos fichiers PDF")
        return False
    
    # Initialiser ChromaDB
    try:
        chroma_manager = ChromaDBManager(
            persist_directory=persist_dir,
            embedding_model=embedding_model
        )
        print("✅ ChromaDB initialisé")
    except Exception as e:
        print(f"❌ Erreur d'initialisation ChromaDB: {e}")
        return False
    
    # Afficher les informations actuelles
    collection_info = chroma_manager.get_collection_info()
    if collection_info:
        print(f"📊 Collection actuelle: {collection_info.get('document_count', 0)} documents")
    
    # Demander confirmation pour vider la collection
    if collection_info.get('document_count', 0) > 0:
        response = input("⚠️  La collection contient déjà des documents. Voulez-vous la vider ? (y/N): ")
        if response.lower() == 'y':
            chroma_manager.clear_collection()
            print("✅ Collection vidée")
        else:
            print("ℹ️  Ajout des nouveaux documents à la collection existante")
    
    # Indexer les documents
    print("\n🔄 Indexation en cours...")
    success = chroma_manager.load_and_index_documents(data_dir)
    
    if success:
        print("\n✅ Indexation terminée avec succès!")
        
        # Afficher les nouvelles informations
        new_collection_info = chroma_manager.get_collection_info()
        if new_collection_info:
            print(f"📊 Nouveau total: {new_collection_info.get('document_count', 0)} documents")
        
        print(f"💾 Données sauvegardées dans: {persist_dir}")
        return True
    else:
        print("\n❌ Échec de l'indexation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 