#!/usr/bin/env python3
"""
Évaluation RAG avec ChromaDB et MMR simulé
Utilise la recherche simple de ChromaDB + simulation MMR
"""

import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Local imports
import sys
sys.path.append('../system')
from chromadb_manager import ChromaDBManager
from ollama_utils import OllamaClient, OllamaEmbeddings
from climate_dataset import get_random_subset

# Load environment variables
load_dotenv()

class SimulatedMMREvaluator:
    """Évaluateur RAG avec ChromaDB et MMR simulé"""
    
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
        
        # Initialiser les embeddings pour la simulation MMR
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        
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
    
    def cosine_similarity_safe(self, a, b):
        """Calculer la similarité cosinus de manière sûre"""
        import numpy as np
        
        # Convertir en listes si nécessaire
        if hasattr(a, 'tolist'):
            a = a.tolist()
        if hasattr(b, 'tolist'):
            b = b.tolist()
        
        # Convertir en numpy arrays
        a = np.array(a, dtype=np.float64)
        b = np.array(b, dtype=np.float64)
        
        # Handle zero vectors
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def simulate_mmr_selection(self, search_results, query_embedding, k=5):
        """Simuler MMR en post-traitant les résultats de recherche ChromaDB"""
        import numpy as np
        
        if not search_results:
            return []
        
        # Générer les embeddings pour les documents trouvés
        print("  🔄 Simulation MMR sur les résultats ChromaDB...")
        document_embeddings = []
        
        for i, doc in enumerate(search_results):
            try:
                # Générer l'embedding du document
                doc_embedding = self.embeddings.embed_query(doc['content'])
                document_embeddings.append((i, doc, doc_embedding))
            except Exception as e:
                print(f"    ⚠️ Erreur embedding document {i}: {e}")
                continue
        
        if not document_embeddings:
            print("  ❌ Aucun embedding généré pour MMR")
            return search_results[:k]  # Retourner les premiers résultats
        
        # Calculer les similarités avec la requête
        similarities = []
        for idx, doc, emb in document_embeddings:
            sim = self.cosine_similarity_safe(query_embedding, emb)
            similarities.append((idx, sim, emb, doc))
        
        # Trier par similarité
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Premier document : plus haute pertinence
        selected_indices = [similarities[0][0]]
        selected_embeddings = [similarities[0][2]]
        selected_docs = [similarities[0][3]]
        
        # Documents restants : sélection MMR
        remaining_candidates = similarities[1:]
        
        for _ in range(min(k - 1, len(remaining_candidates))):
            best_mmr_score = -1
            best_idx = -1
            best_emb = None
            best_doc = None
            
            for idx, sim, emb, doc in remaining_candidates:
                # Score de pertinence
                relevance = sim
                
                # Score de diversité
                if not selected_embeddings:
                    diversity = 1.0
                else:
                    similarities_to_selected = []
                    for selected_emb in selected_embeddings:
                        sim_to_selected = self.cosine_similarity_safe(emb, selected_emb)
                        similarities_to_selected.append(sim_to_selected)
                    diversity = 1.0 - max(similarities_to_selected)
                
                # Score MMR
                mmr_score = self.lambda_param * relevance + (1 - self.lambda_param) * diversity
                
                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_idx = idx
                    best_emb = emb
                    best_doc = doc
            
            if best_idx != -1:
                selected_indices.append(best_idx)
                selected_embeddings.append(best_emb)
                selected_docs.append(best_doc)
                # Retirer le candidat sélectionné
                remaining_candidates = [(idx, sim, emb, doc) for idx, sim, emb, doc in remaining_candidates if idx != best_idx]
            else:
                break
        
        return selected_docs
    
    def get_rag_response(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Obtenir une réponse RAG complète avec MMR simulé
        
        Returns:
            Dict avec 'response', 'context', 'sources', 'similarity_scores'
        """
        try:
            # 1. Utiliser la recherche simple de ChromaDB (qui fonctionne)
            # Récupérer plus de résultats pour une meilleure évaluation MMR
            search_results = self.chroma_manager.search_documents(question, n_results=n_results*4)  # 4x plus de documents
            
            if not search_results:
                print("❌ Aucun document trouvé")
                return self._error_response("Aucun document trouvé")
            
            # 2. Générer l'embedding de la requête pour MMR
            query_embedding = self.embeddings.embed_query(question)
            
            # 3. Appliquer MMR simulé sur les résultats
            mmr_selected_docs = self.simulate_mmr_selection(search_results, query_embedding, k=n_results)
            
            if not mmr_selected_docs:
                # Fallback: utiliser les résultats originaux
                mmr_selected_docs = search_results[:n_results]
            
            # 4. Extraire les informations
            context_parts = []
            sources = []
            similarity_scores = []
            
            for doc in mmr_selected_docs:
                context_parts.append(doc['content'])
                sources.append({
                    'source': doc['metadata'].get('source', 'Unknown'),
                    'similarity': doc['similarity'],
                    'distance': doc['distance'],
                    'mmr_selected': True
                })
                similarity_scores.append(doc['similarity'])
            
            context = "\n\n".join(context_parts)
            
            # 5. Générer la réponse avec le contexte
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
                'context_length': len(context),
                'mmr_simulated': True,
                'lambda_param': self.lambda_param,
                'initial_pool_size': len(search_results),  # Ajouter cette info
                'final_selection_size': len(mmr_selected_docs)
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération RAG: {e}")
            return self._error_response(str(e))
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Créer une réponse d'erreur standardisée"""
        return {
            'response': f"Erreur: {error_msg}",
            'context': "",
            'sources': [],
            'similarity_scores': [],
            'context_length': 0,
            'mmr_simulated': False,
            'lambda_param': self.lambda_param
        }
    
    async def evaluate_rag_system(self, max_questions: int = 10) -> Dict[str, Any]:
        """
        Évaluer le système RAG complet avec MMR simulé
        
        Args:
            max_questions: Nombre maximum de questions à évaluer
            
        Returns:
            Résultats complets de l'évaluation
        """
        test_cases = get_random_subset(max_questions)
        
        print(f"🧪 Évaluation du RAG avec ChromaDB et MMR simulé")
        print(f"🤖 Modèle d'embedding: {self.embedding_model}")
        print(f"📊 Paramètre MMR (λ): {self.lambda_param}")
        print(f"📋 {len(test_cases)} cas de test")
        print("=" * 60)
        
        # Générer les réponses du modèle
        print("🔄 Génération des réponses RAG avec MMR simulé...")
        rag_details = []
        
        for i, test_case in enumerate(test_cases):
            print(f"  [{i+1}/{len(test_cases)}] {test_case['question'][:60]}...")
            
            # Obtenir la réponse RAG avec MMR simulé
            rag_result = self.get_rag_response(test_case['question'])
            
            # Stocker les détails pour l'analyse
            rag_details.append({
                'question': test_case['question'],
                'expected': test_case['expected_answer'],
                'actual': rag_result['response'],
                'category': test_case['category'],
                'context': rag_result['context'],
                'sources': rag_result['sources'],
                'similarity_scores': rag_result['similarity_scores'],
                'context_length': rag_result['context_length'],
                'mmr_simulated': rag_result['mmr_simulated'],
                'lambda_param': rag_result['lambda_param']
            })
        
        # Analyser les résultats par catégorie
        category_analysis = self.analyze_by_category(rag_details)
        
        # Calculer des métriques supplémentaires
        additional_metrics = self.calculate_additional_metrics(rag_details)
        
        # Compiler tous les résultats
        final_results = {
            'evaluation_date': datetime.now().isoformat(),
            'model': self.embedding_model,
            'lambda_param': self.lambda_param,
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
                    'avg_context_length': 0,
                    'mmr_simulated_count': 0
                }
            
            categories[category]['count'] += 1
            if detail['mmr_simulated']:
                categories[category]['mmr_simulated_count'] += 1
            if detail['similarity_scores']:
                categories[category]['avg_similarity'] += sum(detail['similarity_scores']) / len(detail['similarity_scores'])
            categories[category]['avg_context_length'] += detail['context_length']
        
        # Calculer les moyennes
        for category in categories:
            count = categories[category]['count']
            categories[category]['avg_similarity'] /= count
            categories[category]['avg_context_length'] /= count
        
        return categories
    
    def calculate_additional_metrics(self, rag_details: List[Dict]) -> Dict[str, float]:
        """Calculer des métriques supplémentaires"""
        import numpy as np
        
        # Métriques globales
        similarities = []
        context_lengths = []
        mmr_simulated_count = 0
        
        for detail in rag_details:
            if detail['mmr_simulated']:
                mmr_simulated_count += 1
            if detail['similarity_scores']:
                similarities.extend(detail['similarity_scores'])
            context_lengths.append(detail['context_length'])
        
        avg_similarity = np.mean(similarities) if similarities else 0.0
        avg_context_length = np.mean(context_lengths) if context_lengths else 0.0
        mmr_simulation_rate = mmr_simulated_count / len(rag_details) if rag_details else 0.0
        
        return {
            'avg_similarity_score': avg_similarity,
            'avg_context_length': avg_context_length,
            'mmr_simulation_rate': mmr_simulation_rate,
            'total_questions': len(rag_details)
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Afficher les résultats de l'évaluation"""
        print("\n" + "="*60)
        print("📊 RÉSULTATS DE L'ÉVALUATION MMR SIMULÉ AVEC CHROMADB")
        print("="*60)
        
        # Informations générales
        print(f"📅 Date: {results['evaluation_date']}")
        print(f"🤖 Modèle: {results['model']}")
        print(f"📊 Paramètre MMR (λ): {results['lambda_param']}")
        print(f"📋 Nombre de tests: {results['test_cases_count']}")
        
        # Métriques supplémentaires
        print("\n📈 MÉTRIQUES MMR SIMULÉ:")
        additional_metrics = results['additional_metrics']
        print(f"  Similarité moyenne: {additional_metrics['avg_similarity_score']:.3f}")
        print(f"  Longueur contexte moyenne: {additional_metrics['avg_context_length']:.0f} caractères")
        print(f"  Taux de simulation MMR: {additional_metrics['mmr_simulation_rate']:.1%}")
        
        # Analyse par catégorie
        print("\n📂 ANALYSE PAR CATÉGORIE:")
        category_analysis = results['category_analysis']
        for category, metrics in category_analysis.items():
            print(f"  {category}:")
            print(f"    Nombre de tests: {metrics['count']}")
            print(f"    MMR simulé: {metrics['mmr_simulated_count']}/{metrics['count']}")
            print(f"    Similarité moyenne: {metrics['avg_similarity']:.3f}")
            print(f"    Longueur contexte moyenne: {metrics['avg_context_length']:.0f} caractères")
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Sauvegarder les résultats dans un fichier JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_eval_mmr_simulated_lambda{self.lambda_param}_{timestamp}.json"
        
        filepath = filename  # Sauvegarder dans le répertoire courant
        
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
    """Fonction principale pour l'évaluation MMR simulé avec ChromaDB"""
    print("🚀 Démarrage de l'évaluation RAG avec ChromaDB et MMR simulé")
    
    # Paramètres d'évaluation
    embedding_model = "llama2:7b"
    lambda_param = 0.5  # Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)
    max_questions = 10  # Nombre de questions à tester
    
    # Créer l'évaluateur
    evaluator = SimulatedMMREvaluator(
        embedding_model=embedding_model,
        lambda_param=lambda_param
    )
    
    # Évaluer le système
    results = await evaluator.evaluate_rag_system(max_questions=max_questions)
    
    # Afficher les résultats
    evaluator.print_results(results)
    
    # Sauvegarder les résultats
    evaluator.save_results(results)
    
    print("\n✅ Évaluation MMR simulé avec ChromaDB terminée!")

if __name__ == "__main__":
    asyncio.run(main()) 