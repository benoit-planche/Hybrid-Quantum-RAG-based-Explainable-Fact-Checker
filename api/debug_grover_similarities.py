#!/usr/bin/env python3
"""
Script pour diagnostiquer les similarités dans Grover
"""

import requests
import json
import time

def debug_grover_similarities():
    """Diagnostiquer les similarités dans Grover"""
    base_url = "http://localhost:8000"
    
    print("🔍 DIAGNOSTIC DES SIMILARITÉS GROVER")
    print("=" * 50)
    
    # Test avec différents seuils pour voir le comportement
    thresholds = [0.1, 0.05, 0.01, 0.005, 0.001]
    test_query = "Antarctica is gaining ice due to climate change"
    
    print(f"📝 Test avec la requête: '{test_query[:30]}...'")
    
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
                    results_count = result.get('results_count', 0)
                    
                    print(f"   🔍 Résultats: {results_count}")
                    print(f"   ⏱️ Durée: {duration:.2f}s")
                    
                    if results_count > 0:
                        print(f"   🎉 SEUIL FONCTIONNEL TROUVÉ: {threshold}")
                        return threshold
                else:
                    print(f"   ❌ Erreur test: {test_response.status_code}")
            else:
                print(f"   ❌ Erreur config: {config_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n⚠️ Aucun seuil fonctionnel trouvé")
    print(f"   Le problème vient probablement de la normalisation des similarités")
    return None

def test_very_low_threshold():
    """Tester avec un seuil très bas"""
    base_url = "http://localhost:8000"
    
    print("\n🎯 TEST AVEC SEUIL TRÈS BAS")
    print("=" * 30)
    
    # Test avec un seuil extrêmement bas
    very_low_threshold = 0.0001
    
    try:
        # Configurer le seuil
        config_response = requests.post(f"{base_url}/configure-grover", 
                                      json={"threshold": very_low_threshold})
        
        if config_response.status_code == 200:
            print(f"✅ Seuil configuré: {very_low_threshold}")
            
            # Tester Grover
            start_time = time.time()
            test_response = requests.get(f"{base_url}/grover-test")
            duration = time.time() - start_time
            
            if test_response.status_code == 200:
                result = test_response.json()
                results_count = result.get('results_count', 0)
                
                print(f"🔍 Résultats: {results_count}")
                print(f"⏱️ Durée: {duration:.2f}s")
                
                if results_count > 0:
                    print(f"🎉 SUCCÈS avec seuil très bas: {very_low_threshold}")
                    return very_low_threshold
                else:
                    print(f"❌ Toujours 0 résultats même avec seuil très bas")
                    print(f"   Le problème est plus profond que le seuil")
            else:
                print(f"❌ Erreur test: {test_response.status_code}")
        else:
            print(f"❌ Erreur config: {config_response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return None

def main():
    """Fonction principale"""
    print("🚀 DIAGNOSTIC DES SIMILARITÉS GROVER")
    print("=" * 60)
    
    # Étape 1: Test avec différents seuils
    working_threshold = debug_grover_similarities()
    
    # Étape 2: Test avec seuil très bas
    if not working_threshold:
        working_threshold = test_very_low_threshold()
    
    print("\n" + "=" * 60)
    print("🎉 DIAGNOSTIC TERMINÉ")
    print("=" * 60)
    
    if working_threshold:
        print(f"✅ Seuil fonctionnel trouvé: {working_threshold}")
        print(f"🚀 Grover fonctionne avec ce seuil")
        
        # Configurer le seuil optimal
        try:
            base_url = "http://localhost:8000"
            config_response = requests.post(f"{base_url}/configure-grover", 
                                          json={"threshold": working_threshold})
            
            if config_response.status_code == 200:
                print(f"✅ Configuration appliquée avec succès")
        except Exception as e:
            print(f"❌ Erreur configuration: {e}")
    else:
        print(f"❌ Aucun seuil fonctionnel trouvé")
        print(f"   Le problème vient de l'implémentation de Grover")
        print(f"   Recommandation: Vérifier la normalisation des similarités")
    
    print(f"\n📋 Prochaines étapes:")
    print(f"1. Tester avec: curl http://localhost:8000/grover-test")
    print(f"2. Vérifier les stats: curl http://localhost:8000/grover-stats")
    print(f"3. Faire un fact-check: curl -X POST http://localhost:8000/fact-check ...")

if __name__ == "__main__":
    main()
