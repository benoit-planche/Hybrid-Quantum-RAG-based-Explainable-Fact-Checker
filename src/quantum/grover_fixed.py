#!/usr/bin/env python3
"""
Version CORRIGÉE de Grover qui utilise les similarités originales
Sans normalisation qui casse le seuil
"""

import os
import numpy as np
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import MCMT
from typing import List, Dict, Any, Tuple, Optional
import logging
from performance_metrics import time_operation, time_operation_context

logger = logging.getLogger(__name__)

class FixedGroverSearch:
    """
    Version CORRIGÉE de Grover qui utilise les similarités originales
    """
    
    def __init__(self, n_qubits: int = 8, threshold: float = 0.4):
        """
        Initialiser le système de recherche Grover corrigé
        
        Args:
            n_qubits: Nombre de qubits pour l'encodage
            threshold: Seuil de similarité pour marquer un document comme pertinent
        """
        self.n_qubits = n_qubits
        self.threshold = threshold
        self.backend = Aer.get_backend('statevector_simulator')
        self.shots = 1024
        
    def calculate_original_similarities(self, query_embedding: np.ndarray, 
                                      document_embeddings: List[np.ndarray]) -> np.ndarray:
        """
        Calculer les similarités originales SANS normalisation
        
        Args:
            query_embedding: Embedding de la requête
            document_embeddings: Liste des embeddings des documents
            
        Returns:
            Vecteur des similarités originales
        """
        n_docs = len(document_embeddings)
        similarities = np.zeros(n_docs)
        
        # Calculer les similarités cosinus ORIGINALES
        for i, doc_embedding in enumerate(document_embeddings):
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities[i] = similarity  # Garder les valeurs originales (positives et négatives)
        
        logger.info(f"📊 Similarités calculées: min={similarities.min():.3f}, max={similarities.max():.3f}")
        return similarities
    
    @time_operation("grover_oracle_creation")
    def create_correct_oracle(self, similarities: np.ndarray, 
                            threshold: float) -> QuantumCircuit:
        """
        Créer un oracle CORRECT pour Grover basé sur les similarités originales
        
        Args:
            similarities: Vecteur des similarités originales
            threshold: Seuil de similarité
            
        Returns:
            Circuit quantique oracle correct
        """
        n_docs = len(similarities)
        n_qubits_needed = int(np.ceil(np.log2(n_docs)))
        
        # Créer le circuit oracle
        oracle = QuantumCircuit(n_qubits_needed + 1)  # +1 pour le qubit auxiliaire
        
        # Identifier les documents pertinents avec les similarités originales
        relevant_docs = [i for i, sim in enumerate(similarities) if sim > threshold]
        
        logger.info(f"🔍 Oracle: {len(relevant_docs)} documents pertinents sur {n_docs} (seuil: {threshold})")
        
        # Marquer chaque document pertinent
        for doc_index in relevant_docs:
            # Encoder l'index en binaire
            binary_index = format(doc_index, f'0{n_qubits_needed}b')
            
            # Appliquer les portes X pour les qubits à 0
            for j, bit in enumerate(binary_index):
                if bit == '0':
                    oracle.x(j)
            
            # Appliquer la porte multi-contrôlée pour marquer l'état
            if n_qubits_needed == 1:
                oracle.cx(0, n_qubits_needed)
            elif n_qubits_needed == 2:
                oracle.ccx(0, 1, n_qubits_needed)
            else:
                # Utiliser MCMT pour n > 2 qubits
                oracle.append(MCMT('x', n_qubits_needed, 1), 
                            list(range(n_qubits_needed)) + [n_qubits_needed])
            
            # Restaurer les qubits
            for j, bit in enumerate(binary_index):
                if bit == '0':
                    oracle.x(j)
        
        return oracle
    
    @time_operation("grover_diffusion_operator")
    def create_correct_diffusion(self, n_qubits: int) -> QuantumCircuit:
        """
        Créer l'opérateur de diffusion CORRECT de Grover
        
        Args:
            n_qubits: Nombre de qubits
            
        Returns:
            Circuit quantique de diffusion correct
        """
        diffusion = QuantumCircuit(n_qubits)
        
        # Appliquer H^⊗n
        diffusion.h(range(n_qubits))
        
        # Appliquer |0⟩⟨0| - I
        diffusion.x(range(n_qubits))
        
        if n_qubits == 1:
            diffusion.z(0)
        elif n_qubits == 2:
            diffusion.cz(0, 1)
        else:
            # Pour n > 2, utiliser MCMT pour la porte multi-contrôlée
            diffusion.append(MCMT('z', n_qubits - 1, 1), range(n_qubits))
        
        diffusion.x(range(n_qubits))
        
        # Appliquer H^⊗n
        diffusion.h(range(n_qubits))
        
        return diffusion
    
    @time_operation("grover_adaptive_iterations")
    def adaptive_grover_search(self, similarities: np.ndarray, 
                             threshold: float) -> List[Tuple[int, float]]:
        """
        Recherche Grover adaptative avec similarités originales
        
        Args:
            similarities: Vecteur des similarités originales
            threshold: Seuil de similarité
            
        Returns:
            Liste des documents trouvés (index, similarité)
        """
        n_docs = len(similarities)
        n_qubits_needed = int(np.ceil(np.log2(n_docs)))
        
        # Compter les solutions avec les similarités originales
        num_solutions = sum(1 for sim in similarities if sim > threshold)
        
        if num_solutions == 0:
            logger.warning(f"Aucun document ne dépasse le seuil de similarité {threshold}")
            return []
        
        logger.info(f"🔍 Grover adaptatif: {n_docs} documents, {num_solutions} solutions, seuil {threshold}")
        
        # Créer l'oracle et la diffusion
        oracle = self.create_correct_oracle(similarities, threshold)
        diffusion = self.create_correct_diffusion(n_qubits_needed)
        

        # Stratégie adaptative optimisée: limiter à 5 itérations max
        max_iterations = min(5, int(np.sqrt(n_docs)))
        best_results = []
        best_confidence = 0
        
        # Tester seulement quelques itérations pour la rapidité
        for iterations in range(1, max_iterations + 1):
            results = self._execute_grover_iterations(
                oracle, diffusion, n_qubits_needed, iterations, similarities
            )
            
            if results:
                # Calculer la confiance basée sur la cohérence des résultats
                confidence = self._calculate_confidence(results, similarities, threshold)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_results = results
                
                logger.info(f"   Itérations {iterations}: {len(results)} résultats, confiance {confidence:.3f}")
        
        logger.info(f"✅ Meilleur résultat: {len(best_results)} documents, confiance {best_confidence:.3f}")
        return best_results
    
    def _execute_grover_iterations(self, oracle: QuantumCircuit, diffusion: QuantumCircuit,
                                 n_qubits: int, iterations: int, 
                                 similarities: np.ndarray) -> List[Tuple[int, float]]:
        """
        Exécuter Grover avec un nombre spécifique d'itérations
        
        Args:
            oracle: Circuit oracle
            diffusion: Circuit de diffusion
            n_qubits: Nombre de qubits
            iterations: Nombre d'itérations
            similarities: Vecteur des similarités originales
            
        Returns:
            Liste des résultats (index, similarité)
        """
        # Créer le circuit principal
        grover_circuit = QuantumCircuit(n_qubits + 1, n_qubits)
        
        # Initialiser la superposition uniforme
        grover_circuit.h(range(n_qubits))
        grover_circuit.x(n_qubits)  # Qubit auxiliaire
        grover_circuit.h(n_qubits)
        
        # Appliquer les itérations de Grover
        for _ in range(iterations):
            # Appliquer l'oracle
            grover_circuit.append(oracle, range(n_qubits + 1))
            
            # Appliquer la diffusion
            grover_circuit.append(diffusion, range(n_qubits))
        
        # Mesurer les qubits
        grover_circuit.measure(range(n_qubits), range(n_qubits))
        
        # Exécuter le circuit
        try:
            transpiled_circuit = transpile(grover_circuit, self.backend)
            job = self.backend.run(transpiled_circuit, shots=self.shots)
            result = job.result()
            counts = result.get_counts()
            
            # Analyser les résultats
            results = []
            n_docs = len(similarities)
            
            for state, count in counts.items():
                doc_index = int(state, 2)
                if doc_index < n_docs:
                    similarity = similarities[doc_index]
                    # Ponderer par le nombre de mesures
                    weighted_similarity = similarity * (count / self.shots)
                    results.append((doc_index, weighted_similarity, count))
            
            # Trier par similarité pondérée et retourner les meilleurs
            results.sort(key=lambda x: x[1], reverse=True)
            return [(idx, sim) for idx, sim, _ in results[:10]]  # Top 10
            
        except Exception as e:
            logger.error(f"Erreur dans l'exécution Grover: {e}")
            return []
    
    def _calculate_confidence(self, results: List[Tuple[int, float]], 
                            similarities: np.ndarray, threshold: float) -> float:
        """
        Calculer la confiance des résultats Grover
        
        Args:
            results: Résultats de Grover
            similarities: Vecteur des similarités originales
            threshold: Seuil de similarité
            
        Returns:
            Score de confiance entre 0 et 1
        """
        if not results:
            return 0.0
        
        # Calculer la cohérence: combien de résultats sont au-dessus du seuil
        above_threshold = sum(1 for idx, sim in results if similarities[idx] > threshold)
        coherence = above_threshold / len(results)
        
        # Calculer la qualité moyenne des résultats
        avg_quality = np.mean([similarities[idx] for idx, _ in results])
        
        # Combiner cohérence et qualité
        confidence = (coherence * 0.7) + (avg_quality * 0.3)
        
        return min(1.0, confidence)
    
    @time_operation("grover_document_search")
    def search_documents(self, query_embedding: np.ndarray, 
                        document_embeddings: List[np.ndarray],
                        max_results: int = 10) -> List[Tuple[int, float]]:
        """
        Recherche principale de documents avec Grover corrigé
        
        Args:
            query_embedding: Embedding de la requête
            document_embeddings: Liste des embeddings des documents
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des documents trouvés (index, similarité)
        """
        if not document_embeddings:
            return []
        
        logger.info(f"🚀 Recherche Grover corrigée sur {len(document_embeddings)} documents")
        
        # Calculer les similarités originales
        similarities = self.calculate_original_similarities(query_embedding, document_embeddings)
        
        # Exécuter la recherche Grover adaptative
        results = self.adaptive_grover_search(similarities, self.threshold)
        
        # Retourner les meilleurs résultats
        return results[:max_results]
    
    @time_operation("grover_hybrid_integration")
    def hybrid_grover_search(self, query_text: str, cassandra_manager, 
                           db_folder: str, k: int = 5) -> List[Tuple[float, str, str]]:
        """
        Recherche hybride CORRIGÉE combinant Grover et le système existant
        
        Args:
            query_text: Texte de la requête
            cassandra_manager: Gestionnaire Cassandra
            db_folder: Dossier contenant les circuits QASM
            k: Nombre de résultats à retourner
            
        Returns:
            Liste des résultats (score, qasm_path, chunk_id)
        """
        logger.info(f"🚀 Recherche hybride Grover CORRIGÉE pour: '{query_text[:50]}...'")
        
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
        
        # 3. Exécuter la recherche Grover CORRIGÉE
        with time_operation_context("grover_search"):
            grover_results = self.search_documents(
                query_embedding, 
                document_embeddings, 
                max_results=min(100, len(document_embeddings))
            )
        
        logger.info(f"🔍 Grover CORRIGÉ trouvé {len(grover_results)} documents pertinents")
        
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
        
        logger.info(f"✅ {len(qasm_results)} circuits QASM trouvés pour Grover CORRIGÉ")
        return qasm_results[:k]

# Fonction de compatibilité avec l'API existante
def fixed_grover_retrieve_top_k(query_text: str, db_folder: str, k: int = 5, 
                               n_qubits: int = 8, cassandra_manager=None) -> List[Tuple[float, str, str]]:
    """
    Interface de compatibilité CORRIGÉE pour remplacer retrieve_top_k avec Grover
    
    Args:
        query_text: Texte de la requête
        db_folder: Dossier des circuits QASM
        k: Nombre de résultats
        n_qubits: Nombre de qubits
        cassandra_manager: Gestionnaire Cassandra
        
    Returns:
        Liste des résultats (score, qasm_path, chunk_id)
    """
    if cassandra_manager is None:
        logger.error("❌ Cassandra manager requis pour Grover")
        return []
    
    grover_search = FixedGroverSearch(n_qubits=n_qubits)
    return grover_search.hybrid_grover_search(query_text, cassandra_manager, db_folder, k)
