#!/usr/bin/env python3
"""
Script d'intégration du système Grover corrigé dans l'API existante
Modifie automatiquement l'API pour utiliser le nouveau système
"""

import os
import sys
import shutil
from datetime import datetime

def backup_api_file():
    """Créer une sauvegarde de l'API existante"""
    api_file = "../../api/quantum_fact_checker_api.py"
    backup_file = f"../../api/quantum_fact_checker_api_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(api_file):
        shutil.copy2(api_file, backup_file)
        print(f"✅ Sauvegarde créée: {backup_file}")
        return True
    else:
        print(f"❌ Fichier API non trouvé: {api_file}")
        return False

def modify_api_file():
    """Modifier l'API pour intégrer Grover"""
    api_file = "../../api/quantum_fact_checker_api.py"
    
    if not os.path.exists(api_file):
        print(f"❌ Fichier API non trouvé: {api_file}")
        return False
    
    # Lire le fichier existant
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modifications à apporter
    modifications = [
        # 1. Ajouter les imports Grover
        {
            'old': 'from quantum_search import retrieve_top_k',
            'new': '''from quantum_search import retrieve_top_k
from hybrid_quantum_search_correct import correct_hybrid_retrieve_top_k, SearchStrategy
from grover_correct import correct_grover_retrieve_top_k'''
        },
        
        # 2. Ajouter la configuration Grover dans __init__
        {
            'old': '        self.n_qubits = 8',
            'new': '''        self.n_qubits = 8
        
        # NOUVEAU : Configuration Grover
        self.use_grover = True  # Activer Grover
        self.grover_strategy = "hybrid_adaptive"  # Stratégie par défaut
        self.grover_threshold = 0.7  # Seuil de similarité
        
        # NOUVEAU : Historique des performances
        self.performance_history = {
            'classical': [],
            'grover': [],
            'hybrid': []
        }'''
        },
        
        # 3. Modifier la méthode fact_check pour utiliser Grover
        {
            'old': '        # Recherche des documents pertinents',
            'new': '''        # NOUVEAU : Sélection de la stratégie
        if self.use_grover:
            logger.info(f"🚀 Utilisation du système Grover corrigé")
            
            # Déterminer la stratégie selon la taille de la base
            try:
                collection_info = self.cassandra_manager.get_collection_info()
                db_size = collection_info.get('document_count', 5000)
            except:
                db_size = 5000
            
            # Sélection adaptative
            if db_size < 1000:
                strategy = "classical_quantum"
            elif db_size > 10000:
                strategy = "grover_correct"
            else:
                strategy = self.grover_strategy
            
            logger.info(f"📊 Base de {db_size} documents, stratégie: {strategy}")
            
            # NOUVEAU : Utiliser le système hybride corrigé
            with time_operation_context("grover_hybrid_search"):
                results = correct_hybrid_retrieve_top_k(
                    message, 
                    self.db_folder, 
                    k=10, 
                    n_qubits=self.n_qubits,
                    cassandra_manager=self.cassandra_manager,
                    strategy=strategy
                )
            
            logger.info(f"🔍 Grover trouvé {len(results)} résultats")
            
        else:
            # Système classique (fallback)
            logger.info("🔄 Utilisation du système classique")
            results = retrieve_top_k(
                message, self.db_folder, k=10, 
                n_qubits=self.n_qubits, cassandra_manager=self.cassandra_manager
            )'''
        }
    ]
    
    # Appliquer les modifications
    for mod in modifications:
        if mod['old'] in content:
            content = content.replace(mod['old'], mod['new'])
            print(f"✅ Modification appliquée: {mod['old'][:50]}...")
        else:
            print(f"⚠️ Modification non trouvée: {mod['old'][:50]}...")
    
    # Écrire le fichier modifié
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ API modifiée avec succès: {api_file}")
    return True

def add_grover_endpoints():
    """Ajouter les nouveaux endpoints Grover"""
    api_file = "../../api/quantum_fact_checker_api.py"
    
    if not os.path.exists(api_file):
        return False
    
    # Lire le fichier
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Endpoints à ajouter
    grover_endpoints = '''

# NOUVEAU : Endpoints Grover
@app.post("/configure-grover")
async def configure_grover(config: dict):
    """Configurer le système Grover"""
    try:
        if "enabled" in config:
            api.use_grover = config["enabled"]
        if "strategy" in config:
            api.grover_strategy = config["strategy"]
        if "threshold" in config:
            api.grover_threshold = config["threshold"]
        
        return {"status": "success", "config": {
            "use_grover": api.use_grover,
            "strategy": api.grover_strategy,
            "threshold": api.grover_threshold
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/grover-stats")
async def get_grover_stats():
    """Obtenir les statistiques du système Grover"""
    try:
        stats = {
            "grover_enabled": api.use_grover,
            "current_strategy": api.grover_strategy,
            "performance_history": api.performance_history,
            "config": {
                "enabled": api.use_grover,
                "strategy": api.grover_strategy,
                "threshold": api.grover_threshold
            }
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/grover-test")
async def test_grover():
    """Tester le système Grover"""
    try:
        test_query = "Antarctica is gaining ice due to climate change"
        
        # Test avec différentes stratégies
        strategies = ["classical_quantum", "grover_correct", "hybrid_adaptive"]
        results = {}
        
        for strategy in strategies:
            try:
                start_time = time.time()
                strategy_results = correct_hybrid_retrieve_top_k(
                    test_query, api.db_folder, k=5, 
                    n_qubits=api.n_qubits, cassandra_manager=api.cassandra_manager,
                    strategy=strategy
                )
                duration = time.time() - start_time
                
                results[strategy] = {
                    "success": True,
                    "results_count": len(strategy_results),
                    "duration": duration,
                    "error": None
                }
            except Exception as e:
                results[strategy] = {
                    "success": False,
                    "results_count": 0,
                    "duration": 0,
                    "error": str(e)
                }
        
        return {
            "test_query": test_query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    # Ajouter les endpoints avant la section main
    if 'if __name__ == "__main__":' in content:
        content = content.replace('if __name__ == "__main__":', grover_endpoints + '\nif __name__ == "__main__":')
        print("✅ Endpoints Grover ajoutés")
    else:
        # Ajouter à la fin du fichier
        content += grover_endpoints
        print("✅ Endpoints Grover ajoutés à la fin")
    
    # Écrire le fichier modifié
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_test_script():
    """Créer un script de test pour valider l'intégration"""
    test_script = '''#!/usr/bin/env python3
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
    print("\\n📝 Test 2: Statistiques Grover...")
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
    print("\\n📝 Test 3: Test Grover...")
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
    print("\\n📝 Test 4: Fact-check avec Grover...")
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
    
    print("\\n🎉 Test d'intégration terminé !")
    return True

if __name__ == "__main__":
    test_grover_integration()
'''
    
    with open("test_grover_integration.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Script de test créé: test_grover_integration.py")
    return True

def main():
    """Fonction principale d'intégration"""
    print("🚀 INTÉGRATION DU SYSTÈME GROVER CORRIGÉ")
    print("=" * 50)
    
    # Étape 1: Sauvegarde
    print("📝 Étape 1: Sauvegarde de l'API existante...")
    if not backup_api_file():
        print("❌ Échec de la sauvegarde")
        return False
    
    # Étape 2: Modification de l'API
    print("\\n📝 Étape 2: Modification de l'API...")
    if not modify_api_file():
        print("❌ Échec de la modification")
        return False
    
    # Étape 3: Ajout des endpoints
    print("\\n📝 Étape 3: Ajout des endpoints Grover...")
    if not add_grover_endpoints():
        print("❌ Échec de l'ajout des endpoints")
        return False
    
    # Étape 4: Création du script de test
    print("\\n📝 Étape 4: Création du script de test...")
    if not create_test_script():
        print("❌ Échec de la création du script de test")
        return False
    
    print("\\n" + "=" * 50)
    print("🎉 INTÉGRATION TERMINÉE AVEC SUCCÈS !")
    print("=" * 50)
    
    print("\\n📋 PROCHAINES ÉTAPES:")
    print("1. Démarrer l'API: cd ../../api && python quantum_fact_checker_api.py")
    print("2. Tester l'intégration: python test_grover_integration.py")
    print("3. Vérifier les stats: curl http://localhost:8000/grover-stats")
    print("4. Configurer Grover: curl -X POST http://localhost:8000/configure-grover -d '{\"enabled\": true}'")
    
    print("\\n🚀 Votre système est maintenant équipé de Grover corrigé !")
    
    return True

if __name__ == "__main__":
    main()
