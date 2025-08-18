#!/usr/bin/env python3
"""
Évaluation complète du système quantique 8 qubits sophistiqué
"""

import sys
import os
sys.path.append('system')
sys.path.append('src/quantum')

import time
import numpy as np
import pickle
from cassandra_manager import CassandraVectorStoreManager
from quantum_search_8qubits import retrieve_top_k_8qubits
from quantum_encoder_8qubits import sophisticated_amplitude_encoding_8qubits

def evaluate_quantum_8qubits():
    """Évaluation complète du système quantique 8 qubits"""
    
    print("🚀 Évaluation du système quantique 8 qubits sophistiqué")
    print("=" * 60)
    
    # Connexion à Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Chargement du modèle PCA
    pca_path = "src/quantum/pca_model.pkl"
    with open(pca_path, 'rb') as f:
        pca = pickle.load(f)
    
    print(f"📊 Modèle PCA chargé: {pca.n_components_} dimensions")
    
    # Requêtes de test pour l'évaluation
    test_queries = [
        "Is Antarctica losing ice?",
        "What causes climate change?",
        "Are humans responsible for global warming?",
        "What is the greenhouse effect?",
        "How does carbon dioxide affect the climate?",
        "What are the consequences of melting glaciers?",
        "Is the Earth's temperature increasing?",
        "What is the Paris Agreement?",
        "How do oceans affect climate?",
        "What is renewable energy?"
    ]
    
    print(f"\n🔍 {len(test_queries)} requêtes de test préparées")
    
    # Métriques d'évaluation
    total_time = 0
    total_results = 0
    similarity_scores = []
    response_times = []
    
    print(f"\n📈 Début de l'évaluation...")
    print("-" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Requête {i}/{len(test_queries)}: '{query}'")
        
        # Mesure du temps
        start_time = time.time()
        
        try:
            # Recherche quantique
            results = retrieve_top_k_8qubits(
                query, 
                "src/quantum/quantum_db_8qubits", 
                k=10,
                cassandra_manager=cassandra_manager
            )
            
            end_time = time.time()
            query_time = end_time - start_time
            total_time += query_time
            total_results += len(results)
            
            # Collecte des scores
            scores = [score for score, _, _ in results]
            similarity_scores.extend(scores)
            response_times.append(query_time)
            
            print(f"   ⏱️ Temps: {query_time:.2f}s")
            print(f"   📊 Résultats: {len(results)}")
            print(f"   🎯 Score max: {max(scores):.4f}")
            print(f"   🎯 Score min: {min(scores):.4f}")
            print(f"   🎯 Score moyen: {np.mean(scores):.4f}")
            
            # Affichage des top 3 résultats
            print(f"   📋 Top 3 résultats:")
            for j, (score, path, chunk_id) in enumerate(results[:3], 1):
                print(f"      {j}. {chunk_id}: {score:.4f}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            continue
    
    # Calcul des métriques globales
    print(f"\n📊 MÉTRIQUES GLOBALES")
    print("=" * 60)
    
    avg_time = total_time / len(test_queries)
    avg_results = total_results / len(test_queries)
    avg_similarity = np.mean(similarity_scores)
    std_similarity = np.std(similarity_scores)
    
    print(f"⏱️ Temps total: {total_time:.2f}s")
    print(f"⏱️ Temps moyen par requête: {avg_time:.2f}s")
    print(f"📊 Nombre total de résultats: {total_results}")
    print(f"📊 Résultats moyens par requête: {avg_results:.1f}")
    print(f"🎯 Similarité moyenne: {avg_similarity:.4f}")
    print(f"🎯 Écart-type similarité: {std_similarity:.4f}")
    print(f"🎯 Similarité min: {min(similarity_scores):.4f}")
    print(f"🎯 Similarité max: {max(similarity_scores):.4f}")
    
    # Analyse de la distribution des similarités
    print(f"\n📈 DISTRIBUTION DES SIMILARITÉS")
    print("-" * 40)
    
    # Histogramme des similarités
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    hist, _ = np.histogram(similarity_scores, bins=bins)
    
    for i, (bin_start, bin_end) in enumerate(zip(bins[:-1], bins[1:])):
        count = hist[i]
        percentage = (count / len(similarity_scores)) * 100
        bar = "█" * int(percentage / 5)
        print(f"   {bin_start:.1f}-{bin_end:.1f}: {count:3d} ({percentage:5.1f}%) {bar}")
    
    # Analyse des temps de réponse
    print(f"\n⏱️ ANALYSE DES TEMPS DE RÉPONSE")
    print("-" * 40)
    
    print(f"   Temps min: {min(response_times):.2f}s")
    print(f"   Temps max: {max(response_times):.2f}s")
    print(f"   Temps moyen: {np.mean(response_times):.2f}s")
    print(f"   Écart-type: {np.std(response_times):.2f}s")
    
    # Comparaison avec les performances théoriques
    print(f"\n🔬 COMPARAISON THÉORIQUE")
    print("-" * 40)
    
    # Calcul théorique pour 16 qubits
    theoretical_16q_time = avg_time * 256  # 2^8 = 256 fois plus rapide
    theoretical_16q_total = theoretical_16q_time * len(test_queries)
    
    print(f"   Temps théorique 16 qubits: {theoretical_16q_total:.2f}s ({theoretical_16q_total/60:.1f} min)")
    print(f"   Gain de performance: ~256x")
    print(f"   Économie de temps: {theoretical_16q_total - total_time:.2f}s")
    
    # Évaluation de la qualité
    print(f"\n🎯 ÉVALUATION DE LA QUALITÉ")
    print("-" * 40)
    
    # Différenciation des résultats
    unique_scores = len(set([round(s, 3) for s in similarity_scores]))
    differentiation_ratio = unique_scores / len(similarity_scores)
    
    print(f"   Scores uniques: {unique_scores}/{len(similarity_scores)}")
    print(f"   Ratio de différenciation: {differentiation_ratio:.3f}")
    
    if differentiation_ratio > 0.8:
        print(f"   ✅ Excellente différenciation")
    elif differentiation_ratio > 0.5:
        print(f"   ✅ Bonne différenciation")
    else:
        print(f"   ⚠️ Différenciation insuffisante")
    
    # Stabilité des résultats
    time_variance = np.var(response_times)
    if time_variance < 1.0:
        print(f"   ✅ Temps de réponse stables")
    else:
        print(f"   ⚠️ Temps de réponse variables")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS")
    print("-" * 40)
    
    if avg_time < 60:  # Moins d'1 minute par requête
        print(f"   ✅ Performance acceptable pour usage interactif")
    else:
        print(f"   ⚠️ Performance lente pour usage interactif")
    
    if avg_similarity > 0.7:
        print(f"   ✅ Qualité des résultats élevée")
    else:
        print(f"   ⚠️ Qualité des résultats à améliorer")
    
    if differentiation_ratio > 0.5:
        print(f"   ✅ Différenciation suffisante")
    else:
        print(f"   ⚠️ Différenciation insuffisante")
    
    print(f"\n🎉 Évaluation terminée !")
    return {
        'total_time': total_time,
        'avg_time': avg_time,
        'avg_similarity': avg_similarity,
        'differentiation_ratio': differentiation_ratio,
        'similarity_scores': similarity_scores,
        'response_times': response_times
    }

if __name__ == "__main__":
    results = evaluate_quantum_8qubits()
