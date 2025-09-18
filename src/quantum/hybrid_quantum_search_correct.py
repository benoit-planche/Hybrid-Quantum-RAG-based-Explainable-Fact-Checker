#!/usr/bin/env python3
"""
Système hybride CORRECT combinant le système actuel et Grover corrigé
Permet de basculer entre les deux approches selon les besoins
"""

import os
import sys
import time
import logging
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum

# Ajouter les chemins nécessaires
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(os.path.dirname(current_dir), 'system')
sys.path.insert(0, system_dir)
sys.path.insert(0, current_dir)

from quantum_search import retrieve_top_k as classical_quantum_search
from grover_correct import correct_grover_retrieve_top_k
from performance_metrics import time_operation, time_operation_context

logger = logging.getLogger(__name__)

class SearchStrategy(Enum):
    """Stratégies de recherche disponibles"""
    CLASSICAL_QUANTUM = "classical_quantum"  # Système actuel
    GROVER_CORRECT = "grover_correct"        # Grover corrigé
    HYBRID_ADAPTIVE = "hybrid_adaptive"      # Hybride adaptatif
    GROVER_HYBRID = "grover_hybrid"          # Grover + quantum overlap

class CorrectHybridQuantumSearch:
    """
    Système de recherche hybride CORRECT combinant différentes stratégies quantiques
    """
    
    def __init__(self, strategy: SearchStrategy = SearchStrategy.HYBRID_ADAPTIVE):
        """
        Initialiser le système hybride correct
        
        Args:
            strategy: Stratégie de recherche à utiliser
        """
        self.strategy = strategy
        self.performance_history = {
            'classical_quantum': [],
            'grover_correct': [],
            'grover_hybrid': []
        }
        
    def adaptive_strategy_selection(self, query_length: int, database_size: int) -> SearchStrategy:
        """
        Sélectionner automatiquement la meilleure stratégie selon le contexte
        
        Args:
            query_length: Longueur de la requête
            database_size: Taille de la base de données
            
        Returns:
            Stratégie recommandée
        """
        # Règles d'adaptation basées sur l'historique et le contexte
        if database_size < 1000:
            # Petite base : système classique plus efficace
            return SearchStrategy.CLASSICAL_QUANTUM
        elif database_size > 10000:
            # Grande base : Grover corrigé plus avantageux
            return SearchStrategy.GROVER_CORRECT
        elif query_length > 100:
            # Requête complexe : hybride pour plus de précision
            return SearchStrategy.GROVER_HYBRID
        else:
            # Cas par défaut : hybride adaptatif
            return SearchStrategy.HYBRID_ADAPTIVE
    
    @time_operation("correct_hybrid_search_execution")
    def search(self, query_text: str, db_folder: str, k: int = 5, 
              n_qubits: int = 8, cassandra_manager=None, 
              strategy: Optional[SearchStrategy] = None) -> List[Tuple[float, str, str]]:
        """
        Exécuter la recherche selon la stratégie sélectionnée
        
        Args:
            query_text: Texte de la requête
            db_folder: Dossier des circuits QASM
            k: Nombre de résultats
            n_qubits: Nombre de qubits
            cassandra_manager: Gestionnaire Cassandra
            strategy: Stratégie à utiliser (optionnel)
            
        Returns:
            Liste des résultats (score, qasm_path, chunk_id)
        """
        # Sélectionner la stratégie
        if strategy is None:
            if self.strategy == SearchStrategy.HYBRID_ADAPTIVE:
                # Estimer la taille de la base
                try:
                    collection_info = cassandra_manager.get_collection_info()
                    db_size = collection_info.get('document_count', 5000)
                except:
                    db_size = 5000
                
                strategy = self.adaptive_strategy_selection(len(query_text), db_size)
            else:
                strategy = self.strategy
        
        logger.info(f"🔍 Stratégie sélectionnée: {strategy.value}")
        
        # Exécuter selon la stratégie
        start_time = time.time()
        
        try:
            if strategy == SearchStrategy.CLASSICAL_QUANTUM:
                results = self._execute_classical_quantum(query_text, db_folder, k, n_qubits, cassandra_manager)
            elif strategy == SearchStrategy.GROVER_CORRECT:
                results = self._execute_grover_correct(query_text, db_folder, k, n_qubits, cassandra_manager)
            elif strategy == SearchStrategy.GROVER_HYBRID:
                results = self._execute_grover_hybrid(query_text, db_folder, k, n_qubits, cassandra_manager)
            else:
                results = self._execute_hybrid_adaptive(query_text, db_folder, k, n_qubits, cassandra_manager)
            
            duration = time.time() - start_time
            
            # Enregistrer les performances
            self.performance_history[strategy.value].append({
                'duration': duration,
                'results_count': len(results),
                'query_length': len(query_text)
            })
            
            logger.info(f"✅ Recherche terminée en {duration:.2f}s avec {len(results)} résultats")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur dans la recherche {strategy.value}: {e}")
            # Fallback vers le système classique
            logger.info("🔄 Fallback vers le système classique")
            return self._execute_classical_quantum(query_text, db_folder, k, n_qubits, cassandra_manager)
    
    def _execute_classical_quantum(self, query_text: str, db_folder: str, k: int, 
                                 n_qubits: int, cassandra_manager) -> List[Tuple[float, str, str]]:
        """Exécuter le système classique quantique"""
        logger.info("🔄 Exécution système classique quantique")
        return classical_quantum_search(query_text, db_folder, k, n_qubits, cassandra_manager)
    
    def _execute_grover_correct(self, query_text: str, db_folder: str, k: int, 
                              n_qubits: int, cassandra_manager) -> List[Tuple[float, str, str]]:
        """Exécuter Grover corrigé"""
        logger.info("🚀 Exécution Grover CORRECT")
        return correct_grover_retrieve_top_k(query_text, db_folder, k, n_qubits, cassandra_manager)
    
    def _execute_grover_hybrid(self, query_text: str, db_folder: str, k: int, 
                             n_qubits: int, cassandra_manager) -> List[Tuple[float, str, str]]:
        """Exécuter Grover + quantum overlap"""
        logger.info("⚡ Exécution Grover hybride CORRECT")
        
        # Phase 1: Grover corrigé pour la sélection rapide
        with time_operation_context("grover_correct_candidate_selection"):
            grover_results = correct_grover_retrieve_top_k(query_text, db_folder, k*3, n_qubits, cassandra_manager)
        
        if not grover_results:
            return []
        
        # Phase 2: Quantum overlap sur les candidats sélectionnés
        with time_operation_context("quantum_overlap_refinement"):
            # Pour l'instant, on retourne les résultats Grover
            # TODO: Ajouter une étape de raffinement quantique
            return grover_results[:k]
    
    def _execute_hybrid_adaptive(self, query_text: str, db_folder: str, k: int, 
                               n_qubits: int, cassandra_manager) -> List[Tuple[float, str, str]]:
        """Exécuter la stratégie hybride adaptative"""
        logger.info("🎯 Exécution hybride adaptative CORRECTE")
        
        # Combiner les résultats des deux systèmes
        with time_operation_context("parallel_search"):
            # Recherche classique
            classical_results = self._execute_classical_quantum(query_text, db_folder, k, n_qubits, cassandra_manager)
            
            # Recherche Grover corrigée
            grover_results = self._execute_grover_correct(query_text, db_folder, k, n_qubits, cassandra_manager)
        
        # Fusionner et dédupliquer les résultats
        return self._merge_results(classical_results, grover_results, k)
    
    def _merge_results(self, classical_results: List[Tuple[float, str, str]], 
                      grover_results: List[Tuple[float, str, str]], k: int) -> List[Tuple[float, str, str]]:
        """
        Fusionner les résultats des deux systèmes
        
        Args:
            classical_results: Résultats du système classique
            grover_results: Résultats de Grover corrigé
            k: Nombre de résultats finaux
            
        Returns:
            Liste fusionnée et dédupliquée
        """
        # Créer un dictionnaire pour dédupliquer
        merged = {}
        
        # Ajouter les résultats classiques avec poids 1.0
        for score, path, chunk_id in classical_results:
            if chunk_id not in merged or merged[chunk_id][0] < score:
                merged[chunk_id] = (score, path, chunk_id)
        
        # Ajouter les résultats Grover avec poids 0.9 (légèrement inférieur pour équilibrer)
        for score, path, chunk_id in grover_results:
            weighted_score = score * 0.9
            if chunk_id not in merged or merged[chunk_id][0] < weighted_score:
                merged[chunk_id] = (weighted_score, path, chunk_id)
        
        # Trier et retourner les k meilleurs
        sorted_results = sorted(merged.values(), key=lambda x: x[0], reverse=True)
        return sorted_results[:k]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de performance"""
        stats = {}
        
        for strategy, history in self.performance_history.items():
            if history:
                durations = [h['duration'] for h in history]
                result_counts = [h['results_count'] for h in history]
                
                stats[strategy] = {
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'avg_results': sum(result_counts) / len(result_counts),
                    'total_queries': len(history)
                }
        
        return stats
    
    def optimize_strategy(self) -> SearchStrategy:
        """
        Optimiser la stratégie basée sur l'historique de performance
        
        Returns:
            Stratégie optimale recommandée
        """
        stats = self.get_performance_stats()
        
        if not stats:
            return SearchStrategy.HYBRID_ADAPTIVE
        
        # Trouver la stratégie la plus rapide
        fastest_strategy = min(stats.keys(), 
                             key=lambda s: stats[s]['avg_duration'])
        
        logger.info(f"🎯 Stratégie optimale recommandée: {fastest_strategy}")
        return SearchStrategy(fastest_strategy)

# Interface de compatibilité pour l'API existante
def correct_hybrid_retrieve_top_k(query_text: str, db_folder: str, k: int = 5, 
                                 n_qubits: int = 8, cassandra_manager=None,
                                 strategy: str = "hybrid_adaptive") -> List[Tuple[float, str, str]]:
    """
    Interface de compatibilité CORRECTE pour l'API existante
    
    Args:
        query_text: Texte de la requête
        db_folder: Dossier des circuits QASM
        k: Nombre de résultats
        n_qubits: Nombre de qubits
        cassandra_manager: Gestionnaire Cassandra
        strategy: Stratégie à utiliser
        
    Returns:
        Liste des résultats (score, qasm_path, chunk_id)
    """
    try:
        search_strategy = SearchStrategy(strategy)
    except ValueError:
        logger.warning(f"Stratégie inconnue '{strategy}', utilisation de 'hybrid_adaptive'")
        search_strategy = SearchStrategy.HYBRID_ADAPTIVE
    
    hybrid_search = CorrectHybridQuantumSearch(strategy=search_strategy)
    return hybrid_search.search(query_text, db_folder, k, n_qubits, cassandra_manager)
