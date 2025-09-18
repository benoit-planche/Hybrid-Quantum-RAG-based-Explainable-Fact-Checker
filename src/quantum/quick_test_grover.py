#!/usr/bin/env python3
"""
Test rapide de l'intégration Grover
"""

import os
import sys
import numpy as np

# Ajouter les chemins nécessaires
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(os.path.dirname(current_dir), 'system')
sys.path.insert(0, system_dir)
sys.path.insert(0, current_dir)

def test_grover_basic():
    """Test basique de Grover sans Cassandra"""
    print("🧪 TEST BASIQUE DE GROVER")
    print("=" * 30)
    
    try:
        from grover_search import GroverDocumentSearch
        
        # Créer une instance
        grover = GroverDocumentSearch(n_qubits=4, threshold=0.5)
        print("✅ GroverDocumentSearch créé")
        
        # Test avec des données factices
        query_embedding = np.random.rand(10)
        document_embeddings = [np.random.rand(10) for _ in range(8)]
        
        print(f"📊 Test avec {len(document_embeddings)} documents")
        
        # Test de l'oracle
        oracle = grover.create_relevance_oracle(query_embedding, document_embeddings)
        print(f"✅ Oracle créé: {oracle.num_qubits} qubits")
        
        # Test de l'opérateur de diffusion
        diffusion = grover.create_diffusion_operator(4)
        print(f"✅ Opérateur de diffusion créé: {diffusion.num_qubits} qubits")
        
        print("🎉 Test basique réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le test basique: {e}")
        return False

def test_hybrid_system():
    """Test du système hybride"""
    print("\n🔧 TEST SYSTÈME HYBRIDE")
    print("=" * 30)
    
    try:
        from hybrid_quantum_search import HybridQuantumSearch, SearchStrategy
        
        # Créer une instance
        hybrid = HybridQuantumSearch(strategy=SearchStrategy.HYBRID_ADAPTIVE)
        print("✅ HybridQuantumSearch créé")
        
        # Test de sélection adaptative
        strategy1 = hybrid.adaptive_strategy_selection(50, 1000)
        strategy2 = hybrid.adaptive_strategy_selection(50, 20000)
        
        print(f"📊 Stratégie pour petite base: {strategy1.value}")
        print(f"📊 Stratégie pour grande base: {strategy2.value}")
        
        # Test des statistiques
        stats = hybrid.get_performance_stats()
        print(f"📈 Statistiques: {len(stats)} stratégies enregistrées")
        
        print("🎉 Test système hybride réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le test hybride: {e}")
        return False

def test_imports():
    """Test des imports"""
    print("📦 TEST DES IMPORTS")
    print("=" * 20)
    
    imports_to_test = [
        ("grover_search", "GroverDocumentSearch"),
        ("hybrid_quantum_search", "HybridQuantumSearch"),
        ("hybrid_quantum_search", "SearchStrategy"),
        ("quantum_search", "retrieve_top_k"),
    ]
    
    success_count = 0
    
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name)
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")
    
    print(f"\n📊 Imports réussis: {success_count}/{len(imports_to_test)}")
    return success_count == len(imports_to_test)

def main():
    """Fonction principale"""
    print("🚀 TEST RAPIDE D'INTÉGRATION GROVER")
    print("=" * 50)
    
    # Tests
    test1 = test_imports()
    test2 = test_grover_basic()
    test3 = test_hybrid_system()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    tests = [
        ("Imports", test1),
        ("Grover basique", test2),
        ("Système hybride", test3)
    ]
    
    for test_name, result in tests:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{test_name:20} | {status}")
    
    success_rate = sum(1 for _, result in tests if result) / len(tests)
    print(f"\n🎯 Taux de réussite: {success_rate:.1%}")
    
    if success_rate == 1.0:
        print("🎉 Tous les tests sont passés ! L'intégration Grover est prête.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()
