#!/usr/bin/env python3
"""
Script pour exécuter l'évaluation MMR avec différents paramètres
"""

import asyncio
import sys
import os
from datetime import datetime

# Ajouter le chemin du système
sys.path.append('../system')

from evaluate_rag_chromadb_mmr import MMRRAGEvaluator

async def run_mmr_evaluation(lambda_param=0.5, max_questions=10):
    """
    Exécuter l'évaluation MMR
    
    Args:
        lambda_param: Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)
        max_questions: Nombre de questions à tester
    """
    print(f"🚀 Démarrage de l'évaluation MMR avec λ={lambda_param}")
    print(f"📋 {max_questions} questions à tester")
    print("=" * 60)
    
    # Créer l'évaluateur
    evaluator = MMRRAGEvaluator(
        embedding_model="llama2:7b",
        lambda_param=lambda_param
    )
    
    # Évaluer le système
    results = await evaluator.evaluate_rag_system(max_questions=max_questions)
    
    # Afficher les résultats
    evaluator.print_results(results)
    
    # Sauvegarder les résultats avec le paramètre lambda dans le nom
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_eval_mmr_lambda{lambda_param}_{timestamp}.json"
    evaluator.save_results(results, filename)
    
    print(f"\n✅ Évaluation MMR terminée avec λ={lambda_param}")

async def run_comparison_study():
    """Exécuter une étude comparative avec différents paramètres lambda"""
    print("🔬 Étude comparative MMR avec différents paramètres λ")
    print("=" * 60)
    
    lambda_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    max_questions = 5  # Moins de questions pour l'étude comparative
    
    for lambda_param in lambda_values:
        print(f"\n{'='*20} λ = {lambda_param} {'='*20}")
        await run_mmr_evaluation(lambda_param=lambda_param, max_questions=max_questions)
        print(f"{'='*60}")

async def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Évaluation MMR pour le fact-checker')
    parser.add_argument('--lambda_param', type=float, default=0.5, 
                       help='Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)')
    parser.add_argument('--questions', type=int, default=10,
                       help='Nombre de questions à tester (défaut: 10)')
    parser.add_argument('--comparison', action='store_true',
                       help='Exécuter une étude comparative avec différents λ')
    
    args = parser.parse_args()
    
    if args.comparison:
        await run_comparison_study()
    else:
        await run_mmr_evaluation(lambda_param=args.lambda_param, max_questions=args.questions)

if __name__ == "__main__":
    asyncio.run(main()) 