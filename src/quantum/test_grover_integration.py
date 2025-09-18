#!/usr/bin/env python3
"""
Script de test pour valider l'intégration Grover
"""

import requests
import json
import time

def test_grover_integration():
    """Tester l'intégration Grover"""
    base_url = "http://localhost:8000"
    
    print("🧪 TEST D'INTÉGRATION GROVER")
    print("=" * 40)
    
    # Test 1: Vérifier que l'API fonctionne
    print("📝 Test 1: Vérification API...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ API accessible")
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion API: {e}")
        return False
    
    # Test 2: Vérifier les stats Grover
    print("\n📝 Test 2: Statistiques Grover...")
    try:
        response = requests.get(f"{base_url}/grover-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Grover activé: {stats.get('grover_enabled', False)}")
            print(f"✅ Stratégie: {stats.get('current_strategy', 'N/A')}")
        else:
            print(f"❌ Erreur stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur stats: {e}")
    
    # Test 3: Test Grover
    print("\n📝 Test 3: Test Grover...")
    try:
        response = requests.get(f"{base_url}/grover-test")
        if response.status_code == 200:
            test_results = response.json()
            print("✅ Test Grover réussi")
            for strategy, result in test_results['results'].items():
                status = "✅" if result['success'] else "❌"
                print(f"   {strategy}: {status} ({result['results_count']} résultats, {result['duration']:.2f}s)")
        else:
            print(f"❌ Erreur test: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    # Test 4: Fact-check avec Grover
    print("\n📝 Test 4: Fact-check avec Grover...")
    try:
        test_data = {
            "message": "Antarctica is gaining ice due to climate change",
            "user_id": "test_user",
            "language": "en"
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/fact-check", json=test_data)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Fact-check réussi en {duration:.2f}s")
            print(f"   Verdict: {result.get('verdict', 'N/A')}")
            print(f"   Confiance: {result.get('confidence_level', 'N/A')}")
            print(f"   Sources: {len(result.get('sources_used', []))}")
        else:
            print(f"❌ Erreur fact-check: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur fact-check: {e}")
    
    print("\n🎉 Test d'intégration terminé !")
    return True

if __name__ == "__main__":
    test_grover_integration()
