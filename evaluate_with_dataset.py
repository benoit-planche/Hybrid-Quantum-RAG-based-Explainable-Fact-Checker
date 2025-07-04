#!/usr/bin/env python3
"""
Évaluation du fact-checker avec le dataset complet
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancy, ContextRelevancy, Faithfulness
from deepeval.test_case import LLMTestCase
from ollama_utils import OllamaClient, OllamaEmbeddings
from ollama_config import config
from pinecone import Pinecone
from climate_dataset import CLIMATE_DATASET, get_dataset_by_category, get_random_subset

# Load environment variables
load_dotenv()

class ComprehensiveFactCheckerEvaluator:
    """Évaluateur complet pour le système de fact-checking"""
    
    def __init__(self, use_rag=True):
        self.ollama_client = OllamaClient()
        self.use_rag = use_rag
        
        if use_rag:
            self.embeddings = OllamaEmbeddings()
            # Initialize Pinecone
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            self.index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    async def get_model_response(self, question: str) -> str:
        """Obtenir la réponse du modèle pour une question donnée"""
        
        if self.use_rag:
            return await self.get_rag_response(question)
        else:
            return await self.get_direct_response(question)
    
    async def get_direct_response(self, question: str) -> str:
        """Obtenir une réponse directe sans RAG"""
        
        prompt = f"""
        Tu es un expert en fact-checking sur le changement climatique. 
        Réponds à la question suivante de manière factuelle et précise, 
        en te basant sur les connaissances scientifiques actuelles.
        
        Question: {question}
        
        Réponse:
        """
        
        try:
            response = await self.ollama_client.generate_response(prompt)
            return response
        except Exception as e:
            print(f"Erreur lors de la génération de réponse: {e}")
            return "Erreur lors de la génération de réponse"
    
    async def get_rag_response(self, question: str) -> str:
        """Obtenir une réponse RAG pour une question donnée"""
        
        try:
            # 1. Générer l'embedding de la question
            question_embedding = self.embeddings.embed_query(question)
            
            # 2. Rechercher dans Pinecone
            search_results = self.index.query(
                vector=question_embedding,
                top_k=5,
                include_metadata=True
            )
            
            # 3. Extraire le contexte
            context_parts = []
            for match in search_results.matches:
                if 'text' in match.metadata:
                    context_parts.append(match.metadata['text'])
            
            context = "\n".join(context_parts)
            
            # 4. Générer la réponse avec le contexte
            prompt = f"""
            Tu es un expert en fact-checking sur le changement climatique.
            
            Contexte scientifique:
            {context}
            
            Question: {question}
            
            Réponds de manière factuelle et précise en te basant sur le contexte fourni.
            Si le contexte ne contient pas d'information pertinente, indique-le clairement.
            
            Réponse:
            """
            
            response = await self.ollama_client.generate_response(prompt)
            return response
            
        except Exception as e:
            print(f"Erreur lors de la génération de réponse RAG: {e}")
            return f"Erreur lors de la génération de réponse: {e}"
    
    def create_llm_test_cases(self, test_cases):
        """Créer des cas de test LLMTestCase pour DeepEval"""
        
        llm_test_cases = []
        
        for i, test_case in enumerate(test_cases):
            llm_test_cases.append(
                LLMTestCase(
                    input=test_case["question"],
                    actual_output="",  # Sera rempli lors de l'évaluation
                    expected_output=test_case["expected_answer"],
                    context=test_case.get("category", "")
                )
            )
        
        return llm_test_cases
    
    async def evaluate_model(self, test_cases=None, max_questions=50):
        """Évaluer le modèle avec DeepEval"""
        
        if test_cases is None:
            # Utiliser un sous-ensemble aléatoire du dataset complet
            test_cases = get_random_subset(max_questions)
        
        llm_test_cases = self.create_llm_test_cases(test_cases)
        
        print(f"🧪 Évaluation du fact-checker ({'RAG' if self.use_rag else 'Direct'})")
        print("=" * 60)
        print(f"📋 {len(test_cases)} cas de test")
        
        # Générer les réponses du modèle
        print("🔄 Génération des réponses du modèle...")
        for i, test_case in enumerate(test_cases):
            print(f"  [{i+1}/{len(test_cases)}] {test_case['question'][:60]}...")
            response = await self.get_model_response(test_case['question'])
            llm_test_cases[i].actual_output = response
        
        # Définir les métriques d'évaluation
        metrics = [
            AnswerRelevancy(threshold=0.7),
            ContextRelevancy(threshold=0.7),
            Faithfulness(threshold=0.7)
        ]
        
        # Lancer l'évaluation
        print("\n📊 Lancement de l'évaluation...")
        results = evaluate(
            llm_test_cases,
            metrics=metrics
        )
        
        # Afficher les résultats
        print("\n📈 Résultats de l'évaluation:")
        print("=" * 40)
        
        for metric in metrics:
            print(f"{metric.__class__.__name__}: {results[metric.__class__.__name__]:.3f}")
        
        # Analyse par catégorie
        print("\n📊 Analyse par catégorie:")
        categories = {}
        for test_case in test_cases:
            cat = test_case["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(test_case)
        
        for cat, cases in categories.items():
            print(f"  {cat}: {len(cases)} questions")
        
        return results, test_cases, llm_test_cases

async def main():
    """Fonction principale"""
    
    print("🎯 Évaluation complète du fact-checker")
    print("=" * 50)
    
    # Évaluation avec RAG
    print("\n1️⃣ Évaluation avec RAG...")
    rag_evaluator = ComprehensiveFactCheckerEvaluator(use_rag=True)
    rag_results, rag_test_cases, rag_llm_cases = await rag_evaluator.evaluate_model(max_questions=30)
    
    # Évaluation sans RAG
    print("\n2️⃣ Évaluation sans RAG...")
    direct_evaluator = ComprehensiveFactCheckerEvaluator(use_rag=False)
    direct_results, direct_test_cases, direct_llm_cases = await direct_evaluator.evaluate_model(max_questions=30)
    
    # Comparaison des résultats
    print("\n📊 Comparaison des résultats:")
    print("=" * 40)
    
    metrics = ["AnswerRelevancy", "ContextRelevancy", "Faithfulness"]
    
    print(f"{'Métrique':<20} {'RAG':<10} {'Direct':<10} {'Différence':<10}")
    print("-" * 50)
    
    for metric in metrics:
        rag_score = rag_results.get(metric, 0)
        direct_score = direct_results.get(metric, 0)
        diff = rag_score - direct_score
        
        print(f"{metric:<20} {rag_score:<10.3f} {direct_score:<10.3f} {diff:<+10.3f}")
    
    # Sauvegarder les résultats détaillés
    detailed_results = {
        "rag_results": {
            "metrics": rag_results,
            "test_cases": [
                {
                    "question": tc["question"],
                    "expected": tc["expected_answer"],
                    "actual": llm_cases[i].actual_output,
                    "category": tc["category"]
                }
                for i, tc in enumerate(rag_test_cases)
            ]
        },
        "direct_results": {
            "metrics": direct_results,
            "test_cases": [
                {
                    "question": tc["question"],
                    "expected": tc["expected_answer"],
                    "actual": llm_cases[i].actual_output,
                    "category": tc["category"]
                }
                for i, tc in enumerate(direct_test_cases)
            ]
        }
    }
    
    with open("comprehensive_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    print("\n💾 Résultats détaillés sauvegardés dans comprehensive_evaluation_results.json")
    print("\n🎉 Évaluation terminée !")

if __name__ == "__main__":
    asyncio.run(main()) 