#!/usr/bin/env python3
"""
Script pour refaire les embeddings avec Cassandra
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cassandra_manager import create_cassandra_manager

def main():
    """Embedding des documents avec llama_index OllamaEmbeddings et CassandraVectorStore"""
    
    print("🔄 Début de l'indexation avec Cassandra...")
    
    # Créer le gestionnaire Cassandra
    manager = create_cassandra_manager()
    
    # Chemin vers les données
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "../../llm/rapport")
    
    if not os.path.exists(data_dir):
        print(f"❌ Le dossier {data_dir} n'existe pas")
        return False
    
    print(f"📁 Dossier de données: {data_dir}")
    
    # Charger et indexer les documents
    print("📄 Chargement et indexation des documents...")
    success = manager.load_and_index_documents(data_dir)
    
    if success:
        print("✅ Réindexation terminée avec succès!")
        
        # Afficher les informations de la collection
        info = manager.get_collection_info()
        print(f"📊 Informations de la collection:")
        print(f"   - Nombre de documents: {info.get('count', 'N/A')}")
        print(f"   - Taille des chunks: 500")
        print(f"   - Overlap: 100")
        
        return True
    else:
        print("❌ Échec de la réindexation")
        return False

if __name__ == "__main__":
    main() 