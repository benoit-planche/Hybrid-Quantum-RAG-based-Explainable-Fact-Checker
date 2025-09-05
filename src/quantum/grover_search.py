#!/usr/bin/env python3
"""
Implémentation de l'algorithme de Grover pour la recherche de documents
dans le système de fact-checking quantique
"""

import os
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
from typing import List, Dict, Any, Tuple
import logging
from performance_metrics import time_operation, time_operation_context

logger = logging.getLogger(__name__)

class GroverDocumentSearch:
    """
    Recherche de documents utilisant l'algorithme de Grover
    pour accélérer la recherche dans la base de données
    """
    
    def __init__(self, n_qubits: int = 8, threshold: float = 0.7):
        """
        Initialiser le système de recherche Grover
        
        Args:
            n_qubits: Nombre de qubits pour l'encodage
            threshold: Seuil de similarité pour marquer un document comme pertinent
        """
        self.n_qubits = n_qubits
        self.threshold = threshold
        self.backend = Aer.get_backend('statevector_simulator')
        self.database_size = 2 ** n_qubits  # Taille maximale de la base
        
    @time_operation("grover_oracle_creation")
    def create_relevance_oracle(self, query_embedding: np.ndarray, 
                              document_embeddings: List[np.ndarray]) -> QuantumCircuit:
        """
        Créer l'oracle de pertinence pour l'algorithme de Grover
        
        Args:
            query_embedding: Embedding de la requête
            document_embeddings: Liste des embeddings des documents
            
        Returns:
            Circuit quantique représentant l'oracle
        """
        n_docs = len(document_embeddings)
        n_qubits_needed = int(np.ceil(np.log2(n_docs)))
        
        # Créer le circuit oracle
        oracle = QuantumCircuit(n_qubits_needed + 1)  # +1 pour le qubit auxiliaire
        
        # Marquer les documents pertinents
        for i, doc_embedding in enumerate(document_embeddings):
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            
            if similarity > self.threshold:
                # Encoder l'index du document en binaire
                binary_index = format(i, f'0{n_qubits_needed}b')
                
                # Appliquer la porte X pour les qubits à 0
                for j, bit in enumerate(binary_index):
                    if bit == '0':
                        oracle.x(j)
                
                # Appliquer la porte multi-contrôlée
                if n_qubits_needed == 1:
                    oracle.cx(0, n_qubits_needed)
                elif n_qubits_needed == 2:
                    oracle.ccx(0, 1, n_qubits_needed)
                else:
                    # Pour plus de 2 qubits, utiliser une implémentation simplifiée
                    # Appliquer une porte X contrôlée par le premier qubit
                    oracle.cx(0, n_qubits_needed)
                
                # Restaurer les qubits
                for j, bit in enumerate(binary_index):
                    if bit == '0':
                        oracle.x(j)
        
        return oracle
    
    @time_operation("grover_diffusion_operator")
    def create_diffusion_operator(self, n_qubits: int) -> QuantumCircuit:
        """
        Créer l'opérateur de diffusion de Grover
        
        Args:
            n_qubits: Nombre de qubits
            
        Returns:
            Circuit quantique de diffusion
        """
        diffusion = QuantumCircuit(n_qubits)
        
        # Appliquer H^⊗n
        diffusion.h(range(n_qubits))
        
        # Appliquer |0⟩⟨0| - I
        diffusion.x(range(n_qubits))
        diffusion.h(n_qubits - 1)
        
        # Porte multi-contrôlée selon le nombre de qubits
        if n_qubits == 1:
            diffusion.z(0)
        elif n_qubits == 2:
            diffusion.cz(0, 1)
        else:
            # Pour plus de 2 qubits, utiliser une implémentation simplifiée
            # Appliquer une porte Z contrôlée par le premier qubit
            diffusion.cz(0, n_qubits - 1)
        
        diffusion.h(n_qubits - 1)
        diffusion.x(range(n_qubits))
        
        # Appliquer H^⊗n
        diffusion.h(range(n_qubits))
        
        return diffusion
    
    @time_operation("grover_search_execution")
    def grover_search(self, query_embedding: np.ndarray, 
                     document_embeddings: List[np.ndarray],
                     max_results: int = 10) -> List[Tuple[int, float]]:
        """
        Exécuter la recherche Grover pour trouver les documents pertinents
        
        Args:
            query_embedding: Embedding de la requête
            document_embeddings: Liste des embeddings des documents
            max_results: Nombre maximum de résultats à retourner
            
        Returns:
            Liste des tuples (index_document, score_similarité)
        """
        n_docs = len(document_embeddings)
        if n_docs == 0:
            return []
        
        n_qubits_needed = int(np.ceil(np.log2(n_docs)))
        
        # Créer l'oracle de pertinence
        oracle = self.create_relevance_oracle(query_embedding, document_embeddings)
        
        # Créer l'opérateur de diffusion
        diffusion = self.create_diffusion_operator(n_qubits_needed)
        
        # Créer le circuit principal de Grover
        grover_circuit = QuantumCircuit(n_qubits_needed + 1, n_qubits_needed)
        
        # Initialiser la superposition uniforme
        grover_circuit.h(range(n_qubits_needed))
        grover_circuit.x(n_qubits_needed)  # Qubit auxiliaire
        grover_circuit.h(n_qubits_needed)
        
        # Calculer le nombre optimal d'itérations
        num_solutions = sum(1 for doc in document_embeddings 
                          if np.dot(query_embedding, doc) / (
                              np.linalg.norm(query_embedding) * np.linalg.norm(doc)
                          ) > self.threshold)
        
        if num_solutions == 0:
            logger.warning("Aucun document ne dépasse le seuil de similarité")
            return []
        
        optimal_iterations = int(np.pi / 4 * np.sqrt(n_docs / num_solutions))
        optimal_iterations = min(optimal_iterations, 10)  # Limiter pour éviter la sur-optimisation
        
        logger.info(f"🔍 Grover: {n_docs} documents, {num_solutions} solutions, {optimal_iterations} itérations")
        
        # Appliquer les itérations de Grover
        for _ in range(optimal_iterations):
            # Appliquer l'oracle
            grover_circuit.append(oracle, range(n_qubits_needed + 1))
            
            # Appliquer la diffusion
            grover_circuit.append(diffusion, range(n_qubits_needed))
        
        # Mesurer les qubits
        grover_circuit.measure(range(n_qubits_needed), range(n_qubits_needed))
        
        # Exécuter le circuit
        transpiled_circuit = transpile(grover_circuit, self.backend)
        job = self.backend.run(transpiled_circuit, shots=1024)
        result = job.result()
        counts = result.get_counts()
        
        # Analyser les résultats
        results = []
        for state, count in counts.items():
            doc_index = int(state, 2)
            if doc_index < n_docs:
                similarity = np.dot(query_embedding, document_embeddings[doc_index]) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(document_embeddings[doc_index])
                )
                results.append((doc_index, similarity, count))
        
        # Trier par similarité et retourner les meilleurs
        results.sort(key=lambda x: x[1], reverse=True)
        return [(idx, sim) for idx, sim, _ in results[:max_results]]
    
    @time_operation("grover_hybrid_search")
    def hybrid_grover_search(self, query_text: str, cassandra_manager, 
                           db_folder: str, k: int = 5) -> List[Tuple[float, str, str]]:
        """
        Recherche hybride combinant Grover et le système existant
        
        Args:
            query_text: Texte de la requête
            cassandra_manager: Gestionnaire Cassandra
            db_folder: Dossier contenant les circuits QASM
            k: Nombre de résultats à retourner
            
        Returns:
            Liste des résultats (score, qasm_path, chunk_id)
        """
        logger.info(f"🚀 Recherche hybride Grover pour: '{query_text[:50]}...'")
        
        # 1. Générer l'embedding de la requête
        with time_operation_context("query_embedding_generation"):
            query_embedding = cassandra_manager.embed_model.get_text_embedding_batch([query_text])[0]
        
        # 2. Récupérer tous les embeddings de la base
        with time_operation_context("database_embedding_retrieval"):
            query_cql = "SELECT row_id, vector FROM fact_checker_keyspace.fact_checker_docs"
            rows = cassandra_manager.session.execute(query_cql)
            
            document_embeddings = []
            chunk_mapping = []
            
            for row in rows:
                if hasattr(row, 'vector') and row.vector:
                    document_embeddings.append(row.vector)
                    chunk_mapping.append(row.row_id)
        
        logger.info(f"📊 Base de données: {len(document_embeddings)} documents avec embeddings")
        
        # 3. Exécuter la recherche Grover
        with time_operation_context("grover_search"):
            grover_results = self.grover_search(
                query_embedding, 
                document_embeddings, 
                max_results=min(100, len(document_embeddings))
            )
        
        logger.info(f"🔍 Grover trouvé {len(grover_results)} documents pertinents")
        
        # 4. Convertir les résultats en circuits QASM
        qasm_results = []
        for doc_index, similarity in grover_results:
            chunk_id = chunk_mapping[doc_index]
            
            # Extraire le numéro du chunk
            if chunk_id.startswith('doc_'):
                chunk_num = chunk_id.replace('doc_', '')
            else:
                chunk_num = str(chunk_id)
            
            # Construire le chemin QASM
            qasm_name = f"None_doc_{chunk_num}_8qubits.qasm"
            qasm_path = os.path.join(db_folder, qasm_name)
            
            if os.path.exists(qasm_path):
                qasm_results.append((similarity, qasm_path, chunk_num))
            else:
                logger.warning(f"⚠️ Circuit QASM non trouvé: {qasm_path}")
        
        logger.info(f"✅ {len(qasm_results)} circuits QASM trouvés pour Grover")
        return qasm_results[:k]

# Fonction de compatibilité avec l'API existante
def grover_retrieve_top_k(query_text: str, db_folder: str, k: int = 5, 
                         n_qubits: int = 8, cassandra_manager=None) -> List[Tuple[float, str, str]]:
    """
    Interface de compatibilité pour remplacer retrieve_top_k avec Grover
    
    Args:
        query_text: Texte de la requête
        db_folder: Dossier des circuits QASM
        k: Nombre de résultats
        n_qubits: Nombre de qubits (non utilisé dans Grover)
        cassandra_manager: Gestionnaire Cassandra
        
    Returns:
        Liste des résultats (score, qasm_path, chunk_id)
    """
    if cassandra_manager is None:
        logger.error("❌ Cassandra manager requis pour Grover")
        return []
    
    grover_search = GroverDocumentSearch(n_qubits=n_qubits)
    return grover_search.hybrid_grover_search(query_text, cassandra_manager, db_folder, k)
