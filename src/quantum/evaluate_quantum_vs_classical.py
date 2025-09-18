#!/usr/bin/env python3
"""
Script d'évaluation comparative : Quantum RAG vs Classical RAG
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Tuple
import json
from datetime import datetime

sys.path.append('system')
sys.path.append('src/quantum')

from cassandra_manager import CassandraVectorStoreManager
from quantum_search import retrieve_top_k, quantum_overlap_similarity
from quantum_encoder import amplitude_encoding
import joblib

class QuantumVsClassicalEvaluator:
    def __init__(self):
        """Initialise l'évaluateur"""
        self.cassandra_manager = CassandraVectorStoreManager()
        self.pca = joblib.load("src/quantum/pca_model.pkl")
        
        # Requêtes de test pour l'évaluation
        self.test_queries = [
            "Is Antarctica losing land ice?",
            "What is the evidence for global warming?",
            "How reliable are climate models?",
            "What causes sea level rise?",
            "Is CO2 the main driver of climate change?",
            "What is the urban heat island effect?",
            "How do solar cycles affect climate?",
            "What is the evidence for ocean acidification?",
            "Are extreme weather events increasing?",
            "What is the role of aerosols in climate change?"
        ]
        
        # Métriques de comparaison
        self.metrics = {
            'retrieval_time': {'quantum': [], 'classical': []},
            'similarity_scores': {'quantum': [], 'classical': []},
            'precision_at_k': {'quantum': [], 'classical': []},
            'recall_at_k': {'quantum': [], 'classical': []},
            'mrr': {'quantum': [], 'classical': []},
            'ndcg_at_k': {'quantum': [], 'classical': []}
        }
    
    def classical_search(self, query: str, k: int = 10) -> List[Dict]:
        """Recherche classique avec Cassandra"""
        start_time = time.time()
        
        # Recherche classique
        results = self.cassandra_manager.search_documents_simple(query, n_results=k)
        
        search_time = time.time() - start_time
        
        return results, search_time
    
    def quantum_search(self, query: str, k: int = 10) -> List[Dict]:
        """Recherche quantique"""
        start_time = time.time()
        
        # Recherche quantique
        results = retrieve_top_k(
            query, 
            k, 
            self.cassandra_manager, 
            self.pca, 
            db_folder="src/quantum/quantum_db/"
        )
        
        search_time = time.time() - start_time
        
        return results, search_time
    
    def calculate_precision_at_k(self, results: List[Dict], k: int, relevant_keywords: List[str]) -> float:
        """Calcule la précision@K basée sur des mots-clés pertinents"""
        if not results:
            return 0.0
        
        relevant_count = 0
        for i, result in enumerate(results[:k]):
            text = result.get('text', '').lower()
            if any(keyword.lower() in text for keyword in relevant_keywords):
                relevant_count += 1
        
        return relevant_count / min(k, len(results))
    
    def calculate_recall_at_k(self, results: List[Dict], k: int, relevant_keywords: List[str], total_relevant: int) -> float:
        """Calcule le rappel@K"""
        if not results or total_relevant == 0:
            return 0.0
        
        relevant_found = 0
        for result in results[:k]:
            text = result.get('text', '').lower()
            if any(keyword.lower() in text for keyword in relevant_keywords):
                relevant_found += 1
        
        return relevant_found / total_relevant
    
    def calculate_mrr(self, results: List[Dict], relevant_keywords: List[str]) -> float:
        """Calcule le Mean Reciprocal Rank"""
        for i, result in enumerate(results):
            text = result.get('text', '').lower()
            if any(keyword.lower() in text for keyword in relevant_keywords):
                return 1.0 / (i + 1)
        return 0.0
    
    def calculate_ndcg_at_k(self, results: List[Dict], k: int, relevant_keywords: List[str]) -> float:
        """Calcule le NDCG@K"""
        if not results:
            return 0.0
        
        # Calculer les scores de pertinence
        relevance_scores = []
        for result in results[:k]:
            text = result.get('text', '').lower()
            relevance = sum(1 for keyword in relevant_keywords if keyword.lower() in text)
            relevance_scores.append(relevance)
        
        # NDCG = DCG / IDCG
        dcg = sum(score / np.log2(i + 2) for i, score in enumerate(relevance_scores))
        
        # IDCG (scores idéaux triés)
        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = sum(score / np.log2(i + 2) for i, score in enumerate(ideal_scores))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def get_relevant_keywords(self, query: str) -> List[str]:
        """Extrait les mots-clés pertinents de la requête"""
        # Mots-clés spécifiques pour chaque requête
        query_keywords = {
            "Is Antarctica losing land ice?": ["antarctica", "ice", "losing", "land", "melting"],
            "What is the evidence for global warming?": ["evidence", "global warming", "temperature", "increase"],
            "How reliable are climate models?": ["climate models", "reliable", "accuracy", "prediction"],
            "What causes sea level rise?": ["sea level", "rise", "ocean", "melting", "thermal expansion"],
            "Is CO2 the main driver of climate change?": ["co2", "carbon dioxide", "driver", "climate change", "greenhouse"],
            "What is the urban heat island effect?": ["urban heat island", "city", "temperature", "urban"],
            "How do solar cycles affect climate?": ["solar cycles", "sun", "solar activity", "climate"],
            "What is the evidence for ocean acidification?": ["ocean acidification", "ph", "carbonate", "ocean"],
            "Are extreme weather events increasing?": ["extreme weather", "events", "increasing", "storms", "heatwaves"],
            "What is the role of aerosols in climate change?": ["aerosols", "climate change", "cooling", "particles"]
        }
        
        return query_keywords.get(query, query.lower().split())
    
    def evaluate_single_query(self, query: str) -> Dict:
        """Évalue une seule requête"""
        print(f"\n🔍 Évaluation de la requête: {query}")
        
        # Mots-clés pertinents
        relevant_keywords = self.get_relevant_keywords(query)
        
        # Recherche classique
        print("  📊 Recherche classique...")
        classical_results, classical_time = self.classical_search(query, k=10)
        
        # Recherche quantique
        print("  ⚛️ Recherche quantique...")
        quantum_results, quantum_time = self.quantum_search(query, k=10)
        
        # Calculer les métriques
        results = {
            'query': query,
            'classical': {
                'time': classical_time,
                'precision_at_5': self.calculate_precision_at_k(classical_results, 5, relevant_keywords),
                'precision_at_10': self.calculate_precision_at_k(classical_results, 10, relevant_keywords),
                'recall_at_10': self.calculate_recall_at_k(classical_results, 10, relevant_keywords, 10),
                'mrr': self.calculate_mrr(classical_results, relevant_keywords),
                'ndcg_at_10': self.calculate_ndcg_at_k(classical_results, 10, relevant_keywords),
                'num_results': len(classical_results)
            },
            'quantum': {
                'time': quantum_time,
                'precision_at_5': self.calculate_precision_at_k(quantum_results, 5, relevant_keywords),
                'precision_at_10': self.calculate_precision_at_k(quantum_results, 10, relevant_keywords),
                'recall_at_10': self.calculate_recall_at_k(quantum_results, 10, relevant_keywords, 10),
                'mrr': self.calculate_mrr(quantum_results, relevant_keywords),
                'ndcg_at_10': self.calculate_ndcg_at_k(quantum_results, 10, relevant_keywords),
                'num_results': len(quantum_results)
            }
        }
        
        # Afficher les résultats
        print(f"  ⏱️  Temps - Classique: {classical_time:.3f}s, Quantum: {quantum_time:.3f}s")
        print(f"  📈 Précision@5 - Classique: {results['classical']['precision_at_5']:.3f}, Quantum: {results['quantum']['precision_at_5']:.3f}")
        print(f"  📈 Précision@10 - Classique: {results['classical']['precision_at_10']:.3f}, Quantum: {results['quantum']['precision_at_10']:.3f}")
        print(f"  📈 MRR - Classique: {results['classical']['mrr']:.3f}, Quantum: {results['quantum']['mrr']:.3f}")
        
        return results
    
    def run_full_evaluation(self) -> Dict:
        """Lance l'évaluation complète"""
        print("🚀 ÉVALUATION QUANTUM vs CLASSICAL")
        print("=" * 60)
        
        all_results = []
        
        for query in self.test_queries:
            try:
                result = self.evaluate_single_query(query)
                all_results.append(result)
            except Exception as e:
                print(f"❌ Erreur pour la requête '{query}': {e}")
        
        # Calculer les moyennes
        summary = self.calculate_summary_statistics(all_results)
        
        # Sauvegarder les résultats
        self.save_results(all_results, summary)
        
        return summary
    
    def calculate_summary_statistics(self, results: List[Dict]) -> Dict:
        """Calcule les statistiques résumées"""
        classical_metrics = []
        quantum_metrics = []
        
        for result in results:
            classical_metrics.append(result['classical'])
            quantum_metrics.append(result['quantum'])
        
        summary = {
            'classical_avg': {
                'time': np.mean([m['time'] for m in classical_metrics]),
                'precision_at_5': np.mean([m['precision_at_5'] for m in classical_metrics]),
                'precision_at_10': np.mean([m['precision_at_10'] for m in classical_metrics]),
                'recall_at_10': np.mean([m['recall_at_10'] for m in classical_metrics]),
                'mrr': np.mean([m['mrr'] for m in classical_metrics]),
                'ndcg_at_10': np.mean([m['ndcg_at_10'] for m in classical_metrics])
            },
            'quantum_avg': {
                'time': np.mean([m['time'] for m in quantum_metrics]),
                'precision_at_5': np.mean([m['precision_at_5'] for m in quantum_metrics]),
                'precision_at_10': np.mean([m['precision_at_10'] for m in quantum_metrics]),
                'recall_at_10': np.mean([m['recall_at_10'] for m in quantum_metrics]),
                'mrr': np.mean([m['mrr'] for m in quantum_metrics]),
                'ndcg_at_10': np.mean([m['ndcg_at_10'] for m in quantum_metrics])
            }
        }
        
        return summary
    
    def save_results(self, results: List[Dict], summary: Dict):
        """Sauvegarde les résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_results_{timestamp}.json"
        
        output = {
            'timestamp': timestamp,
            'summary': summary,
            'detailed_results': results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Résultats sauvegardés dans: {filename}")
    
    def print_summary(self, summary: Dict):
        """Affiche le résumé des résultats"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'ÉVALUATION")
        print("=" * 60)
        
        print(f"\n⏱️  TEMPS DE RECHERCHE (moyenne):")
        print(f"  Classique: {summary['classical_avg']['time']:.3f}s")
        print(f"  Quantum:   {summary['quantum_avg']['time']:.3f}s")
        print(f"  Ratio:     {summary['quantum_avg']['time'] / summary['classical_avg']['time']:.2f}x")
        
        print(f"\n📈 PRÉCISION@5 (moyenne):")
        print(f"  Classique: {summary['classical_avg']['precision_at_5']:.3f}")
        print(f"  Quantum:   {summary['quantum_avg']['precision_at_5']:.3f}")
        print(f"  Différence: {summary['quantum_avg']['precision_at_5'] - summary['classical_avg']['precision_at_5']:+.3f}")
        
        print(f"\n📈 PRÉCISION@10 (moyenne):")
        print(f"  Classique: {summary['classical_avg']['precision_at_10']:.3f}")
        print(f"  Quantum:   {summary['quantum_avg']['precision_at_10']:.3f}")
        print(f"  Différence: {summary['quantum_avg']['precision_at_10'] - summary['classical_avg']['precision_at_10']:+.3f}")
        
        print(f"\n📈 MRR (moyenne):")
        print(f"  Classique: {summary['classical_avg']['mrr']:.3f}")
        print(f"  Quantum:   {summary['quantum_avg']['mrr']:.3f}")
        print(f"  Différence: {summary['quantum_avg']['mrr'] - summary['classical_avg']['mrr']:+.3f}")
        
        print(f"\n📈 NDCG@10 (moyenne):")
        print(f"  Classique: {summary['classical_avg']['ndcg_at_10']:.3f}")
        print(f"  Quantum:   {summary['quantum_avg']['ndcg_at_10']:.3f}")
        print(f"  Différence: {summary['quantum_avg']['ndcg_at_10'] - summary['classical_avg']['ndcg_at_10']:+.3f}")

def main():
    """Script principal"""
    evaluator = QuantumVsClassicalEvaluator()
    
    # Lancer l'évaluation
    summary = evaluator.run_full_evaluation()
    
    # Afficher le résumé
    evaluator.print_summary(summary)

if __name__ == "__main__":
    main() 