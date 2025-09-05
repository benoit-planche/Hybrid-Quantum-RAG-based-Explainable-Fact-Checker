#!/usr/bin/env python3
"""
Test simple pour vérifier l'intégration Grover
"""

import requests
import json

def test_grover_endpoints():
    """Tester les endpoints Grover"""
    base_url = "http://localhost:8000"
    
    print("🧪 TEST SIMPLE DES ENDPOINTS GROVER")
    print("=" * 40)
    
    # Test 1: Vérifier que l'API fonctionne
    print("📝 Test 1: API de base...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ API accessible: {response.status_code}")
        print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False
    
    # Test 2: Vérifier les stats Grover
    print("\n📝 Test 2: Stats Grover...")
    try:
        response = requests.get(f"{base_url}/grover-stats")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats Grover: {json.dumps(stats, indent=2)}")
        else:
            print(f"❌ Erreur stats: {response.text}")
    except Exception as e:
        print(f"❌ Erreur stats: {e}")
    
    # Test 3: Configuration Grover
    print("\n📝 Test 3: Configuration Grover...")
    try:
        config_data = {"strategy": "grover_correct"}
        response = requests.post(f"{base_url}/configure-grover", json=config_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Configuration: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Erreur config: {response.text}")
    except Exception as e:
        print(f"❌ Erreur config: {e}")
    
    # Test 4: Test Grover
    print("\n📝 Test 4: Test Grover...")
    try:
        response = requests.get(f"{base_url}/grover-test")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test Grover: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Erreur test: {response.text}")
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    print("\n🎉 Test terminé !")
    return True

if __name__ == "__main__":
    test_grover_endpoints()
