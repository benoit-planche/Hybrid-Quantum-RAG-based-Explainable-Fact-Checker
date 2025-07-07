#!/usr/bin/env python3
"""
Test rapide de l'évaluation RAG avec ChromaDB
"""

import asyncio
import sys
import os

# Ajouter le dossier system au path
sys.path.append('../system')

from evaluate_rag_chromadb import ComprehensiveRAGEvaluator
from climate_dataset import get_random_subset

async def quick_test():
    """Test rapide avec 5 questions"""
    
    print("🚀 TEST RAPIDE DE L'ÉVALUATION RAG")
    print("=" * 40)
    
    # Initialiser l'évaluateur
    evaluator = ComprehensiveRAGEvaluator(embedding_model="llama2:7b")
    
    # Vérifier ChromaDB
    collection_info = evaluator.chroma_manager.get_collection_info()
    if collection_info.get('document_count', 0) == 0:
        print("❌ Aucun document dans ChromaDB")
        return
    
    print(f"✅ ChromaDB: {collection_info['document_count']} documents")
    
    # Test avec 5 questions
    test_cases = get_random_subset(5)
    
    print(f"\n🧪 Test avec 5 questions...")
    
    # Évaluer
    results = await evaluator.evaluate_rag_system(test_cases)
    
    # Afficher les résultats
    evaluator.print_results(results)
    
    print("\n✅ Test rapide terminé !")

if __name__ == "__main__":
    asyncio.run(quick_test()) 