#!/usr/bin/env python3
"""
Script de lancement simple pour l'API Quantum Fact-Checker
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_prerequisites():
    """Vérifier les prérequis avant de lancer l'API"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier que nous sommes dans le bon répertoire
    current_dir = Path.cwd()
    if not (current_dir / "quantum_fact_checker_api.py").exists():
        print("❌ Veuillez exécuter ce script depuis le répertoire api/")
        return False
    
    # Vérifier les dépendances
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ Dépendances Python OK")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez les dépendances avec: pip install -r requirements_api.txt")
        return False
    
    # Vérifier les chemins
    quantum_db_path = Path("../src/quantum/quantum_db/")
    if not quantum_db_path.exists():
        print(f"❌ Dossier quantum_db non trouvé: {quantum_db_path}")
        return False
    else:
        qasm_files = list(quantum_db_path.glob("*.qasm"))
        print(f"✅ {len(qasm_files)} fichiers QASM trouvés")
    
    print("✅ Tous les prérequis sont satisfaits!")
    return True

def start_api():
    """Lancer l'API"""
    print("🚀 Lancement de l'API Quantum Fact-Checker...")
    print("=" * 50)
    
    try:
        # Lancer l'API avec uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "quantum_fact_checker_api:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'API...")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")

def main():
    """Fonction principale"""
    print("🔬 API Quantum Fact-Checker - Script de lancement")
    print("=" * 50)
    
    # Vérifier les prérequis
    if not check_prerequisites():
        print("\n❌ Impossible de lancer l'API. Vérifiez les prérequis.")
        sys.exit(1)
    
    print("\n📋 Informations:")
    print("   🌐 URL: http://localhost:8000")
    print("   📚 Documentation: http://localhost:8000/docs")
    print("   🔍 Santé: http://localhost:8000/health")
    print("   📊 Stats: http://localhost:8000/stats")
    print("\n💡 Pour tester l'API, ouvrez un autre terminal et lancez:")
    print("   python test_api.py")
    
    # Attendre un peu avant de lancer
    print("\n⏳ Lancement dans 3 secondes...")
    time.sleep(3)
    
    # Lancer l'API
    start_api()

if __name__ == "__main__":
    main()
