"""
Gestionnaire Cassandra Vector Store pour le fact-checker avec MMR
"""

import os
from typing import List, Dict, Any
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.cassandra import CassandraVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings
from ollama_utils import SimpleTextSplitter
from pdf_loader import PDFDocumentLoader
import cassio
from cassandra.cluster import Cluster

class CassandraVectorStoreManager:
    """Gestionnaire pour Cassandra Vector Store avec MMR intégré"""
    
    def __init__(self, table_name="fact_checker_docs", embedding_model="llama2:7b", keyspace="fact_checker_keyspace"):
        """
        Initialiser Cassandra Vector Store
        
        Args:
            table_name: Nom de la table Cassandra
            embedding_model: Modèle Ollama pour les embeddings
        """
        self.table_name = table_name
        self.keyspace = keyspace
        self.embedding_model = embedding_model
        
        # Initialiser la session Cassandra
        self._init_cassandra_session()
        
        # Initialiser les embeddings Ollama
        self.embed_model = OllamaEmbedding(model_name=embedding_model)
        
        # Initialiser le LLM Ollama
        self.llm = Ollama(model=embedding_model, request_timeout=120.0)
        
        # Pas besoin de settings pour l'instant
        self.settings = None
        
        # Initialiser Cassandra Vector Store
        self.vector_store = CassandraVectorStore(
            table=table_name,
            embedding_dimension=4096  # Dimension des embeddings Ollama llama2:7b
        )
        
        # Créer le storage context
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # Initialiser l'index (sera None si pas de documents)
        self.index = None
        self._load_index()
        
        print(f"🔧 Modèle d'embedding: {embedding_model}")
        print(f"📊 Table Cassandra: {table_name}")
    
    def _init_cassandra_session(self):
        """Initialiser la session Cassandra"""
        try:
            # Créer la session Cassandra
            cluster = Cluster(['localhost'], port=9042)
            self.session = cluster.connect()
            
            # Configurer cassio avec la session
            cassio.init(
                session=self.session,
                keyspace=self.keyspace
            )
            
            # Créer le keyspace s'il n'existe pas
            self.session.execute("""
                CREATE KEYSPACE IF NOT EXISTS fact_checker_keyspace 
                WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
            """)
            
            print("✅ Session Cassandra initialisée")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation Cassandra: {e}")
            raise
    
    def _load_index(self):
        """Charger l'index existant si des documents existent"""
        try:
            # Essayer de charger l'index existant avec le bon modèle d'embedding
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store,
                embed_model=self.embed_model
            )
            print(f"✅ Index Cassandra chargé")
        except Exception as e:
            print(f"ℹ️ Pas d'index existant trouvé: {e}")
            self.index = None
    
    def _reload_index(self):
        """Recharger l'index après modification"""
        try:
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store,
                embed_model=self.embed_model
            )
            print(f"✅ Index Cassandra rechargé")
        except Exception as e:
            print(f"❌ Erreur lors du rechargement de l'index: {e}")
            self.index = None
    
    def _add_text_to_body_blob(self, texts, ids):
        """Ajouter manuellement le texte dans body_blob"""
        print("📝 Ajout du texte dans body_blob...")
        for i, (text, node_id) in enumerate(zip(texts, ids)):
            try:
                # Extraire partition_id et row_id du node_id
                partition_id = "None"  # Valeur par défaut
                row_id = node_id
                
                # Insérer le texte dans body_blob
                update_query = f"""
                    UPDATE {self.keyspace}.{self.table_name} 
                    SET body_blob = %s 
                    WHERE partition_id = %s AND row_id = %s
                """
                self.session.execute(update_query, (text, partition_id, row_id))
                
            except Exception as e:
                print(f"⚠️ Erreur lors de l'ajout du texte pour {node_id}: {e}")
    
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
            splitter = SimpleTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            print(f"✂️ {len(chunks)} chunks créés")
            
            # Préparer les données pour Cassandra
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
            
            # Générer les embeddings avec LlamaIndex OllamaEmbeddings
            print("🔄 Génération des embeddings...")
            embeddings_list = self.embed_model.get_text_embedding_batch(
                texts, 
                show_progress=True
            )
            
            # Créer des objets Node pour Cassandra
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
            
            # Ajouter les nodes à Cassandra
            self.vector_store.add(nodes)
            
            # Ajouter manuellement le texte dans body_blob
            self._add_text_to_body_blob(texts, ids)
            
            # Recharger l'index après ajout
            self._reload_index()
            
            print(f"✅ {len(chunks)} chunks indexés dans Cassandra")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'indexation: {e}")
            return False
    
    def load_and_index_specific_documents(self, data_dir: str, pdf_list: List[str]) -> bool:
        """
        Charger et indexer seulement les documents PDF spécifiés
        
        Args:
            data_dir: Dossier contenant les PDFs
            pdf_list: Liste des noms de fichiers PDF à indexer
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Charger seulement les documents PDF spécifiés
            documents = []
            for pdf_name in pdf_list:
                pdf_path = os.path.join(data_dir, pdf_name)
                if os.path.exists(pdf_path):
                    doc = PDFDocumentLoader.load_single_file(pdf_path)
                    if doc:
                        documents.append(doc)
                else:
                    print(f"⚠️ Fichier non trouvé: {pdf_path}")
            
            if not documents:
                print("❌ Aucun document PDF valide trouvé")
                return False
            
            print(f"📄 {len(documents)} documents spécifiques chargés")
            
            # Splitter les documents
            splitter = SimpleTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            print(f"✂️ {len(chunks)} chunks créés")
            
            # Préparer les données pour Cassandra
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
            
            # Générer les embeddings avec LlamaIndex OllamaEmbeddings
            print("🔄 Génération des embeddings...")
            embeddings_list = self.embed_model.get_text_embedding_batch(
                texts, 
                show_progress=True
            )
            
            # Créer des objets Node pour Cassandra
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
            
            # Ajouter les nodes à Cassandra
            self.vector_store.add(nodes)
            
            # Ajouter manuellement le texte dans body_blob
            self._add_text_to_body_blob(texts, ids)
            
            # Recharger l'index après ajout
            self._reload_index()
            
            print(f"✅ {len(chunks)} chunks indexés dans Cassandra")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'indexation: {e}")
            return False
    
    def search_documents_mmr(self, query: str, n_results: int = 5, lambda_param: float = 0.5) -> List[Dict[str, Any]]:
        """
        Rechercher des documents avec MMR (Maximum Marginal Relevance)
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats à retourner
            lambda_param: Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)
            
        Returns:
            Liste des documents trouvés
        """
        try:
            if self.index is None:
                print("❌ Aucun index disponible")
                return []
            
            # Créer le retriever avec MMR
            retriever = self.index.as_retriever(
                similarity_top_k=n_results * 2,  # Plus de candidats pour MMR
                vector_store_query_mode="mmr",
                vector_store_kwargs={
                    "lambda_mult": lambda_param,
                    "k": n_results
                }
            )
            
            # Récupérer les nodes
            retrieved_nodes = retriever.retrieve(query)
            
            # Formater les résultats
            documents = []
            for i, node in enumerate(retrieved_nodes[:n_results]):
                doc = {
                    'content': node.text,
                    'metadata': node.metadata,
                    'score': node.score if hasattr(node, 'score') else 0.0,
                    'similarity': node.score if hasattr(node, 'score') else 0.0
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche MMR: {e}")
            return []
    
    def search_documents_simple(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche simple sans MMR pour comparaison
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats à retourner
            
        Returns:
            Liste des documents trouvés
        """
        try:
            if self.index is None:
                print("❌ Aucun index disponible")
                return []
            
            # Créer le retriever simple
            retriever = self.index.as_retriever(
                similarity_top_k=n_results
            )
            
            # Récupérer les nodes
            retrieved_nodes = retriever.retrieve(query)
            
            # Formater les résultats
            documents = []
            for i, node in enumerate(retrieved_nodes):
                doc = {
                    'content': node.text,
                    'metadata': node.metadata,
                    'score': node.score if hasattr(node, 'score') else 0.0,
                    'similarity': node.score if hasattr(node, 'score') else 0.0
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche simple: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur la table"""
        try:
            if self.index is None:
                return {
                    'name': self.table_name,
                    'document_count': 0,
                    'table_name': self.table_name
                }
            
            # Compter les documents en utilisant une requête directe
            try:
                count_query = f"SELECT COUNT(*) FROM fact_checker_keyspace.{self.table_name}"
                result = self.session.execute(count_query)
                document_count = result.one()[0]
                
                return {
                    'name': self.table_name,
                    'document_count': document_count,
                    'table_name': self.table_name,
                    'index_loaded': True
                }
            except Exception as count_error:
                # Fallback si la requête COUNT échoue
                print(f"⚠️ Impossible de compter les documents: {count_error}")
                return {
                    'name': self.table_name,
                    'document_count': 'N/A (Cassandra)',
                    'table_name': self.table_name,
                    'index_loaded': True
                }
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos: {e}")
            return {}
    
    def clear_collection(self):
        """Vider la table (recharger l'index)"""
        try:
            # Supprimer la table complètement pour forcer la recréation
            self.session.execute(f"DROP TABLE IF EXISTS fact_checker_keyspace.{self.table_name}")
            print("🗑️ Table Cassandra supprimée")
            
            # Recréer la table avec la bonne dimension
            self.vector_store = CassandraVectorStore(
                table=self.table_name,
                embedding_dimension=4096  # Dimension des embeddings Ollama llama2:7b
            )
            
            # Recréer le storage context
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Réinitialiser l'index
            self.index = None
            print("✅ Index Cassandra réinitialisé")
        except Exception as e:
            print(f"❌ Erreur lors de la réinitialisation: {e}")

    def get_all_chunks_with_embeddings(self):
        query = f"SELECT partition_id, row_id, vector FROM {self.keyspace}.{self.table_name};"
        rows = self.session.execute(query)
        results = []
        for row in rows:
            chunk_id = f"{row.partition_id}_{row.row_id}"
            results.append({
                "id": chunk_id,
                "embedding": row.vector
            })
        return results

def create_cassandra_manager(table_name="fact_checker_docs", keyspace="fact_checker_keyspace") -> CassandraVectorStoreManager:
    """Fonction utilitaire pour créer un gestionnaire Cassandra"""
    return CassandraVectorStoreManager(table_name=table_name, keyspace=keyspace)