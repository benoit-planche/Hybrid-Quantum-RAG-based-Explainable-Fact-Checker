#!/usr/bin/env python3
"""
Évaluation stratégique des avantages quantiques spécifiques
Focus sur les points où le quantum peut vraiment briller
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Tuple
import json
from datetime import datetime
from collections import Counter
import random

sys.path.append('system')
sys.path.append('src/quantum')

from cassandra_manager import CassandraVectorStoreManager
from quantum_search import retrieve_top_k, quantum_overlap_similarity
from quantum_encoder import amplitude_encoding
import joblib

class StrategicQuantumEvaluator:
    def __init__(self):
        """Initialise l'évaluateur stratégique"""
        self.cassandra_manager = CassandraVectorStoreManager()
        self.pca = joblib.load("src/quantum/pca_model.pkl")
        
        # Requêtes stratégiques pour tester les avantages quantiques
        self.strategic_queries = {
            'diversity_test': [
                "climate change evidence",
                "global warming causes",
                "temperature increase",
                "greenhouse effect",
                "carbon dioxide impact"
            ],
            'robustness_test': [
                "Is Antarctica losing ice?",
                "Is Antarctica losing land ice?",
                "Is Antarctica losing ice mass?",
                "Is Antarctica losing ice due to global warming?",
                "Is Antarctica losing ice because of climate change?"
            ],
            'quantum_exploration_test': [
                "antarctica ice melting",
                "antarctica ice loss",
                "antarctica ice decline",
                "antarctica ice reduction",
                "antarctica ice decrease"
            ]
        }
    
    def calculate_mmr_score(self, results: List[Dict], lambda_param: float = 0.5) -> float:
        """Calcule le score MMR (Maximum Marginal Relevance)"""
        if len(results) < 2:
            return 0.0
        
        # Simuler MMR en calculant la diversité des résultats
        texts = [result.get('text', '') for result in results]
        
        # Calculer la similarité moyenne entre les résultats
        similarities = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                # Similarité simple basée sur les mots communs
                words_i = set(texts[i].lower().split())
                words_j = set(texts[j].lower().split())
                if words_i and words_j:
                    similarity = len(words_i.intersection(words_j)) / len(words_i.union(words_j))
                    similarities.append(similarity)
        
        if similarities:
            avg_similarity = np.mean(similarities)
            # MMR = 1 - similarité moyenne (plus c'est diversifié, plus MMR est élevé)
            return 1.0 - avg_similarity
        return 0.0
    
    def calculate_semantic_diversity(self, results: List[Dict]) -> float:
        """Calcule la diversité sémantique des résultats"""
        if not results:
            return 0.0
        
        # Extraire les mots-clés uniques de chaque résultat
        all_keywords = set()
        result_keywords = []
        
        for result in results:
            text = result.get('text', '').lower()
            # Mots-clés climatiques importants
            climate_keywords = {
                'antarctica', 'ice', 'melting', 'temperature', 'warming', 'climate',
                'co2', 'carbon', 'ocean', 'sea', 'level', 'greenhouse', 'emissions',
                'solar', 'sun', 'atmospheric', 'weather', 'extreme', 'models'
            }
            
            words = set(text.split())
            keywords = words.intersection(climate_keywords)
            result_keywords.append(keywords)
            all_keywords.update(keywords)
        
        if not all_keywords:
            return 0.0
        
        # Calculer la diversité comme le ratio de mots-clés uniques par résultat
        total_keywords = sum(len(kw) for kw in result_keywords)
        unique_keywords = len(all_keywords)
        
        return unique_keywords / total_keywords if total_keywords > 0 else 0.0
    
    def calculate_consistency_score(self, query_variations: List[str]) -> Dict:
        """Calcule la cohérence entre variations de requêtes"""
        print(f"\n🔄 Test de cohérence pour {len(query_variations)} variations...")
        
        all_results = []
        consistency_scores = []
        
        for query in query_variations:
            # Recherche classique
            classical_results, _ = self.classical_search(query, k=5)
            classical_texts = [r.get('text', '')[:100] for r in classical_results]
            
            # Recherche quantique
            quantum_results, _ = self.quantum_search(query, k=5)
            quantum_texts = [r.get('text', '')[:100] for r in quantum_results]
            
            all_results.append({
                'query': query,
                'classical': classical_texts,
                'quantum': quantum_texts
            })
        
        # Calculer la cohérence entre les variations
        classical_consistency = self._calculate_text_consistency([r['classical'] for r in all_results])
        quantum_consistency = self._calculate_text_consistency([r['quantum'] for r in all_results])
        
        return {
            'classical_consistency': classical_consistency,
            'quantum_consistency': quantum_consistency,
            'consistency_improvement': quantum_consistency - classical_consistency
        }
    
    def _calculate_text_consistency(self, result_sets: List[List[str]]) -> float:
        """Calcule la cohérence entre plusieurs ensembles de résultats"""
        if len(result_sets) < 2:
            return 0.0
        
        # Calculer la similarité entre les ensembles de résultats
        similarities = []
        for i in range(len(result_sets)):
            for j in range(i + 1, len(result_sets)):
                set_i = set(result_sets[i])
                set_j = set(result_sets[j])
                if set_i and set_j:
                    similarity = len(set_i.intersection(set_j)) / len(set_i.union(set_j))
                    similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def calculate_quantum_exploration_advantage(self, query_variations: List[str]) -> Dict:
        """Calcule l'avantage d'exploration quantique"""
        print(f"\n⚛️ Test d'exploration quantique pour {len(query_variations)} variations...")
        
        all_unique_results = {'classical': set(), 'quantum': set()}
        exploration_scores = []
        
        for query in query_variations:
            # Recherche classique
            classical_results, _ = self.classical_search(query, k=10)
            classical_texts = [r.get('text', '')[:200] for r in classical_results]
            
            # Recherche quantique
            quantum_results, _ = self.quantum_search(query, k=10)
            quantum_texts = [r.get('text', '')[:200] for r in quantum_results]
            
            # Ajouter aux ensembles uniques
            all_unique_results['classical'].update(classical_texts)
            all_unique_results['quantum'].update(quantum_texts)
            
            # Calculer le ratio d'exploration (nouveaux résultats vs total)
            exploration_scores.append({
                'classical_new': len(classical_texts),
                'quantum_new': len(quantum_texts),
                'classical_unique_ratio': len(set(classical_texts)) / len(classical_texts) if classical_texts else 0,
                'quantum_unique_ratio': len(set(quantum_texts)) / len(quantum_texts) if quantum_texts else 0
            })
        
        # Calculer les métriques d'exploration
        total_classical_unique = len(all_unique_results['classical'])
        total_quantum_unique = len(all_unique_results['quantum'])
        
        avg_classical_unique_ratio = np.mean([s['classical_unique_ratio'] for s in exploration_scores])
        avg_quantum_unique_ratio = np.mean([s['quantum_unique_ratio'] for s in exploration_scores])
        
        return {
            'total_unique_classical': total_classical_unique,
            'total_unique_quantum': total_quantum_unique,
            'exploration_advantage': total_quantum_unique - total_classical_unique,
            'avg_unique_ratio_classical': avg_classical_unique_ratio,
            'avg_unique_ratio_quantum': avg_quantum_unique_ratio,
            'unique_ratio_improvement': avg_quantum_unique_ratio - avg_classical_unique_ratio
        }
    
    def classical_search(self, query: str, k: int = 10) -> Tuple[List[Dict], float]:
        """Recherche classique avec mesure du temps"""
        start_time = time.time()
        results = self.cassandra_manager.search_documents_simple(query, n_results=k)
        search_time = time.time() - start_time
        return results, search_time
    
    def quantum_search(self, query: str, k: int = 10) -> Tuple[List[Dict], float]:
        """Recherche quantique avec mesure du temps"""
        start_time = time.time()
        results = retrieve_top_k(
            query, k, self.cassandra_manager, self.pca, 
            db_folder="src/quantum/quantum_db/"
        )
        search_time = time.time() - start_time
        return results, search_time
    
    def evaluate_diversity_advantage(self) -> Dict:
        """Évalue l'avantage de diversité du quantum"""
        print("🎯 ÉVALUATION DE L'AVANTAGE DE DIVERSITÉ")
        print("=" * 50)
        
        diversity_results = []
        
        for query in self.strategic_queries['diversity_test']:
            print(f"\n📊 Test de diversité: {query}")
            
            # Recherche classique
            classical_results, classical_time = self.classical_search(query, k=10)
            classical_mmr = self.calculate_mmr_score(classical_results)
            classical_semantic = self.calculate_semantic_diversity(classical_results)
            
            # Recherche quantique
            quantum_results, quantum_time = self.quantum_search(query, k=10)
            quantum_mmr = self.calculate_mmr_score(quantum_results)
            quantum_semantic = self.calculate_semantic_diversity(quantum_results)
            
            result = {
                'query': query,
                'classical': {
                    'mmr': classical_mmr,
                    'semantic_diversity': classical_semantic,
                    'time': classical_time
                },
                'quantum': {
                    'mmr': quantum_mmr,
                    'semantic_diversity': quantum_semantic,
                    'time': quantum_time
                }
            }
            
            diversity_results.append(result)
            
            print(f"  MMR - Classique: {classical_mmr:.3f}, Quantum: {quantum_mmr:.3f}")
            print(f"  Diversité sémantique - Classique: {classical_semantic:.3f}, Quantum: {quantum_semantic:.3f}")
        
        # Calculer les moyennes
        avg_classical_mmr = np.mean([r['classical']['mmr'] for r in diversity_results])
        avg_quantum_mmr = np.mean([r['quantum']['mmr'] for r in diversity_results])
        avg_classical_semantic = np.mean([r['classical']['semantic_diversity'] for r in diversity_results])
        avg_quantum_semantic = np.mean([r['quantum']['semantic_diversity'] for r in diversity_results])
        
        return {
            'mmr_improvement': avg_quantum_mmr - avg_classical_mmr,
            'semantic_improvement': avg_quantum_semantic - avg_classical_semantic,
            'detailed_results': diversity_results
        }
    
    def evaluate_robustness_advantage(self) -> Dict:
        """Évalue l'avantage de robustesse du quantum"""
        print("\n🛡️ ÉVALUATION DE L'AVANTAGE DE ROBUSTESSE")
        print("=" * 50)
        
        consistency_results = self.calculate_consistency_score(
            self.strategic_queries['robustness_test']
        )
        
        return consistency_results
    
    def evaluate_quantum_exploration_advantage(self) -> Dict:
        """Évalue l'avantage d'exploration quantique"""
        print("\n⚛️ ÉVALUATION DE L'AVANTAGE D'EXPLORATION QUANTIQUE")
        print("=" * 50)
        
        exploration_results = self.calculate_quantum_exploration_advantage(
            self.strategic_queries['quantum_exploration_test']
        )
        
        return exploration_results
    
    def run_strategic_evaluation(self) -> Dict:
        """Lance l'évaluation stratégique complète"""
        print("🚀 ÉVALUATION STRATÉGIQUE DES AVANTAGES QUANTIQUES")
        print("=" * 70)
        
        # 1. Évaluation de la diversité
        diversity_results = self.evaluate_diversity_advantage()
        
        # 2. Évaluation de la robustesse
        robustness_results = self.evaluate_robustness_advantage()
        
        # 3. Évaluation de l'exploration quantique
        exploration_results = self.evaluate_quantum_exploration_advantage()
        
        # Résumé stratégique
        strategic_summary = {
            'diversity_advantage': diversity_results,
            'robustness_advantage': robustness_results,
            'exploration_advantage': exploration_results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Sauvegarder les résultats
        self.save_strategic_results(strategic_summary)
        
        # Afficher le résumé
        self.print_strategic_summary(strategic_summary)
        
        return strategic_summary
    
    def save_strategic_results(self, results: Dict):
        """Sauvegarde les résultats stratégiques"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"strategic_quantum_evaluation_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Résultats stratégiques sauvegardés dans: {filename}")
    
    def print_strategic_summary(self, results: Dict):
        """Affiche le résumé stratégique"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ STRATÉGIQUE DES AVANTAGES QUANTIQUES")
        print("=" * 70)
        
        # Diversité
        div = results['diversity_advantage']
        print(f"\n🎯 AVANTAGE DE DIVERSITÉ:")
        print(f"  MMR Improvement: {div['mmr_improvement']:+.3f}")
        print(f"  Semantic Diversity Improvement: {div['semantic_improvement']:+.3f}")
        
        # Robustesse
        rob = results['robustness_advantage']
        print(f"\n🛡️ AVANTAGE DE ROBUSTESSE:")
        print(f"  Classical Consistency: {rob['classical_consistency']:.3f}")
        print(f"  Quantum Consistency: {rob['quantum_consistency']:.3f}")
        print(f"  Consistency Improvement: {rob['consistency_improvement']:+.3f}")
        
        # Exploration
        exp = results['exploration_advantage']
        print(f"\n⚛️ AVANTAGE D'EXPLORATION QUANTIQUE:")
        print(f"  Total Unique Classical: {exp['total_unique_classical']}")
        print(f"  Total Unique Quantum: {exp['total_unique_quantum']}")
        print(f"  Exploration Advantage: {exp['exploration_advantage']:+d} documents")
        print(f"  Unique Ratio Improvement: {exp['unique_ratio_improvement']:+.3f}")
        
        # Score global
        global_score = (
            div['mmr_improvement'] + 
            div['semantic_improvement'] + 
            rob['consistency_improvement'] + 
            exp['unique_ratio_improvement']
        )
        print(f"\n🏆 SCORE GLOBAL D'AVANTAGE QUANTIQUE: {global_score:+.3f}")

def main():
    """Script principal"""
    evaluator = StrategicQuantumEvaluator()
    
    # Lancer l'évaluation stratégique
    results = evaluator.run_strategic_evaluation()
    
    print(f"\n🎉 Évaluation stratégique terminée !")

if __name__ == "__main__":
    main() 