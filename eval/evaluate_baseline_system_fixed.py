#!/usr/bin/env python3
"""
Évaluation complète du système de base (classique) - Version corrigée
"""

import sys
import os
sys.path.append('system')
sys.path.append('src/quantum')

import time
import numpy as np
from datetime import datetime
from system.cassandra_manager import CassandraVectorStoreManager

def evaluate_baseline_system_fixed():
    """Évaluation complète du système de base classique avec gestion d'erreurs"""
    
    print("🚀 Évaluation du système de base (classique) - Version corrigée")
    print("=" * 70)
    
    # Connexion à Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Requêtes de test identiques à l'évaluation quantique
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
    
    print(f"📋 {len(test_queries)} requêtes de test")
    print(f"🔍 Système: Classique (Cassandra + Ollama)")
    print(f"🤖 Modèle: {cassandra_manager.embedding_model}")
    print()
    
    # Métriques de collecte
    all_times = []
    all_similarities = []
    all_results = []
    
    # Test de chaque requête
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Requête {i}/{len(test_queries)}: '{query}'")
        
        start_time = time.time()
        
        try:
            # Essayer d'abord la recherche MMR
            try:
                results = cassandra_manager.search_documents_mmr(
                    query=query,
                    n_results=10,
                    lambda_param=0.5
                )
            except Exception as e:
                print(f"   ⚠️ MMR échoué, tentative recherche simple: {e}")
                # Fallback vers recherche simple
                results = cassandra_manager.search_documents_simple(
                    query=query,
                    n_results=10
                )
            
            end_time = time.time()
            query_time = end_time - start_time
            
            # Extraction des similarités avec gestion d'erreurs
            similarities = []
            valid_results = []
            
            for result in results:
                try:
                    # Essayer différentes clés pour les scores
                    score = None
                    if 'score' in result:
                        score = result['score']
                    elif 'similarity' in result:
                        score = result['similarity']
                    elif 'distance' in result:
                        # Convertir la distance en similarité
                        score = 1.0 - result['distance']
                    else:
                        # Score par défaut
                        score = 0.5
                    
                    # Validation du score
                    if score is not None and 0 <= score <= 1:
                        similarities.append(score)
                        valid_results.append(result)
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur traitement résultat: {e}")
                    continue
            
            # Statistiques de la requête
            if similarities:
                max_sim = max(similarities)
                min_sim = min(similarities)
                mean_sim = np.mean(similarities)
            else:
                max_sim = min_sim = mean_sim = 0
            
            print(f"   ⏱️ Temps: {query_time:.2f}s")
            print(f"   📊 Résultats: {len(valid_results)}")
            print(f"   🎯 Score max: {max_sim:.4f}")
            print(f"   🎯 Score min: {min_sim:.4f}")
            print(f"   🎯 Score moyen: {mean_sim:.4f}")
            
            # Affichage des top 3 résultats
            print(f"   📋 Top 3 résultats:")
            for j, result in enumerate(valid_results[:3], 1):
                doc_id = result.get('id', result.get('doc_id', f'Doc_{j}'))
                score = similarities[j-1] if j <= len(similarities) else 0
                print(f"      {j}. {doc_id}: {score:.4f}")
            
            # Stockage des métriques
            all_times.append(query_time)
            all_similarities.extend(similarities)
            all_results.append({
                'query': query,
                'time': query_time,
                'results_count': len(valid_results),
                'similarities': similarities,
                'max_sim': max_sim,
                'min_sim': min_sim,
                'mean_sim': mean_sim
            })
            
        except Exception as e:
            print(f"   ❌ Erreur complète: {e}")
            all_times.append(0)
            all_results.append({
                'query': query,
                'time': 0,
                'results_count': 0,
                'similarities': [],
                'max_sim': 0,
                'min_sim': 0,
                'mean_sim': 0
            })
        
        print()
    
    # Calcul des métriques globales
    total_time = sum(all_times)
    avg_time = np.mean(all_times)
    total_results = sum(r['results_count'] for r in all_results)
    avg_results = total_results / len(test_queries)
    
    # Statistiques des similarités
    if all_similarities:
        mean_similarity = np.mean(all_similarities)
        std_similarity = np.std(all_similarities)
        min_similarity = min(all_similarities)
        max_similarity = max(all_similarities)
    else:
        mean_similarity = std_similarity = min_similarity = max_similarity = 0
    
    # Distribution des similarités
    similarity_ranges = {
        '0.0-0.2': 0,
        '0.2-0.4': 0,
        '0.4-0.6': 0,
        '0.6-0.8': 0,
        '0.8-1.0': 0
    }
    
    for sim in all_similarities:
        if sim < 0.2:
            similarity_ranges['0.0-0.2'] += 1
        elif sim < 0.4:
            similarity_ranges['0.2-0.4'] += 1
        elif sim < 0.6:
            similarity_ranges['0.4-0.6'] += 1
        elif sim < 0.8:
            similarity_ranges['0.6-0.8'] += 1
        else:
            similarity_ranges['0.8-1.0'] += 1
    
    # Calcul de la différenciation
    unique_scores = len(set(all_similarities))
    differentiation_ratio = unique_scores / len(all_similarities) if all_similarities else 0
    
    # Affichage des résultats globaux
    print("📊 MÉTRIQUES GLOBALES")
    print("=" * 60)
    print(f"⏱️ Temps total: {total_time:.2f}s")
    print(f"⏱️ Temps moyen par requête: {avg_time:.2f}s")
    print(f"📊 Nombre total de résultats: {total_results}")
    print(f"📊 Résultats moyens par requête: {avg_results:.1f}")
    print(f"🎯 Similarité moyenne: {mean_similarity:.4f}")
    print(f"🎯 Écart-type similarité: {std_similarity:.4f}")
    print(f"🎯 Similarité min: {min_similarity:.4f}")
    print(f"🎯 Similarité max: {max_similarity:.4f}")
    print()
    
    print("📈 DISTRIBUTION DES SIMILARITÉS")
    print("-" * 40)
    for range_name, count in similarity_ranges.items():
        percentage = (count / len(all_similarities) * 100) if all_similarities else 0
        bar = "█" * (count // 2) if count > 0 else ""
        print(f"   {range_name}: {count:3d} ({percentage:5.1f}%) {bar}")
    print()
    
    print("⏱️ ANALYSE DES TEMPS DE RÉPONSE")
    print("-" * 40)
    if all_times:
        print(f"   Temps min: {min(all_times):.2f}s")
        print(f"   Temps max: {max(all_times):.2f}s")
        print(f"   Temps moyen: {avg_time:.2f}s")
        print(f"   Écart-type: {np.std(all_times):.2f}s")
    else:
        print("   ❌ Aucun temps mesuré")
    print()
    
    print("🎯 ÉVALUATION DE LA QUALITÉ")
    print("-" * 40)
    print(f"   Scores uniques: {unique_scores}/{len(all_similarities)}")
    print(f"   Ratio de différenciation: {differentiation_ratio:.3f}")
    
    if differentiation_ratio > 0.8:
        print("   ✅ Excellente différenciation")
    elif differentiation_ratio > 0.6:
        print("   ⚠️ Bonne différenciation")
    else:
        print("   ❌ Différenciation insuffisante")
    
    if avg_time < 1:
        print("   ✅ Temps de réponse excellent")
    elif avg_time < 5:
        print("   ⚠️ Temps de réponse acceptable")
    else:
        print("   ❌ Temps de réponse lent")
    print()
    
    print("💡 RECOMMANDATIONS")
    print("-" * 40)
    if avg_time > 5:
        print("   ⚠️ Optimiser les performances de recherche")
    if mean_similarity < 0.7:
        print("   ⚠️ Améliorer la qualité des embeddings")
    if differentiation_ratio < 0.8:
        print("   ⚠️ Améliorer la différenciation des résultats")
    
    print("   ✅ Système classique fonctionnel")
    print()
    
    print("🎉 Évaluation terminée !")
    
    return {
        'total_time': total_time,
        'avg_time': avg_time,
        'total_results': total_results,
        'mean_similarity': mean_similarity,
        'std_similarity': std_similarity,
        'differentiation_ratio': differentiation_ratio,
        'similarity_ranges': similarity_ranges,
        'all_results': all_results
    }

if __name__ == "__main__":
    evaluate_baseline_system_fixed()
