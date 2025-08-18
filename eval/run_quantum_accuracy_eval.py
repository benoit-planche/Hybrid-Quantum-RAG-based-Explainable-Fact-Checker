#!/usr/bin/env python3
"""
Script simple pour lancer l'évaluation de l'accuracy du modèle quantique
"""

import sys
import os

# Ajouter le chemin du système
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluate_quantum_app_accuracy import QuantumAppAccuracyEvaluator

def main():
    """Lancer l'évaluation avec des paramètres prédéfinis"""
    
    print("🚀 Lancement de l'évaluation de l'accuracy du modèle quantique")
    print("=" * 70)
    
    # Configuration par défaut
    config = {
        'db_folder': '../src/quantum/quantum_db/',
        'n_qubits': 8,
        'max_questions': 15  # Commencer avec un nombre raisonnable
    }
    
    print(f"🔬 Configuration:")
    print(f"  📁 Dossier QASM: {config['db_folder']}")
    print(f"  ⚛️  Qubits: {config['n_qubits']}")
    print(f"  📋 Questions: {config['max_questions']}")
    print("=" * 70)
    
    try:
        # Créer l'évaluateur
        evaluator = QuantumAppAccuracyEvaluator(
            db_folder=config['db_folder'],
            n_qubits=config['n_qubits'],
            max_questions=config['max_questions']
        )
        
        # Lancer l'évaluation
        results = evaluator.run_evaluation()
        
        print(f"\n🎉 Évaluation terminée avec succès!")
        print(f"📊 Accuracy finale: {results['performance_metrics']['accuracy']:.1%}")
        
    except Exception as e:
        print(f"❌ Évaluation échouée: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
