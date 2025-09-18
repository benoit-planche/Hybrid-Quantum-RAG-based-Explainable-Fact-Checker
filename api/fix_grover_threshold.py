#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger le problème de seuil de similarité dans Grover
"""

import requests
import json
import time

def diagnose_grover_threshold():
    """Diagnostiquer le problème de seuil de similarité"""
    base_url = "http://localhost:8000"
    
    print("🔍 DIAGNOSTIC DU SEUIL DE SIMILARITÉ GROVER")
    print("=" * 50)
    
    # Test avec différentes requêtes pour voir les similarités
    test_queries = [
        "Antarctica is gaining ice due to climate change",
        "Climate change is causing global warming",
        "CO2 emissions are increasing",
        "Sea levels are rising"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: '{query[:30]}...'")
        
        try:
            # Faire un fact-check pour voir les similarités dans les logs
            start_time = time.time()
            response = requests.post(f"{base_url}/fact-check", 
                                   json={"message": query, "user_id": f"test_{i}", "language": "en"})
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Verdict: {result.get('verdict', 'N/A')}")
                print(f"   ⏱️ Durée: {duration:.2f}s")
                print(f"   📊 Score: {result.get('certainty_score', 0):.3f}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return True

def test_grover_with_different_thresholds():
    """Tester Grover avec différents seuils"""
    base_url = "http://localhost:8000"
    
    print("\n🎯 TEST DE GROVER AVEC DIFFÉRENTS SEUILS")
    print("=" * 50)
    
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
    test_query = "Antarctica is gaining ice due to climate change"
    
    for threshold in thresholds:
        print(f"\n📊 Test avec seuil {threshold}:")
        
        try:
            # Configurer le seuil
            config_response = requests.post(f"{base_url}/configure-grover", 
                                          json={"threshold": threshold})
            
            if config_response.status_code == 200:
                print(f"   ✅ Seuil configuré: {threshold}")
                
                # Tester Grover
                start_time = time.time()
                test_response = requests.get(f"{base_url}/grover-test")
                duration = time.time() - start_time
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    grover_result = result['results'].get('grover_correct', {})
                    
                    print(f"   🔍 Grover résultats: {grover_result.get('results_count', 0)}")
                    print(f"   ⏱️ Durée: {grover_result.get('duration', 0):.2f}s")
                    print(f"   ✅ Succès: {grover_result.get('success', False)}")
                    
                    if grover_result.get('results_count', 0) > 0:
                        print(f"   🎉 SEUIL OPTIMAL TROUVÉ: {threshold}")
                        return threshold
                else:
                    print(f"   ❌ Erreur test: {test_response.status_code}")
            else:
                print(f"   ❌ Erreur config: {config_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def optimize_grover_configuration():
    """Optimiser la configuration Grover"""
    base_url = "http://localhost:8000"
    
    print("\n⚙️ OPTIMISATION DE LA CONFIGURATION GROVER")
    print("=" * 50)
    
    # Trouver le seuil optimal
    optimal_threshold = test_grover_with_different_thresholds()
    
    if optimal_threshold:
        print(f"\n🎯 Configuration optimale trouvée:")
        print(f"   Seuil de similarité: {optimal_threshold}")
        
        # Appliquer la configuration optimale
        try:
            config_response = requests.post(f"{base_url}/configure-grover", 
                                          json={
                                              "enabled": True,
                                              "strategy": "grover_correct",
                                              "threshold": optimal_threshold
                                          })
            
            if config_response.status_code == 200:
                print(f"   ✅ Configuration appliquée avec succès")
                
                # Vérifier la configuration
                stats_response = requests.get(f"{base_url}/grover-stats")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print(f"   📊 Configuration actuelle:")
                    print(f"      - Grover activé: {stats['config']['enabled']}")
                    print(f"      - Stratégie: {stats['config']['strategy']}")
                    print(f"      - Seuil: {stats['config']['threshold']}")
                
                return optimal_threshold
            else:
                print(f"   ❌ Erreur application config: {config_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    else:
        print(f"\n⚠️ Aucun seuil optimal trouvé")
        print(f"   Recommandation: Utiliser le système classique")
        
        # Configurer le fallback
        try:
            config_response = requests.post(f"{base_url}/configure-grover", 
                                          json={
                                              "enabled": False,
                                              "strategy": "classical_quantum"
                                          })
            
            if config_response.status_code == 200:
                print(f"   ✅ Fallback configuré: système classique")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def main():
    """Fonction principale"""
    print("🚀 DIAGNOSTIC ET OPTIMISATION GROVER")
    print("=" * 60)
    
    # Étape 1: Diagnostic
    diagnose_grover_threshold()
    
    # Étape 2: Test des seuils
    optimal_threshold = test_grover_with_different_thresholds()
    
    # Étape 3: Optimisation
    final_threshold = optimize_grover_configuration()
    
    print("\n" + "=" * 60)
    print("🎉 DIAGNOSTIC TERMINÉ")
    print("=" * 60)
    
    if final_threshold:
        print(f"✅ Seuil optimal configuré: {final_threshold}")
        print(f"🚀 Grover est maintenant optimisé et fonctionnel")
    else:
        print(f"⚠️ Grover nécessite des ajustements supplémentaires")
        print(f"🔄 Le système utilise le fallback classique")
    
    print(f"\n📋 Prochaines étapes:")
    print(f"1. Tester avec: curl -X POST http://localhost:8000/fact-check ...")
    print(f"2. Vérifier les stats: curl http://localhost:8000/grover-stats")
    print(f"3. Monitorer les performances dans les logs")

if __name__ == "__main__":
    main()
