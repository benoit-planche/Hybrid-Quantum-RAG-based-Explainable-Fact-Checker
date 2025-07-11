#!/usr/bin/env python3
"""
Évaluation RAG avec ChromaDB et MMR (Version corrigée)
Utilise MMR sans récupérer les embeddings de ChromaDB
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

class FixedMMREvaluator:
    """Évaluateur RAG avec ChromaDB et MMR (Version corrigée)"""
    
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
        
        # Initialiser les embeddings séparément pour MMR
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
    
    def mmr_selection_with_external_embeddings(self, documents, query_embedding, k=5):
        """Sélection MMR en générant les embeddings externement"""
        import numpy as np
        
        # Générer les embeddings pour tous les documents
        print("  🔄 Génération des embeddings pour MMR...")
        document_embeddings = []
        for i, doc in enumerate(documents):
            try:
                emb = self.embeddings.embed_query(doc['content'])
                document_embeddings.append((i, emb))
            except Exception as e:
                print(f"    ⚠️ Erreur embedding document {i}: {e}")
                continue
        
        if not document_embeddings:
            print("  ❌ Aucun embedding généré")
            return []
        
        # Calculer les similarités avec la requête
        similarities = []
        for idx, emb in document_embeddings:
            sim = self.cosine_similarity_safe(query_embedding, emb)
            similarities.append((idx, sim, emb))
        
        # Trier par similarité
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Premier document : plus haute pertinence
        selected_indices = [similarities[0][0]]
        selected_embeddings = [similarities[0][2]]
        
        # Documents restants : sélection MMR
        remaining_candidates = similarities[1:]
        
        for _ in range(min(k - 1, len(remaining_candidates))):
            best_mmr_score = -1
            best_idx = -1
            best_emb = None
            
            for idx, sim, emb in remaining_candidates:
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
            
            if best_idx != -1:
                selected_indices.append(best_idx)
                selected_embeddings.append(best_emb)
                # Retirer le candidat sélectionné
                remaining_candidates = [(idx, sim, emb) for idx, sim, emb in remaining_candidates if idx != best_idx]
            else:
                break
        
        return selected_indices
    
    def get_rag_response(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Obtenir une réponse RAG complète avec MMR
        
        Returns:
            Dict avec 'response', 'context', 'sources', 'similarity_scores'
        """
        try:
            # 1. Obtenir tous les documents de la collection (sans embeddings)
            results = self.chroma_manager.collection.get(
                include=['documents', 'metadatas']
            )
            
            if not results['documents'] or len(results['documents']) == 0:
                print("❌ Aucun document trouvé dans la collection")
                return self._error_response("Aucun document disponible")
            
            all_documents = results['documents']
            all_metadatas = results['metadatas']
            
            # 2. Préparer les documents pour MMR
            documents_for_mmr = []
            for i, (content, metadata) in enumerate(zip(all_documents, all_metadatas)):
                documents_for_mmr.append({
                    'content': content,
                    'metadata': metadata,
                    'index': i
                })
            
            # 3. Générer l'embedding de la requête
            query_embedding = self.embeddings.embed_query(question)
            
            # 4. Appliquer MMR pour sélectionner les documents
            mmr_indices = self.mmr_selection_with_external_embeddings(
                documents_for_mmr, query_embedding, k=n_results
            )
            
            if not mmr_indices:
                print("❌ Aucun document sélectionné par MMR")
                return self._error_response("Aucun document sélectionné par MMR")
            
            # 5. Extraire les documents sélectionnés par MMR
            context_parts = []
            sources = []
            similarity_scores = []
            
            for idx in mmr_indices:
                content = all_documents[idx]
                metadata = all_metadatas[idx]
                
                # Calculer la similarité avec la requête
                doc_embedding = self.embeddings.embed_query(content)
                similarity = self.cosine_similarity_safe(query_embedding, doc_embedding)
                
                context_parts.append(content)
                sources.append({
                    'source': metadata.get('source', 'Unknown'),
                    'similarity': similarity,
                    'mmr_index': idx
                })
                similarity_scores.append(similarity)
            
            context = "\n\n".join(context_parts)
            
            # 6. Générer la réponse avec le contexte
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
                'mmr_indices': mmr_indices,
                'lambda_param': self.lambda_param
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
            'mmr_indices': [],
            'lambda_param': self.lambda_param
        }
    
    async def evaluate_rag_system(self, max_questions: int = 10) -> Dict[str, Any]:
        """
        Évaluer le système RAG complet avec MMR
        
        Args:
            max_questions: Nombre maximum de questions à évaluer
            
        Returns:
            Résultats complets de l'évaluation
        """
        test_cases = get_random_subset(max_questions)
        
        print(f"🧪 Évaluation du RAG avec ChromaDB et MMR (Version corrigée)")
        print(f"🤖 Modèle d'embedding: {self.embedding_model}")
        print(f"📊 Paramètre MMR (λ): {self.lambda_param}")
        print(f"📋 {len(test_cases)} cas de test")
        print("=" * 60)
        
        # Générer les réponses du modèle
        print("🔄 Génération des réponses RAG avec MMR...")
        rag_details = []
        
        for i, test_case in enumerate(test_cases):
            print(f"  [{i+1}/{len(test_cases)}] {test_case['question'][:60]}...")
            
            # Obtenir la réponse RAG avec MMR
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
                'mmr_indices': rag_result['mmr_indices'],
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
                    'avg_context_length': 0
                }
            
            categories[category]['count'] += 1
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
        
        for detail in rag_details:
            if detail['similarity_scores']:
                similarities.extend(detail['similarity_scores'])
            context_lengths.append(detail['context_length'])
        
        avg_similarity = np.mean(similarities) if similarities else 0.0
        avg_context_length = np.mean(context_lengths) if context_lengths else 0.0
        
        return {
            'avg_similarity_score': avg_similarity,
            'avg_context_length': avg_context_length,
            'total_questions': len(rag_details)
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Afficher les résultats de l'évaluation"""
        print("\n" + "="*60)
        print("📊 RÉSULTATS DE L'ÉVALUATION MMR AVEC CHROMADB (CORRIGÉE)")
        print("="*60)
        
        # Informations générales
        print(f"📅 Date: {results['evaluation_date']}")
        print(f"🤖 Modèle: {results['model']}")
        print(f"📊 Paramètre MMR (λ): {results['lambda_param']}")
        print(f"📋 Nombre de tests: {results['test_cases_count']}")
        
        # Métriques supplémentaires
        print("\n📈 MÉTRIQUES MMR:")
        additional_metrics = results['additional_metrics']
        print(f"  Similarité moyenne: {additional_metrics['avg_similarity_score']:.3f}")
        print(f"  Longueur contexte moyenne: {additional_metrics['avg_context_length']:.0f} caractères")
        
        # Analyse par catégorie
        print("\n📂 ANALYSE PAR CATÉGORIE:")
        category_analysis = results['category_analysis']
        for category, metrics in category_analysis.items():
            print(f"  {category}:")
            print(f"    Nombre de tests: {metrics['count']}")
            print(f"    Similarité moyenne: {metrics['avg_similarity']:.3f}")
            print(f"    Longueur contexte moyenne: {metrics['avg_context_length']:.0f} caractères")
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Sauvegarder les résultats dans un fichier JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_eval_mmr_fixed_lambda{self.lambda_param}_{timestamp}.json"
        
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
    """Fonction principale pour l'évaluation MMR avec ChromaDB (Version corrigée)"""
    print("🚀 Démarrage de l'évaluation RAG avec ChromaDB et MMR (Version corrigée)")
    
    # Paramètres d'évaluation
    embedding_model = "llama2:7b"
    lambda_param = 0.5  # Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)
    max_questions = 10  # Nombre de questions à tester
    
    # Créer l'évaluateur
    evaluator = FixedMMREvaluator(
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
    asyncio.run(main()) 