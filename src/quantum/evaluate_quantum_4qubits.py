#!/usr/bin/env python3
"""
Évaluation du système quantique 4 qubits
"""

import sys
import os
sys.path.append('../../system')
sys.path.append('src/quantum')

import time
import numpy as np
from datetime import datetime
from quantum_search_4qubits import QuantumSearch4Qubits

def evaluate_quantum_4qubits():
    """Évaluer le système quantique 4 qubits"""
    
    print("🔬 Évaluation du système quantique 4 qubits")
    print("=" * 60)
    
    # Initialiser le système
    quantum_search = QuantumSearch4Qubits()
    
    # Requêtes de test
    test_queries = [
        "climate change",
        "global warming", 
        "carbon emissions",
        "renewable energy",
        "greenhouse gases",
        "ocean acidification",
        "melting ice caps",
        "solar power",
        "wind energy",
        "biodiversity loss"
    ]
    
    # Métriques globales
    all_similarities = []
    all_times = []
    all_results = []
    
    print(f"🔍 Évaluation sur {len(test_queries)} requêtes...")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"📊 Requête {i}/{len(test_queries)}: '{query}'")
        
        try:
            # Recherche quantique
            results, search_time = quantum_search.search_documents_quantum_4qubits(query, n_results=10)
            
            if results:
                # Extraire les similarités
                similarities = [result['similarity'] for result in results]
                
                # Statistiques pour cette requête
                max_sim = max(similarities)
                min_sim = min(similarities)
                mean_sim = np.mean(similarities)
                std_sim = np.std(similarities)
                
                print(f"   ⏱️ Temps: {search_time:.2f}s")
                print(f"   📈 Similarités: max={max_sim:.4f}, min={min_sim:.4f}, moy={mean_sim:.4f}, std={std_sim:.4f}")
                print(f"   🎯 Résultats: {len(results)} documents trouvés")
                
                # Stocker les métriques
                all_similarities.extend(similarities)
                all_times.append(search_time)
                all_results.append({
                    'query': query,
                    'results': results,
                    'search_time': search_time,
                    'similarities': similarities
                })
                
            else:
                print(f"   ❌ Aucun résultat trouvé")
                all_times.append(0)
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            all_times.append(0)
        
        print()
    
    # Calculs globaux
    if all_similarities:
        print("📊 MÉTRIQUES GLOBALES")
        print("-" * 40)
        
        # Statistiques des similarités
        print("🔬 Similarités:")
        print(f"   Moyenne: {np.mean(all_similarities):.4f}")
        print(f"   Médiane: {np.median(all_similarities):.4f}")
        print(f"   Écart-type: {np.std(all_similarities):.4f}")
        print(f"   Min: {np.min(all_similarities):.4f}")
        print(f"   Max: {np.max(all_similarities):.4f}")
        
        # Statistiques des temps
        print("\n⏱️ Temps de réponse:")
        print(f"   Total: {np.sum(all_times):.2f}s")
        print(f"   Moyenne par requête: {np.mean(all_times):.2f}s")
        print(f"   Médiane: {np.median(all_times):.2f}s")
        print(f"   Min: {np.min(all_times):.2f}s")
        print(f"   Max: {np.max(all_times):.2f}s")
        
        # Analyse de la distribution
        print("\n📈 Distribution des similarités:")
        ranges = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
        for min_val, max_val in ranges:
            count = sum(1 for s in all_similarities if min_val <= s < max_val)
            percentage = (count / len(all_similarities)) * 100
            bar = "█" * (count // 2) if count > 0 else ""
            print(f"   {min_val:.1f}-{max_val:.1f}: {count:3d} ({percentage:5.1f}%) {bar}")
        
        # Différenciation
        unique_similarities = len(set(all_similarities))
        differentiation_ratio = unique_similarities / len(all_similarities)
        print(f"\n🎯 Différenciation: {unique_similarities}/{len(all_similarities)} scores uniques ({differentiation_ratio*100:.1f}%)")
        
        # Évaluation de la qualité
        print("\n🏆 ÉVALUATION DE LA QUALITÉ")
        print("-" * 40)
        
        # Score de pertinence (basé sur la moyenne des similarités)
        mean_similarity = np.mean(all_similarities)
        if mean_similarity >= 0.7:
            pertinence_score = 9
        elif mean_similarity >= 0.5:
            pertinence_score = 7
        elif mean_similarity >= 0.3:
            pertinence_score = 5
        else:
            pertinence_score = 3
        
        # Score de différenciation
        differentiation_score = differentiation_ratio * 10
        
        # Score de performance (basé sur le temps moyen)
        mean_time = np.mean(all_times)
        if mean_time <= 5:
            performance_score = 9
        elif mean_time <= 10:
            performance_score = 7
        elif mean_time <= 30:
            performance_score = 5
        else:
            performance_score = 3
        
        # Score global
        global_score = (pertinence_score + differentiation_score + performance_score) / 3
        
        print(f"📊 Pertinence: {pertinence_score}/10 (moyenne: {mean_similarity:.3f})")
        print(f"🎯 Différenciation: {differentiation_score:.1f}/10 ({differentiation_ratio*100:.1f}%)")
        print(f"⚡ Performance: {performance_score}/10 (temps moyen: {mean_time:.1f}s)")
        print(f"🏆 Score global: {global_score:.1f}/10")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS")
        print("-" * 40)
        
        if pertinence_score < 7:
            print("⚠️ Améliorer la pertinence des résultats")
        if differentiation_score < 7:
            print("⚠️ Améliorer la différenciation des scores")
        if performance_score < 7:
            print("⚠️ Optimiser les performances")
        
        if global_score >= 7:
            print("✅ Système de bonne qualité")
        elif global_score >= 5:
            print("⚠️ Système de qualité moyenne")
        else:
            print("❌ Système nécessite des améliorations")
        
        return {
            'similarities': all_similarities,
            'times': all_times,
            'results': all_results,
            'global_score': global_score,
            'mean_similarity': mean_similarity,
            'mean_time': mean_time,
            'differentiation_ratio': differentiation_ratio
        }
    
    else:
        print("❌ Aucune donnée d'évaluation disponible")
        return None

if __name__ == "__main__":
    results = evaluate_quantum_4qubits()
    
    if results:
        print(f"\n📅 Évaluation terminée le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ Évaluation du système quantique 4 qubits terminée")
    else:
        print("❌ Évaluation échouée")
