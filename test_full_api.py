#!/usr/bin/env python3
"""
Script de test pour la version complète de l'API Quantum Fact Checker
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test du endpoint de santé"""
    print("🔍 Test du endpoint /health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check réussi: {data}")
            return True
        else:
            print(f"❌ Health check échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du health check: {e}")
        return False

def test_single_fact_check():
    """Test du fact-checking simple"""
    print("\n🔍 Test du fact-checking simple...")
    
    test_message = "Le réchauffement climatique est un mythe inventé par les scientifiques"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/fact-check",
            json={"message": test_message},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Fact-check réussi:")
            print(f"   Message: {test_message}")
            print(f"   Score de certitude: {data.get('certainty_score', 'N/A')}")
            print(f"   Verdict: {data.get('verdict', 'N/A')}")
            print(f"   Temps de traitement: {data.get('processing_time', 'N/A')}s")
            return True
        else:
            print(f"❌ Fact-check échoué: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du fact-check: {e}")
        return False

def test_multiple_fact_checks():
    """Test de plusieurs fact-checks séquentiels"""
    print("\n🔍 Test de plusieurs fact-checks...")
    
    test_messages = [
        "Les émissions de CO2 ont augmenté de 50% depuis 1990",
        "Les énergies renouvelables sont plus chères que les fossiles",
        "La fonte des glaces arctiques s'accélère"
    ]
    
    results = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"   Test {i}/3: {message[:50]}...")
        try:
            response = requests.post(
                f"{API_BASE_URL}/fact-check",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "message": message,
                    "score": data.get('certainty_score'),
                    "verdict": data.get('verdict'),
                    "time": data.get('processing_time')
                })
                print(f"      ✅ Score: {data.get('certainty_score'):.3f}, Verdict: {data.get('verdict')}")
            else:
                print(f"      ❌ Échec: {response.status_code}")
                results.append({"message": message, "error": f"HTTP {response.status_code}"})
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
            results.append({"message": message, "error": str(e)})
    
    return results

def main():
    """Fonction principale de test"""
    print("🚀 Test de l'API Quantum Fact Checker (Version Complète)")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("❌ L'API n'est pas accessible. Arrêt des tests.")
        return
    
    # Test 2: Fact-checking simple
    if not test_single_fact_check():
        print("❌ Le fact-checking simple a échoué.")
        return
    
    # Test 3: Multiple fact-checks
    results = test_multiple_fact_checks()
    
    # Résumé
    print("\n📊 Résumé des tests:")
    print("-" * 40)
    successful_tests = [r for r in results if 'error' not in r]
    failed_tests = [r for r in results if 'error' in r]
    
    print(f"✅ Tests réussis: {len(successful_tests)}/{len(results)}")
    print(f"❌ Tests échoués: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_score = sum(r['score'] for r in successful_tests) / len(successful_tests)
        avg_time = sum(r['time'] for r in successful_tests) / len(successful_tests)
        print(f"📈 Score moyen: {avg_score:.3f}")
        print(f"⏱️  Temps moyen: {avg_time:.2f}s")
    
    print("\n🎉 Tests terminés !")

if __name__ == "__main__":
    main()
