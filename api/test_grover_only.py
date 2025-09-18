#!/usr/bin/env python3
"""
Test simple pour le système Grover uniquement
"""

import requests
import json
import time

def test_grover_only():
    """Tester le système Grover uniquement"""
    base_url = "http://localhost:8000"
    
    print("🧪 TEST SYSTÈME GROVER UNIQUEMENT")
    print("=" * 40)
    
    # Test 1: Vérifier que l'API fonctionne
    print("📝 Test 1: API de base...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ API accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False
    
    # Test 2: Vérifier les stats Grover
    print("\n📝 Test 2: Stats Grover...")
    try:
        response = requests.get(f"{base_url}/grover-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Seuil Grover: {stats.get('grover_threshold', 'N/A')}")
        else:
            print(f"❌ Erreur stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur stats: {e}")
    
    # Test 3: Test Grover
    print("\n📝 Test 3: Test Grover...")
    try:
        response = requests.get(f"{base_url}/grover-test")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test Grover réussi")
            print(f"   Résultats: {result.get('results_count', 0)}")
            print(f"   Durée: {result.get('duration', 0):.2f}s")
            print(f"   Seuil: {result.get('threshold', 'N/A')}")
        else:
            print(f"❌ Erreur test: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    # Test 4: Fact-check avec Grover uniquement
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
    
    print("\n🎉 Test du système Grover uniquement terminé !")
    return True

if __name__ == "__main__":
    test_grover_only()
