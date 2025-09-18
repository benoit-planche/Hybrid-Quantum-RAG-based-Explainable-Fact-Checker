#!/usr/bin/env python3
"""
Script pour lancer l'API en mode 4 qubits
"""

import os
import sys
import shutil
import subprocess

def backup_original_api():
    """Sauvegarder l'API originale"""
    original_file = "quantum_fact_checker_api.py"
    backup_file = "quantum_fact_checker_api_8qubits_backup.py"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✅ API originale sauvegardée: {backup_file}")
        return True
    else:
        print(f"❌ Fichier API non trouvé: {original_file}")
        return False

def modify_api_for_4qubits():
    """Modifier l'API pour utiliser 4 qubits"""
    print("🔧 Modification de l'API pour 4 qubits...")
    
    # Lire le fichier original
    with open("quantum_fact_checker_api.py", "r") as f:
        content = f.read()
    
    # Modifications pour 4 qubits
    modifications = [
        # Changer le dossier des circuits
        ('self.db_folder = "../src/quantum/quantum_db_8qubits/"', 'self.db_folder = "../src/quantum/qasm_circuits_4qubits/"'),
        # Changer le nombre de qubits
        ('self.n_qubits = 8', 'self.n_qubits = 4'),
        # Changer le commentaire
        ('# Fixé à 8 pour correspondre à l\'encodage PCA', '# Fixé à 4 pour correspondre à l\'encodage PCA 4 qubits'),
    ]
    
    # Appliquer les modifications
    for old, new in modifications:
        if old in content:
            content = content.replace(old, new)
            print(f"   ✅ Modification: {old} → {new}")
        else:
            print(f"   ⚠️ Texte non trouvé: {old}")
    
    # Écrire le fichier modifié
    with open("quantum_fact_checker_api.py", "w") as f:
        f.write(content)
    
    print("✅ API modifiée pour 4 qubits")

def create_4qubits_config():
    """Créer un fichier de configuration 4 qubits"""
    config_content = """# Configuration API 4 qubits
QUANTUM_MODE=4qubits
QUANTUM_DB_FOLDER=../src/quantum/qasm_circuits_4qubits/
QUANTUM_N_QUBITS=4
QUANTUM_K_RESULTS=10
"""
    
    with open("config_4qubits.env", "w") as f:
        f.write(config_content)
    
    print("✅ Configuration 4 qubits créée")

def launch_4qubits_api():
    """Lancer l'API 4 qubits"""
    print("🚀 Lancement de l'API 4 qubits...")
    
    try:
        # Lancer l'API
        process = subprocess.Popen([
            sys.executable, "quantum_fact_checker_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("✅ API 4 qubits lancée en arrière-plan")
        print(f"   PID: {process.pid}")
        print("   URL: http://localhost:8000")
        print("   Documentation: http://localhost:8000/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ Erreur lancement API: {e}")
        return None

def test_4qubits_api():
    """Tester l'API 4 qubits"""
    print("\n🧪 Test de l'API 4 qubits...")
    
    import time
    import requests
    
    # Attendre que l'API démarre
    print("   ⏳ Attente du démarrage de l'API...")
    time.sleep(5)
    
    try:
        # Test de santé
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("   ✅ API répond (health check)")
        else:
            print(f"   ⚠️ API répond avec code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API non accessible: {e}")
        return False
    
    # Test de fact-checking
    try:
        test_payload = {
            "message": "Antarctica is gaining ice due to climate change",
            "user_id": "test_user",
            "language": "en"
        }
        
        response = requests.post(
            "http://localhost:8000/fact-check",
            json=test_payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Fact-checking réussi: {result.get('verdict', 'N/A')}")
            print(f"   ⏱️ Temps de traitement: {result.get('processing_time', 'N/A')}s")
        else:
            print(f"   ❌ Fact-checking échoué: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur test fact-checking: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🎯 Lancement de l'API Quantum Fact-Checker en mode 4 qubits")
    print("=" * 60)
    
    # 1. Sauvegarder l'API originale
    if not backup_original_api():
        return
    
    # 2. Modifier l'API pour 4 qubits
    modify_api_for_4qubits()
    
    # 3. Créer la configuration
    create_4qubits_config()
    
    # 4. Lancer l'API
    api_process = launch_4qubits_api()
    if not api_process:
        return
    
    # 5. Tester l'API
    if test_4qubits_api():
        print("\n🎉 API 4 qubits opérationnelle !")
        print("\n📝 Utilisation:")
        print("   - Test simple: curl http://localhost:8000/health")
        print("   - Fact-checking: curl -X POST http://localhost:8000/fact-check -H 'Content-Type: application/json' -d '{\"message\": \"test\"}'")
        print("   - Documentation: http://localhost:8000/docs")
        print("\n⚠️ Pour arrêter l'API: Ctrl+C ou kill", api_process.pid)
    else:
        print("\n❌ Tests de l'API échoués")
        api_process.terminate()

if __name__ == "__main__":
    main()