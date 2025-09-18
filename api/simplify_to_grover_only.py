#!/usr/bin/env python3
"""
Script pour simplifier le système et utiliser uniquement Grover
Retire tout le système hybride complexe
"""

import os
import shutil
from datetime import datetime

def backup_api_file():
    """Créer une sauvegarde de l'API existante"""
    api_file = "quantum_fact_checker_api.py"
    backup_file = f"quantum_fact_checker_api_backup_grover_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(api_file):
        shutil.copy2(api_file, backup_file)
        print(f"✅ Sauvegarde créée: {backup_file}")
        return True
    else:
        print(f"❌ Fichier API non trouvé: {api_file}")
        return False

def simplify_api_to_grover_only():
    """Simplifier l'API pour utiliser uniquement Grover"""
    api_file = "quantum_fact_checker_api.py"
    
    if not os.path.exists(api_file):
        print(f"❌ Fichier API non trouvé: {api_file}")
        return False
    
    # Lire le fichier existant
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Modifications pour utiliser uniquement Grover
    modifications = [
        # 1. Simplifier les imports
        {
            'old': '''from quantum_search import retrieve_top_k
from hybrid_quantum_search_correct import correct_hybrid_retrieve_top_k, SearchStrategy
from grover_correct import correct_grover_retrieve_top_k''',
            'new': '''from grover_correct import correct_grover_retrieve_top_k'''
        },
        
        # 2. Simplifier la configuration
        {
            'old': '''        # NOUVEAU : Configuration Grover
        self.use_grover = True  # Activer Grover
        self.grover_strategy = "hybrid_adaptive"  # Stratégie par défaut
        self.grover_threshold = 0.7  # Seuil de similarité
        
        # NOUVEAU : Historique des performances
        self.performance_history = {
            'classical': [],
            'grover': [],
            'hybrid': []
        }''',
            'new': '''        # Configuration Grover uniquement
        self.grover_threshold = 0.4  # Seuil de similarité optimisé'''
        },
        
        # 3. Simplifier la méthode fact_check
        {
            'old': '''        # NOUVEAU : Sélection de la stratégie
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
            )''',
            'new': '''        # Utilisation exclusive de Grover
        logger.info(f"🚀 Utilisation exclusive de l'algorithme de Grover")
        
        with time_operation_context("grover_search"):
            results = correct_grover_retrieve_top_k(
                message, 
                self.db_folder, 
                k=10, 
                n_qubits=self.n_qubits,
                cassandra_manager=self.cassandra_manager
            )
        
        logger.info(f"🔍 Grover trouvé {len(results)} résultats")'''
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
    
    print(f"✅ API simplifiée pour utiliser uniquement Grover: {api_file}")
    return True

def simplify_grover_endpoints():
    """Simplifier les endpoints Grover"""
    api_file = "quantum_fact_checker_api.py"
    
    if not os.path.exists(api_file):
        return False
    
    # Lire le fichier
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Endpoints simplifiés
    simplified_endpoints = '''

# Endpoints Grover simplifiés
@app.post("/configure-grover")
async def configure_grover(config: dict):
    """Configurer le seuil de similarité Grover"""
    try:
        if "threshold" in config:
            api_instance.grover_threshold = config["threshold"]
        
        return {"status": "success", "config": {
            "threshold": api_instance.grover_threshold
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/grover-stats")
async def get_grover_stats():
    """Obtenir les statistiques du système Grover"""
    try:
        stats = {
            "grover_threshold": api_instance.grover_threshold,
            "config": {
                "threshold": api_instance.grover_threshold
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
        
        start_time = time.time()
        results = correct_grover_retrieve_top_k(
            test_query, api_instance.db_folder, k=5, 
            n_qubits=api_instance.n_qubits, cassandra_manager=api_instance.cassandra_manager
        )
        duration = time.time() - start_time
        
        return {
            "test_query": test_query,
            "results_count": len(results),
            "duration": duration,
            "threshold": api_instance.grover_threshold,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    # Remplacer les anciens endpoints par les nouveaux
    if '# NOUVEAU : Endpoints Grover' in content:
        # Trouver le début et la fin des anciens endpoints
        start_marker = '# NOUVEAU : Endpoints Grover'
        end_marker = 'if __name__ == "__main__":'
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Remplacer la section
            before = content[:start_pos]
            after = content[end_pos:]
            content = before + simplified_endpoints + '\n' + after
            print("✅ Endpoints Grover simplifiés")
        else:
            print("⚠️ Marqueurs des endpoints non trouvés")
    else:
        # Ajouter à la fin du fichier
        content += simplified_endpoints
        print("✅ Endpoints Grover ajoutés")
    
    # Écrire le fichier modifié
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_simple_test_script():
    """Créer un script de test simple pour Grover uniquement"""
    test_script = '''#!/usr/bin/env python3
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
    print("\\n📝 Test 2: Stats Grover...")
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
    print("\\n📝 Test 3: Test Grover...")
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
    
    print("\\n🎉 Test du système Grover uniquement terminé !")
    return True

if __name__ == "__main__":
    test_grover_only()
'''
    
    with open("test_grover_only.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Script de test créé: test_grover_only.py")
    return True

def main():
    """Fonction principale de simplification"""
    print("🚀 SIMPLIFICATION DU SYSTÈME POUR GROVER UNIQUEMENT")
    print("=" * 60)
    
    # Étape 1: Sauvegarde
    print("📝 Étape 1: Sauvegarde de l'API existante...")
    if not backup_api_file():
        print("❌ Échec de la sauvegarde")
        return False
    
    # Étape 2: Simplification de l'API
    print("\\n📝 Étape 2: Simplification de l'API pour Grover uniquement...")
    if not simplify_api_to_grover_only():
        print("❌ Échec de la simplification")
        return False
    
    # Étape 3: Simplification des endpoints
    print("\\n📝 Étape 3: Simplification des endpoints...")
    if not simplify_grover_endpoints():
        print("❌ Échec de la simplification des endpoints")
        return False
    
    # Étape 4: Création du script de test
    print("\\n📝 Étape 4: Création du script de test...")
    if not create_simple_test_script():
        print("❌ Échec de la création du script de test")
        return False
    
    print("\\n" + "=" * 60)
    print("🎉 SIMPLIFICATION TERMINÉE AVEC SUCCÈS !")
    print("=" * 60)
    
    print("\\n📋 PROCHAINES ÉTAPES:")
    print("1. Redémarrer l'API: pkill -f quantum_fact_checker_api.py && python quantum_fact_checker_api.py")
    print("2. Tester le système: python test_grover_only.py")
    print("3. Configurer le seuil: curl -X POST http://localhost:8000/configure-grover -d '{\"threshold\": 0.4}'")
    print("4. Vérifier les stats: curl http://localhost:8000/grover-stats")
    
    print("\\n🚀 Votre système utilise maintenant uniquement l'algorithme de Grover !")
    
    return True

if __name__ == "__main__":
    main()
