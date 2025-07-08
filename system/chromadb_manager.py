"""
Gestionnaire ChromaDB pour le fact-checker
"""

import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from ollama_utils import OllamaEmbeddings, SimpleTextSplitter
from pdf_loader import PDFDocumentLoader

class ChromaDBManager:
    """Gestionnaire pour ChromaDB avec Ollama embeddings"""
    
    def __init__(self, persist_directory="./chroma_db", collection_name="fact_checker_docs", embedding_model="llama2:7b"):
        """
        Initialiser ChromaDB
        
        Args:
            persist_directory: Dossier de persistance des données
            collection_name: Nom de la collection ChromaDB
            embedding_model: Modèle Ollama pour les embeddings
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Créer le dossier de persistance s'il n'existe pas
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialiser ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialiser les embeddings Ollama avec le modèle spécifié
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        print(f"🔧 Modèle d'embedding: {embedding_model}")
        
        # Obtenir ou créer la collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Collection '{collection_name}' chargée")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Documents pour fact-checking"}
            )
            print(f"✅ Collection '{collection_name}' créée")
    
    def load_and_index_documents(self, data_dir: str) -> bool:
        """
        Charger et indexer les documents PDF
        
        Args:
            data_dir: Dossier contenant les PDFs
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Charger les documents PDF
            documents = PDFDocumentLoader.load_directory(data_dir)
            if not documents:
                print("❌ Aucun document PDF trouvé")
                return False
            
            print(f"📄 {len(documents)} documents chargés")
            
            # Splitter les documents
            splitter = SimpleTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(documents)
            print(f"✂️ {len(chunks)} chunks créés")
            
            # Préparer les données pour ChromaDB
            texts = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                texts.append(chunk['page_content'])
                metadatas.append({
                    'source': chunk['metadata'].get('source', 'Unknown'),
                    'file_path': chunk['metadata'].get('file_path', ''),
                    'chunk_id': i
                })
                ids.append(f"doc_{i}")
            
            # Générer les embeddings avec Ollama
            print("🔄 Génération des embeddings...")
            embeddings_list = self.embeddings.embed_documents(texts)
            
            # Ajouter à ChromaDB
            self.collection.add(
                documents=texts,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ {len(chunks)} chunks indexés dans ChromaDB")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'indexation: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Rechercher des documents similaires
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats à retourner
            
        Returns:
            Liste des documents trouvés
        """
        try:
            # Générer l'embedding de la requête
            query_embedding = self.embeddings.embed_query(query)
            
            # Rechercher dans ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Formater les résultats
            documents = []
            for i in range(len(results['documents'][0])):
                doc = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': max(0, 1 - results['distances'][0][i])  # S'assurer que similarité >= 0
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur la collection"""
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'document_count': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos: {e}")
            return {}
    
    def clear_collection(self):
        """Vider la collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Documents pour fact-checking"}
            )
            print("✅ Collection vidée")
        except Exception as e:
            print(f"❌ Erreur lors du vidage: {e}")

def create_chromadb_manager(persist_directory="./chroma_db") -> ChromaDBManager:
    """Fonction utilitaire pour créer un gestionnaire ChromaDB"""
    return ChromaDBManager(persist_directory=persist_directory) 