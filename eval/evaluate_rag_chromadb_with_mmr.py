#!/usr/bin/env python3
"""
Évaluation complète du RAG avec ChromaDB et MMR
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
from chromadb_manager import ChromaDBManager
from ollama_utils import OllamaClient, format_prompt, extract_verdict
from climate_dataset import CLIMATE_DATASET, get_dataset_by_category, get_random_subset
from mmr_utils import mmr_similarity_search, simple_similarity_search, calculate_diversity_metrics

# Load environment variables
load_dotenv()

class ChromaDBMMREvaluator:
    """Évaluateur complet pour le RAG avec ChromaDB et MMR"""
    
    def __init__(self, embedding_model="llama2:7b", lambda_param=0.5):
        """
        Initialiser l'évaluateur
        
        Args:
            embedding_model: Modèle d'embedding à utiliser
            lambda_param: Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)
        """
        self.embedding_model = embedding_model
        self.lambda_param = lambda_param
        
        # Initialiser les composants
        self.ollama_client = OllamaClient()
        self.chroma_manager = ChromaDBManager(
            persist_directory="../system/chroma_db",
            embedding_model=embedding_model
        )
        
        # Prompts pour le fact-checking
        self.fact_checking_prompt = """Tu es un expert en fact-checking sur le changement climatique.

Contexte scientifique:
{context}

Question à vérifier: {question}

Analyse cette question en te basant UNIQUEMENT sur le contexte fourni.
Si le contexte ne contient pas d'information pertinente, indique-le clairement.

IMPORTANT: Limite ta réponse à 500 mots maximum.

Format ta réponse comme suit:
ANALYSE: [Ton analyse basée sur le contexte]
VERDICT: [VRAI/FAUX/MIXTE/INCONNU]
EXPLICATION: [Explication de ton verdict]
SOURCES: [Références au contexte utilisé]
"""
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculer la similarité cosinus entre deux vecteurs"""
        import numpy as np
        # Convert to numpy arrays if they aren't already
        if not isinstance(a, np.ndarray):
            a = np.array(a)
        if not isinstance(b, np.ndarray):
            b = np.array(b)
        
        # Handle zero vectors
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    async def get_rag_response_with_mmr(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Obtenir une réponse RAG complète avec MMR sur ChromaDB
        
        Returns:
            Dict avec 'response', 'context', 'sources', 'similarity_scores', 'mmr_scores'
        """
        try:
            # 1. Obtenir tous les embeddings de la collection
            results = self.chroma_manager.collection.get(
                include=['embeddings', 'documents', 'metadatas']
            )
            
            if not results['embeddings'] or len(results['embeddings']) == 0:
                print("❌ Aucun embedding trouvé dans la collection")
                return self._error_response("Aucun embedding disponible")
            
            # Convertir les embeddings en listes si ce sont des numpy arrays
            import numpy as np
            all_embeddings = []
            for emb in results['embeddings']:
                if isinstance(emb, np.ndarray):
                    all_embeddings.append(emb.tolist())
                else:
                    all_embeddings.append(emb)
            
            all_documents = results['documents']
            all_metadatas = results['metadatas']
            
            # 2. Générer l'embedding de la requête
            query_embedding = self.chroma_manager.embeddings.embed_query(question)
            
            # 3. Appliquer MMR pour sélectionner les documents
            mmr_indices = mmr_similarity_search(
                all_embeddings, 
                query_embedding, 
                k=n_results, 
                lambda_param=self.lambda_param
            )
            
            # 4. Comparer avec la recherche simple pour l'analyse
            simple_indices = simple_similarity_search(
                all_embeddings, 
                query_embedding, 
                k=n_results
            )
            
            # 5. Extraire les documents sélectionnés par MMR
            context_parts = []
            sources = []
            similarity_scores = []
            mmr_scores = []
            
            for idx in mmr_indices:
                content = all_documents[idx]
                metadata = all_metadatas[idx]
                
                # Calculer la similarité avec la requête
                doc_embedding = all_embeddings[idx]
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                context_parts.append(content)
                sources.append({
                    'source': metadata.get('source', 'Unknown'),
                    'similarity': similarity,
                    'mmr_index': idx
                })
                similarity_scores.append(similarity)
                
                # Calculer le score MMR pour ce document
                selected_embeddings = [all_embeddings[i] for i in mmr_indices[:mmr_indices.index(idx)]]
                mmr_score = self._calculate_mmr_score(query_embedding, doc_embedding, selected_embeddings)
                mmr_scores.append(mmr_score)
            
            context = "\n\n".join(context_parts)
            
            # 6. Calculer les métriques de diversité
            selected_embeddings = [all_embeddings[i] for i in mmr_indices]
            diversity_metrics = calculate_diversity_metrics(selected_embeddings)
            
            # 7. Générer la réponse avec le contexte
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
                'mmr_scores': mmr_scores,
                'context_length': len(context),
                'mmr_indices': mmr_indices,
                'simple_indices': simple_indices,
                'diversity_metrics': diversity_metrics,
                'lambda_param': self.lambda_param
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération RAG avec MMR: {e}")
            return self._error_response(str(e))
    
    def _calculate_mmr_score(self, query_embedding: List[float], doc_embedding: List[float], 
                           selected_embeddings: List[List[float]]) -> float:
        """Calculer le score MMR pour un document"""
        # Relevance score (similarity to query)
        relevance = self._cosine_similarity(query_embedding, doc_embedding)
        
        # Diversity score (minimum similarity to already selected documents)
        if not selected_embeddings:
            diversity = 1.0  # First document has maximum diversity
        else:
            similarities = [self._cosine_similarity(doc_embedding, selected_emb) for selected_emb in selected_embeddings]
            diversity = 1.0 - max(similarities)  # 1 - max similarity = diversity
        
        # MMR score = λ * relevance + (1-λ) * diversity
        mmr_score = self.lambda_param * relevance + (1 - self.lambda_param) * diversity
        
        return mmr_score
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Créer une réponse d'erreur standardisée"""
        return {
            'response': f"Erreur: {error_msg}",
            'context': "",
            'sources': [],
            'similarity_scores': [],
            'mmr_scores': [],
            'context_length': 0,
            'mmr_indices': [],
            'simple_indices': [],
            'diversity_metrics': {},
            'lambda_param': self.lambda_param
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
    
    async def evaluate_rag_system(self, test_cases: List[Dict] = None, max_questions: int = 10) -> Dict[str, Any]:
        """
        Évaluer le système RAG complet avec MMR
        
        Args:
            test_cases: Cas de test personnalisés
            max_questions: Nombre maximum de questions à évaluer
            
        Returns:
            Résultats complets de l'évaluation
        """
        if test_cases is None:
            test_cases = get_random_subset(max_questions)
        
        print(f"🧪 Évaluation du RAG avec ChromaDB et MMR")
        print(f"🤖 Modèle d'embedding: {self.embedding_model}")
        print(f"📊 Paramètre MMR (λ): {self.lambda_param}")
        print(f"📋 {len(test_cases)} cas de test")
        print("=" * 60)
        
        # Créer les cas de test DeepEval
        llm_test_cases = self.create_test_cases(test_cases)
        
        # Générer les réponses du modèle
        print("🔄 Génération des réponses RAG avec MMR...")
        rag_details = []
        
        for i, test_case in enumerate(test_cases):
            print(f"  [{i+1}/{len(test_cases)}] {test_case['question'][:60]}...")
            
            # Obtenir la réponse RAG avec MMR
            rag_result = await self.get_rag_response_with_mmr(test_case['question'])
            
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
                'mmr_scores': rag_result['mmr_scores'],
                'context_length': rag_result['context_length'],
                'mmr_indices': rag_result['mmr_indices'],
                'simple_indices': rag_result['simple_indices'],
                'diversity_metrics': rag_result['diversity_metrics'],
                'lambda_param': rag_result['lambda_param']
            })
        
        # Configurer le modèle Ollama pour DeepEval
        ollama_model = OllamaModel(
            model="llama2:7b",
            base_url="http://localhost:11434",
            temperature=0
        )
        
        # Définir toutes les métriques d'évaluation avec Ollama
        metrics = [
            AnswerRelevancyMetric(model=ollama_model),
            ContextualRelevancyMetric(model=ollama_model),
            FaithfulnessMetric(model=ollama_model),
            ContextualRecallMetric(model=ollama_model),
            ContextualPrecisionMetric(model=ollama_model)
        ]
        
        # Évaluer avec DeepEval
        print("📊 Évaluation avec DeepEval...")
        results = await evaluate(
            test_cases=llm_test_cases,
            metrics=metrics
        )
        
        # Analyser les résultats par catégorie
        category_analysis = self.analyze_by_category(rag_details)
        
        # Calculer des métriques supplémentaires
        additional_metrics = self.calculate_additional_metrics(rag_details)
        
        # Compiler tous les résultats
        final_results = {
            'evaluation_date': datetime.now().isoformat(),
            'model': self.embedding_model,
            'lambda_param': self.lambda_param,
            'deepeval_results': results,
            'category_analysis': category_analysis,
            'additional_metrics': additional_metrics,
            'rag_details': rag_details,
            'test_cases_count': len(test_cases)
        }
        
        return final_results
    
    def analyze_by_category(self, rag_details: List[Dict]) -> Dict[str, Dict]:
        """Analyser les résultats par catégorie"""
        categories = {}
        
        for detail in rag_details:
            category = detail['category']
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'avg_similarity': 0,
                    'avg_mmr_score': 0,
                    'avg_diversity_score': 0,
                    'avg_context_length': 0
                }
            
            categories[category]['count'] += 1
            categories[category]['avg_similarity'] += np.mean(detail['similarity_scores'])
            categories[category]['avg_mmr_score'] += np.mean(detail['mmr_scores'])
            categories[category]['avg_diversity_score'] += detail['diversity_metrics'].get('diversity_score', 0)
            categories[category]['avg_context_length'] += detail['context_length']
        
        # Calculer les moyennes
        for category in categories:
            count = categories[category]['count']
            categories[category]['avg_similarity'] /= count
            categories[category]['avg_mmr_score'] /= count
            categories[category]['avg_diversity_score'] /= count
            categories[category]['avg_context_length'] /= count
        
        return categories
    
    def calculate_additional_metrics(self, rag_details: List[Dict]) -> Dict[str, float]:
        """Calculer des métriques supplémentaires"""
        import numpy as np
        
        # Métriques globales
        avg_similarity = np.mean([np.mean(detail['similarity_scores']) for detail in rag_details])
        avg_mmr_score = np.mean([np.mean(detail['mmr_scores']) for detail in rag_details])
        avg_diversity = np.mean([detail['diversity_metrics'].get('diversity_score', 0) for detail in rag_details])
        avg_context_length = np.mean([detail['context_length'] for detail in rag_details])
        
        # Calculer l'overlap entre MMR et recherche simple
        mmr_simple_overlap = 0
        for detail in rag_details:
            mmr_set = set(detail['mmr_indices'])
            simple_set = set(detail['simple_indices'])
            overlap = len(mmr_set.intersection(simple_set))
            mmr_simple_overlap += overlap / len(mmr_set) if mmr_set else 0
        
        avg_overlap = mmr_simple_overlap / len(rag_details)
        
        return {
            'avg_similarity_score': avg_similarity,
            'avg_mmr_score': avg_mmr_score,
            'avg_diversity_score': avg_diversity,
            'avg_context_length': avg_context_length,
            'mmr_simple_overlap_ratio': avg_overlap
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Afficher les résultats de l'évaluation"""
        print("\n" + "="*60)
        print("📊 RÉSULTATS DE L'ÉVALUATION MMR AVEC CHROMADB")
        print("="*60)
        
        # Informations générales
        print(f"📅 Date: {results['evaluation_date']}")
        print(f"🤖 Modèle: {results['model']}")
        print(f"📊 Paramètre MMR (λ): {results['lambda_param']}")
        print(f"📋 Nombre de tests: {results['test_cases_count']}")
        
        # Résultats DeepEval
        print("\n🔍 RÉSULTATS DEEPEVAL:")
        deepeval_results = results['deepeval_results']
        for metric_name, score in deepeval_results.items():
            print(f"  {metric_name}: {score:.3f}")
        
        # Métriques supplémentaires
        print("\n📈 MÉTRIQUES MMR:")
        additional_metrics = results['additional_metrics']
        print(f"  Similarité moyenne: {additional_metrics['avg_similarity_score']:.3f}")
        print(f"  Score MMR moyen: {additional_metrics['avg_mmr_score']:.3f}")
        print(f"  Diversité moyenne: {additional_metrics['avg_diversity_score']:.3f}")
        print(f"  Longueur contexte moyenne: {additional_metrics['avg_context_length']:.0f} caractères")
        print(f"  Overlap MMR/Simple: {additional_metrics['mmr_simple_overlap_ratio']:.3f}")
        
        # Analyse par catégorie
        print("\n📂 ANALYSE PAR CATÉGORIE:")
        category_analysis = results['category_analysis']
        for category, metrics in category_analysis.items():
            print(f"  {category}:")
            print(f"    Nombre de tests: {metrics['count']}")
            print(f"    Similarité moyenne: {metrics['avg_similarity']:.3f}")
            print(f"    Score MMR moyen: {metrics['avg_mmr_score']:.3f}")
            print(f"    Diversité moyenne: {metrics['avg_diversity_score']:.3f}")
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Sauvegarder les résultats dans un fichier JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_eval_chromadb_mmr_lambda{self.lambda_param}_{timestamp}.json"
        
        filepath = os.path.join("eval", filename)
        
        # Convertir les numpy arrays en listes pour la sérialisation JSON
        def convert_numpy(obj):
            import numpy as np
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            return obj
        
        # Convertir récursivement
        def convert_recursive(obj):
            if isinstance(obj, dict):
                return {k: convert_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_recursive(v) for v in obj]
            else:
                return convert_numpy(obj)
        
        results_converted = convert_recursive(results)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_converted, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés dans: {filepath}")
        return filepath

async def main():
    """Fonction principale pour l'évaluation MMR avec ChromaDB"""
    print("🚀 Démarrage de l'évaluation RAG avec MMR et ChromaDB")
    
    # Paramètres d'évaluation
    embedding_model = "llama2:7b"
    lambda_param = 0.5  # Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)
    max_questions = 10  # Nombre de questions à tester
    
    # Créer l'évaluateur
    evaluator = ChromaDBMMREvaluator(
        embedding_model=embedding_model,
        lambda_param=lambda_param
    )
    
    # Évaluer le système
    results = await evaluator.evaluate_rag_system(max_questions=max_questions)
    
    # Afficher les résultats
    evaluator.print_results(results)
    
    # Sauvegarder les résultats
    evaluator.save_results(results)
    
    print("\n✅ Évaluation MMR avec ChromaDB terminée!")

if __name__ == "__main__":
    import numpy as np
    asyncio.run(main()) 