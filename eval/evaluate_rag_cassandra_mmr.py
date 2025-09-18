#!/usr/bin/env python3
"""
Évaluation complète du RAG avec Cassandra et DeepEval
Teste toutes les métriques : Rélevance, Fidélité, Réponse, Contexte
"""

import os
import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# DeepEval imports
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric, 
    ContextualRelevancyMetric, 
    FaithfulnessMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric
)
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel

# Local imports
import sys
sys.path.append('../system')
from cassandra_manager import create_cassandra_manager
from ollama_utils import OllamaClient, format_prompt, extract_verdict
from climate_dataset import CLIMATE_DATASET, get_dataset_by_category, get_random_subset

# Load environment variables
load_dotenv()

class ComprehensiveRAGEvaluator:
    """Évaluateur complet pour le RAG avec Cassandra"""
    
    def __init__(self, embedding_model="llama2:7b"):
        """
        Initialiser l'évaluateur
        
        Args:
            embedding_model: Modèle d'embedding à utiliser
        """
        self.embedding_model = embedding_model
        
        # Initialiser les composants
        self.ollama_client = OllamaClient()
        self.cassandra_manager = create_cassandra_manager(
            table_name="fact_checker_docs"
        )
        
        # Prompts pour le fact-checking (version améliorée)
        self.fact_checking_prompt = """You are a decisive fact-checking expert on climate change.

Scientific context:
{context}

Question to verify:
{question}

CRITICAL VALIDATION: First, assess if the retrieved evidence actually addresses the specific claim made. If the evidence is NOT relevant to the specific claim, you MUST give an UNVERIFIABLE verdict.

IMPORTANT: You must be decisive and take a clear position. Do not hedge or be overly cautious. If the evidence supports the claim, say so. If it contradicts the claim, say so. If there's insufficient evidence, state that clearly.

IMPORTANT: Limit your answer to a maximum of 500 words.

Format your answer as follows:

ANALYSIS: [Your analysis based on the context]
VERDICT: [TRUE / MOSTLY TRUE / MOSTLY FALSE / FALSE / UNVERIFIABLE]
EXPLANATION: [Clear explanation of why you chose this verdict]
SOURCES: [References to the context used]
"""
    
    async def get_rag_response(self, question: str) -> Dict[str, Any]:
        """
        Obtenir une réponse RAG complète avec Cassandra
        
        Returns:
            Dict avec 'response', 'context', 'sources', 'similarity_scores'
        """
        try:
            # 1. Rechercher dans Cassandra avec MMR
            search_results = self.cassandra_manager.search_documents_mmr(
                question, 
                n_results=5, 
                lambda_param=0.7  # Plus de pertinence, moins de diversité
            )
            
            # 2. Extraire le contexte et les métadonnées
            context_parts = []
            sources = []
            similarity_scores = []
            
            for doc in search_results:
                context_parts.append(doc['content'])
                sources.append({
                    'source': doc['metadata'].get('source', 'Unknown'),
                    'similarity': doc.get('similarity', 0.0)
                })
                similarity_scores.append(doc.get('similarity', 0.0))
            
            context = "\n\n".join(context_parts)
            
            # 3. Générer la réponse avec le contexte
            prompt = self.fact_checking_prompt.format(
                context=context,
                question=question
            )
            
            response = self.ollama_client.generate(prompt, temperature=0.2)
            
            return {
                'response': response,
                'context': context,
                'sources': sources,
                'similarity_scores': similarity_scores,
                'context_length': len(context)
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération RAG: {e}")
            return {
                'response': f"Erreur: {e}",
                'context': "",
                'sources': [],
                'similarity_scores': [],
                'context_length': 0
            }
    
    def create_test_cases(self, dataset_subset: List[Dict]) -> List[LLMTestCase]:
        """Créer les cas de test pour DeepEval"""
        test_cases = []
        
        for test_case in dataset_subset:
            test_cases.append(
                LLMTestCase(
                    input=test_case["question"],
                    actual_output="",  # Sera rempli lors de l'évaluation
                    expected_output=test_case["expected_answer"],
                    context=[test_case.get("category", "")],  # Doit être une liste
                    retrieval_context=[]  # Sera rempli lors de l'évaluation
                )
            )
        
        return test_cases
    
    async def evaluate_rag_system(self, test_cases: List[Dict] = None, max_questions: int = 50) -> Dict[str, Any]:
        """
        Évaluer le système RAG complet
        
        Args:
            test_cases: Cas de test personnalisés
            max_questions: Nombre maximum de questions à évaluer
            
        Returns:
            Résultats complets de l'évaluation
        """
        if test_cases is None:
            test_cases = get_random_subset(max_questions)
        
        print(f"🧪 Évaluation du RAG avec Cassandra")
        print(f"🤖 Modèle d'embedding: {self.embedding_model}")
        print(f"📊 Base de données: Cassandra (5,233 documents)")
        print(f"📋 {len(test_cases)} cas de test")
        print("=" * 60)
        
        # Créer les cas de test DeepEval
        llm_test_cases = self.create_test_cases(test_cases)
        
        # Générer les réponses du modèle
        print("🔄 Génération des réponses RAG...")
        rag_details = []
        
        for i, test_case in enumerate(test_cases):
            print(f"  [{i+1}/{len(test_cases)}] {test_case['question'][:60]}...")
            
            # Obtenir la réponse RAG
            rag_result = await self.get_rag_response(test_case['question'])
            
            # Mettre à jour le cas de test
            llm_test_cases[i].actual_output = rag_result['response']
            llm_test_cases[i].retrieval_context = [rag_result['context']]  # Doit être une liste
            
            # Stocker les détails pour l'analyse
            rag_details.append({
                'question': test_case['question'],
                'expected': test_case['expected_answer'],
                'actual': rag_result['response'],
                'category': test_case['category'],
                'context': rag_result['context'],
                'sources': rag_result['sources'],
                'similarity_scores': rag_result['similarity_scores'],
                'context_length': rag_result['context_length']
            })
        
        # Configurer le modèle Ollama pour DeepEval
        ollama_model = OllamaModel(
            model="llama2:7b",
            base_url="http://localhost:11434",
            temperature=0.1  # Légèrement plus décisif
        )
        
        # Définir toutes les métriques d'évaluation avec Ollama
        metrics = [
            AnswerRelevancyMetric(threshold=0.7, model=ollama_model, include_reason=True),
            ContextualRelevancyMetric(threshold=0.7, model=ollama_model),
            FaithfulnessMetric(threshold=0.7, model=ollama_model),
            ContextualRecallMetric(threshold=0.7, model=ollama_model),
            ContextualPrecisionMetric(threshold=0.7, model=ollama_model)
        ]
        
        # Lancer l'évaluation
        print("\n📊 Lancement de l'évaluation DeepEval...")
        start_time = time.time()
        
        results = evaluate(
            llm_test_cases,
            metrics=metrics
        )
        
        evaluation_time = time.time() - start_time
        
        # Analyser les résultats par catégorie
        category_analysis = self.analyze_by_category(rag_details)
        
        # Calculer des métriques supplémentaires
        additional_metrics = self.calculate_additional_metrics(rag_details)
        
        # Compiler les résultats complets
        comprehensive_results = {
            'evaluation_time': evaluation_time,
            'deep_eval_metrics': results,
            'additional_metrics': additional_metrics,
            'category_analysis': category_analysis,
            'test_details': rag_details,
            'model_info': {
                'embedding_model': self.embedding_model,
                'total_questions': len(test_cases),
                'categories_tested': list(set(tc['category'] for tc in test_cases))
            }
        }
        
        return comprehensive_results
    
    def analyze_by_category(self, rag_details: List[Dict]) -> Dict[str, Dict]:
        """Analyser les résultats par catégorie"""
        categories = {}
        
        for detail in rag_details:
            cat = detail['category']
            if cat not in categories:
                categories[cat] = {
                    'count': 0,
                    'avg_similarity': 0,
                    'avg_context_length': 0,
                    'questions': []
                }
            
            categories[cat]['count'] += 1
            categories[cat]['avg_similarity'] += sum(detail['similarity_scores']) / len(detail['similarity_scores']) if detail['similarity_scores'] else 0
            categories[cat]['avg_context_length'] += detail['context_length']
            categories[cat]['questions'].append(detail['question'])
        
        # Calculer les moyennes
        for cat in categories:
            count = categories[cat]['count']
            categories[cat]['avg_similarity'] /= count
            categories[cat]['avg_context_length'] /= count
        
        return categories
    
    def calculate_additional_metrics(self, rag_details: List[Dict]) -> Dict[str, float]:
        """Calculer des métriques supplémentaires"""
        total_questions = len(rag_details)
        
        # Métriques de contexte
        avg_context_length = sum(d['context_length'] for d in rag_details) / total_questions
        avg_similarity = sum(
            sum(d['similarity_scores']) / len(d['similarity_scores']) 
            for d in rag_details if d['similarity_scores']
        ) / total_questions
        
        # Métriques de sources
        unique_sources = set()
        for detail in rag_details:
            for source in detail['sources']:
                unique_sources.add(source['source'])
        
        return {
            'avg_context_length': avg_context_length,
            'avg_similarity_score': avg_similarity,
            'unique_sources_used': len(unique_sources),
            'total_questions': total_questions
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Afficher les résultats de manière formatée"""
        print("\n" + "="*60)
        print("📈 RÉSULTATS DE L'ÉVALUATION RAG")
        print("="*60)
        
        # Métriques DeepEval
        print("\n🎯 MÉTRIQUES DEEPEVAL:")
        print("-" * 30)
        # Accéder aux métriques via l'objet EvaluationResult
        deep_eval_results = results['deep_eval_metrics']
        if hasattr(deep_eval_results, 'metric_scores'):
            for metric_name, score in deep_eval_results.metric_scores.items():
                print(f"{metric_name:<20}: {score:.3f}")
        else:
            print("Résultats DeepEval disponibles mais format non standard")
            print(f"Type: {type(deep_eval_results)}")
            print(f"Contenu: {deep_eval_results}")
        
        # Métriques supplémentaires
        print("\n📊 MÉTRIQUES SUPPLÉMENTAIRES:")
        print("-" * 30)
        additional = results['additional_metrics']
        print(f"Longueur moyenne contexte: {additional['avg_context_length']:.0f} caractères")
        print(f"Score de similarité moyen: {additional['avg_similarity_score']:.3f}")
        print(f"Sources uniques utilisées: {additional['unique_sources_used']}")
        print(f"Temps d'évaluation: {results['evaluation_time']:.1f} secondes")
        
        # Analyse par catégorie
        print("\n📋 ANALYSE PAR CATÉGORIE:")
        print("-" * 30)
        for category, stats in results['category_analysis'].items():
            print(f"{category:<20}: {stats['count']} questions, "
                  f"similarité {stats['avg_similarity']:.3f}, "
                  f"contexte {stats['avg_context_length']:.0f} chars")
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Sauvegarder les résultats dans un fichier JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_evaluation_results_{timestamp}.json"
        
        # Convertir l'objet EvaluationResult en dictionnaire
        deep_eval_results = results['deep_eval_metrics']
        if hasattr(deep_eval_results, 'metric_scores'):
            deep_eval_dict = deep_eval_results.metric_scores
        else:
            deep_eval_dict = str(deep_eval_results)  # Fallback
        
        # Nettoyer les résultats pour la sérialisation JSON
        clean_results = {
            'evaluation_time': results['evaluation_time'],
            'deep_eval_metrics': deep_eval_dict,
            'additional_metrics': results['additional_metrics'],
            'category_analysis': results['category_analysis'],
            'model_info': results['model_info']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés dans: {filename}")
        return filename

async def main():
    """Fonction principale d'évaluation"""
    
    print("🎯 ÉVALUATION COMPLÈTE DU RAG AVEC CASSANDRA")
    print("=" * 60)
    
    # Initialiser l'évaluateur
    evaluator = ComprehensiveRAGEvaluator(embedding_model="llama2:7b")
    
    # Vérifier que Cassandra contient des documents
    collection_info = evaluator.cassandra_manager.get_collection_info()
    if not collection_info.get('index_loaded', False):
        print("❌ Aucun document dans Cassandra. Veuillez d'abord indexer vos documents.")
        return
    
    print(f"✅ Cassandra contient des documents (base vectorielle prête)")
    
    # Évaluer avec différentes tailles de dataset
    test_sizes = [10]  # Commencer petit pour tester
    
    for size in test_sizes:
        print(f"\n🧪 Test avec {size} questions...")
        
        # Obtenir un sous-ensemble du dataset
        test_cases = get_random_subset(size)
        
        # Évaluer
        results = await evaluator.evaluate_rag_system(test_cases)
        
        # Afficher les résultats
        evaluator.print_results(results)
        
        # Sauvegarder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rag_eval_cassandra_{size}q_{timestamp}.json"
        evaluator.save_results(results, filename)
        
        print(f"\n✅ Évaluation avec {size} questions terminée!")
        
        # Pause entre les tests
        if size != test_sizes[-1]:
            print("⏳ Pause de 5 secondes avant le prochain test...")
            await asyncio.sleep(5)
    
    print("\n🎉 Évaluation complète terminée !")

if __name__ == "__main__":
    asyncio.run(main()) 