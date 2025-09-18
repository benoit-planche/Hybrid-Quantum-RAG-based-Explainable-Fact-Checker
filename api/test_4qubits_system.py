#!/usr/bin/env python3
"""
Script de test complet du système 4 qubits
"""

import sys
import os
sys.path.append('../system')
sys.path.append('.')

import numpy as np
import time
from qiskit import transpile
from qiskit_aer import Aer

def test_4qubits_components():
    """Tester tous les composants du système 4 qubits"""
    print("🔬 Test complet du système 4 qubits...")
    
    # 1. Vérifier les circuits QASM
    print("\n📁 Vérification des circuits QASM 4 qubits...")
    qasm_dir = "../src/quantum/qasm_circuits_4qubits"
    if os.path.exists(qasm_dir):
        qasm_files = [f for f in os.listdir(qasm_dir) if f.endswith('.qasm')]
        print(f"   ✅ {len(qasm_files)} circuits QASM trouvés")
        
        # Vérifier quelques circuits
        sample_files = qasm_files[:3]
        for file in sample_files:
            file_path = os.path.join(qasm_dir, file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'OPENQASM' in content:
                        print(f"   ✅ {file}: Format QASM valide")
                    else:
                        print(f"   ⚠️ {file}: Format suspect")
            except Exception as e:
                print(f"   ❌ {file}: Erreur lecture - {e}")
    else:
        print("   ❌ Dossier qasm_circuits_4qubits non trouvé")
        return False
    
    # 2. Vérifier le modèle PCA
    print("\n🔍 Vérification du modèle PCA...")
    pca_files = [f for f in os.listdir('../src/quantum') if 'pca' in f.lower() and f.endswith('.pkl')]
    if pca_files:
        print(f"   ✅ Modèles PCA trouvés: {pca_files}")
        
        # Essayer de charger le PCA principal
        try:
            import pickle
            with open('../src/quantum/pca_model.pkl', 'rb') as f:
                pca = pickle.load(f)
            print(f"   ✅ PCA principal chargé: {pca.n_components_} composantes")
        except Exception as e:
            print(f"   ❌ Erreur chargement PCA: {e}")
            return False
    else:
        print("   ❌ Aucun modèle PCA trouvé")
        return False
    
    # 3. Vérifier Cassandra
    print("\n📊 Vérification de Cassandra...")
    try:
        from cassandra.cluster import Cluster
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect('fact_checker_keyspace')
        
        # Compter les documents
        result = session.execute("SELECT COUNT(*) FROM fact_checker_keyspace.fact_checker_docs")
        count = result.one()[0]
        print(f"   ✅ Cassandra connecté: {count} documents")
        
        session.shutdown()
        cluster.shutdown()
    except Exception as e:
        print(f"   ❌ Erreur Cassandra: {e}")
        return False
    
    # 4. Vérifier Ollama
    print("\n🤖 Vérification d'Ollama...")
    try:
        # Essayer d'importer depuis le bon chemin
        sys.path.append('../system')
        from ollama_utils import OllamaClient
        client = OllamaClient()
        test_response = client.generate("Test", max_tokens=5)
        print(f"   ✅ Ollama connecté: {len(test_response)} caractères générés")
    except Exception as e:
        print(f"   ❌ Erreur Ollama: {e}")
        print("   💡 Vérifiez que le dossier system/ est accessible")
        return False
    
    print("\n🎉 Tous les composants sont fonctionnels !")
    return True

def test_quantum_search_4qubits():
    """Tester la recherche quantique 4 qubits"""
    print("\n🚀 Test de la recherche quantique 4 qubits...")
    
    try:
        # Importer le système de recherche 4 qubits
        from quantum_search_4qubits import QuantumSearch4Qubits
        
        # Initialiser le système
        print("   🔧 Initialisation du système de recherche...")
        quantum_search = QuantumSearch4Qubits()
        
        # Test de recherche
        test_query = "Antarctica ice loss climate change"
        print(f"   🔍 Test de recherche: '{test_query}'")
        
        start_time = time.time()
        results, search_time = quantum_search.search_documents_quantum_4qubits(test_query, n_results=5)
        end_time = time.time()
        
        print(f"   ⏱️ Temps de recherche: {end_time - start_time:.2f}s")
        print(f"   📊 Résultats trouvés: {len(results)}")
        
        # Afficher les premiers résultats
        for i, result in enumerate(results[:3]):
            print(f"     {i+1}. {result.get('chunk_id', 'N/A')}: {result.get('similarity', 0):.4f}")
            text_preview = result.get('text', '')[:100] if result.get('text') else 'Texte non disponible'
            print(f"        Texte: {text_preview}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur recherche quantique: {e}")
        return False

def test_quantum_circuit_loading():
    """Tester le chargement des circuits quantiques"""
    print("\n⚡ Test de chargement des circuits quantiques...")
    
    try:
        # Ajouter le chemin vers src/quantum
        quantum_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'quantum')
        if quantum_path not in sys.path:
            sys.path.append(quantum_path)
        
        from quantum_encoder_4qubits import load_qasm_circuit_4qubits
        
        # Charger quelques circuits
        qasm_dir = os.path.join(quantum_path, "qasm_circuits_4qubits")
        qasm_files = [f for f in os.listdir(qasm_dir) if f.endswith('.qasm')][:3]
        
        for file in qasm_files:
            file_path = os.path.join(qasm_dir, file)
            try:
                circuit = load_qasm_circuit_4qubits(file_path)
                print(f"   ✅ {file}: {circuit.num_qubits} qubits, {len(circuit.data)} opérations")
            except Exception as e:
                print(f"   ❌ {file}: Erreur chargement - {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur test circuits: {e}")
        return False

def main():
    """Fonction principale"""
    print("🎯 Test complet du système Quantum 4 qubits")
    print("=" * 50)
    
    # Test des composants
    if not test_4qubits_components():
        print("\n❌ Tests des composants échoués")
        return
    
    # Test du chargement des circuits
    if not test_quantum_circuit_loading():
        print("\n❌ Tests des circuits échoués")
        return
    
    # Test de la recherche quantique
    if not test_quantum_search_4qubits():
        print("\n❌ Tests de recherche échoués")
        return
    
    print("\n" + "=" * 50)
    print("🎉 TOUS LES TESTS SONT RÉUSSIS !")
    print("✅ Votre système 4 qubits est opérationnel")
    print("\n📝 Prochaines étapes:")
    print("1. Lancer l'API avec 4 qubits")
    print("2. Tester les performances")
    print("3. Comparer avec le système 8 qubits")

if __name__ == "__main__":
    main()
