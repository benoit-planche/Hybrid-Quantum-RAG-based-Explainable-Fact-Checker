#!/usr/bin/env python3
"""
Démonstration de l'intégration de Grover dans le système de fact-checking
"""

import os
import sys
import time
from typing import List, Tuple

# Ajouter les chemins nécessaires
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(os.path.dirname(current_dir), 'system')
sys.path.insert(0, system_dir)
sys.path.insert(0, current_dir)

from hybrid_quantum_search import HybridQuantumSearch, SearchStrategy
from cassandra_manager import create_cassandra_manager

def print_results(results: List[Tuple[float, str, str]], title: str):
    """Afficher les résultats de manière formatée"""
    print(f"\n{title}")
    print("-" * len(title))
    
    if not results:
        print("❌ Aucun résultat trouvé")
        return
    
    for i, (score, path, chunk_id) in enumerate(results[:5]):
        print(f"{i+1}. Chunk {chunk_id} - Score: {score:.4f}")
        print(f"   📁 {os.path.basename(path)}")

def demo_grover_integration():
    """Démonstration de l'intégration Grover"""
    print("🚀 DÉMONSTRATION INTÉGRATION GROVER")
    print("=" * 50)
    
    # Configuration
    query = "Antarctica is gaining ice due to climate change"
    db_folder = "../src/quantum/quantum_db_8qubits/"
    
    # Initialiser Cassandra
    try:
        cassandra_manager = create_cassandra_manager()
        print("✅ Cassandra initialisé")
    except Exception as e:
        print(f"❌ Erreur Cassandra: {e}")
        return
    
    # Vérifier la base de données
    collection_info = cassandra_manager.get_collection_info()
    if not collection_info.get('index_loaded', False):
        print("❌ Aucun document dans la base. Veuillez d'abord indexer.")
        return
    
    print(f"📊 Base de données: {collection_info.get('document_count', 0)} documents")
    print(f"🔍 Requête de test: '{query}'")
    
    # Tester différentes stratégies
    strategies = [
        (SearchStrategy.CLASSICAL_QUANTUM, "Système Classique Quantique"),
        (SearchStrategy.GROVER_ONLY, "Grover Pur"),
        (SearchStrategy.GROVER_HYBRID, "Grover Hybride"),
        (SearchStrategy.HYBRID_ADAPTIVE, "Hybride Adaptatif")
    ]
    
    results_comparison = {}
    
    for strategy, description in strategies:
        print(f"\n{'='*20} {description} {'='*20}")
        
        # Créer le système de recherche
        hybrid_search = HybridQuantumSearch(strategy=strategy)
        
        # Exécuter la recherche
        start_time = time.time()
        try:
            results = hybrid_search.search(
                query_text=query,
                db_folder=db_folder,
                k=5,
                n_qubits=8,
                cassandra_manager=cassandra_manager
            )
            duration = time.time() - start_time
            
            print_results(results, f"Résultats {description}")
            print(f"⏱️ Temps d'exécution: {duration:.2f}s")
            
            results_comparison[strategy.value] = {
                'results': results,
                'duration': duration,
                'count': len(results)
            }
            
        except Exception as e:
            print(f"❌ Erreur avec {description}: {e}")
            results_comparison[strategy.value] = {
                'results': [],
                'duration': 0.0,
                'count': 0,
                'error': str(e)
            }
    
    # Comparaison des performances
    print("\n" + "="*50)
    print("📊 COMPARAISON DES PERFORMANCES")
    print("="*50)
    
    for strategy_name, data in results_comparison.items():
        if 'error' in data:
            print(f"{strategy_name:20} | ❌ Erreur: {data['error']}")
        else:
            print(f"{strategy_name:20} | ⏱️ {data['duration']:6.2f}s | 📊 {data['count']:2d} résultats")
    
    # Recommandation
    print("\n💡 RECOMMANDATIONS:")
    
    # Trouver la stratégie la plus rapide
    valid_strategies = {k: v for k, v in results_comparison.items() if 'error' not in v}
    if valid_strategies:
        fastest = min(valid_strategies.keys(), key=lambda k: valid_strategies[k]['duration'])
        print(f"🚀 Plus rapide: {fastest} ({valid_strategies[fastest]['duration']:.2f}s)")
        
        # Analyser la qualité des résultats
        best_scores = {}
        for strategy_name, data in valid_strategies.items():
            if data['results']:
                best_scores[strategy_name] = data['results'][0][0]
        
        if best_scores:
            best_quality = max(best_scores.keys(), key=lambda k: best_scores[k])
            print(f"🎯 Meilleure qualité: {best_quality} (score: {best_scores[best_quality]:.4f})")
    
    # Statistiques de performance
    hybrid_search = HybridQuantumSearch()
    stats = hybrid_search.get_performance_stats()
    
    if stats:
        print(f"\n📈 STATISTIQUES DE PERFORMANCE:")
        for strategy, stat in stats.items():
            print(f"  {strategy}: {stat['avg_duration']:.2f}s moyen, {stat['total_queries']} requêtes")

def demo_adaptive_strategy():
    """Démonstration de la sélection adaptative de stratégie"""
    print("\n🎯 DÉMONSTRATION SÉLECTION ADAPTATIVE")
    print("="*50)
    
    # Simuler différents scénarios
    scenarios = [
        ("Requête courte", "CO2", 1000),
        ("Requête longue", "Climate change is a complex phenomenon that affects multiple aspects of our planet including temperature, precipitation patterns, sea levels, and ecosystem dynamics", 1000),
        ("Petite base", "Antarctica", 500),
        ("Grande base", "Global warming", 20000)
    ]
    
    hybrid_search = HybridQuantumSearch()
    
    for scenario_name, query, db_size in scenarios:
        print(f"\n📝 {scenario_name}:")
        print(f"   Requête: '{query[:50]}...'")
        print(f"   Base: {db_size} documents")
        
        strategy = hybrid_search.adaptive_strategy_selection(len(query), db_size)
        print(f"   🎯 Stratégie recommandée: {strategy.value}")

if __name__ == "__main__":
    demo_grover_integration()
    demo_adaptive_strategy()
