#!/usr/bin/env python3
"""
Evaluation script for app.py precision testing
Tests the fact-checking accuracy of the Streamlit application
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
import re

# Add the system directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'system'))

from ollama_utils import OllamaClient, format_prompt, extract_verdict
from cassandra_manager import create_cassandra_manager

class AppPrecisionEvaluator:
    def __init__(self):
        """Initialize the evaluator with the same components as app.py"""
        self.ollama_client = OllamaClient()
        
        # Initialize Cassandra Vector Store with MMR
        try:
            self.cassandra_manager = create_cassandra_manager(
                table_name="fact_checker_docs"
            )
            print("✅ Cassandra Vector Store avec MMR initialisé avec succès")
        except Exception as e:
            print(f"❌ Erreur d'initialisation Cassandra Vector Store: {e}")
            self.cassandra_manager = None
        
        # Define the same prompts as in app.py
        self.retrieval_prompt_template = """I need to fact check the following claim:

Claim: {claim}

Generate 3-5 specific and targeted search queries to find reliable scientific evidence that can definitively verify or refute this claim. 

CRITICAL: Focus on the EXACT TIME PERIODS and SPECIFIC FACTS mentioned in the claim:
- If the claim mentions a specific year (like 1998), include that year in queries
- If the claim mentions a specific phenomenon, search for that exact phenomenon
- Create queries that directly test the specific claim made
- Include both supporting and contradicting evidence searches

For example, if the claim is "Did global warming stop in 1998?", create queries like:
- "global warming temperature trend 1998"
- "global temperature data after 1998"
- "climate change hiatus 1998"
- "temperature records 1998 present"

If the claim is about "solar cycles and warming", create queries like:
- "solar cycles global temperature correlation"
- "solar activity climate change evidence"
- "sunspot cycles warming trend"

Make the queries precise and directly test the specific claim made.
"""

        self.analysis_prompt_template = """You are a decisive fact-checker. Your job is to verify the following claim using IN PRIORITY the provided evidence. You must take a clear position based on the available evidence.

Claim: {claim}

Evidence:
{retrieved_docs}

IMPORTANT: You must be decisive and take a clear position. Do not hedge or be overly cautious. If the evidence supports the claim, say so. If it contradicts the claim, say so. If there's insufficient evidence, state that clearly.

CRITICAL VALIDATION: First, assess if the retrieved evidence actually addresses the specific claim made. Ask yourself:
- Does the evidence contain data about the specific time period mentioned in the claim?
- Does the evidence address the exact phenomenon described in the claim?
- If the claim mentions "1998", does the evidence contain data from 1998 or after?
- If the claim asks about "global warming stopping", does the evidence contain temperature data?

If the evidence is NOT relevant to the specific claim, you MUST give a FALSE verdict and explain why the evidence is insufficient.

Please analyze the claim step by step:
1. Break down the claim into its key components
2. For each component, identify supporting or contradicting evidence from the provided sources
3. Note any missing information that would be needed for a complete verification
4. Assign a verdict to the claim from the following options:
   - TRUE: The claim is supported by the evidence
   - FALSE: The claim is contradicted by the evidence or insufficient evidence

IMPORTANT: Choose the verdict that best reflects the overall truth of the claim based on the available evidence. Be decisive. If it's unclear or insufficient evidence, say FALSE.

Format your response as follows:
CLAIM COMPONENTS:
- [List key components]

EVIDENCE ANALYSIS:
- Component 1: [Analysis with direct quotes from sources]
- Component 2: [Analysis with direct quotes from sources]
...

MISSING INFORMATION:
- [List any info gaps]

VERDICT: [Your decisive verdict - TRUE or FALSE only]

EXPLANATION:
[Clear explanation of why you chose this verdict]
"""

        self.summary_prompt_template = """Based on the following fact-check analysis:

{analysis}

Generate a clear and decisive summary that:
1. States what was claimed
2. Explains what the evidence definitively shows
3. Gives a clear verdict with strong reasoning

Be direct and confident in your assessment. If the evidence supports the claim, say so clearly. If it contradicts the claim, state this definitively. If there's insufficient evidence, explain why the claim cannot be verified.

Keep your summary under 200 words and make it accessible to general audiences.
"""

    def generate_search_queries(self, claim: str) -> str:
        """Generate search queries for a given claim."""
        prompt = format_prompt(self.retrieval_prompt_template, claim=claim)
        result = self.ollama_client.generate(prompt, temperature=0.5)
        return result

    def retrieve_documents(self, claim: str, k: int = 5, lambda_param: float = 1.0) -> List[str]:
        """Retrieve relevant documents from Cassandra Vector Store using MMR."""
        if not self.cassandra_manager:
            print("❌ Cassandra Vector Store n'est pas initialisé")
            return []
        
        # Vérifier si l'index contient des documents
        collection_info = self.cassandra_manager.get_collection_info()
        if not collection_info.get('index_loaded', False):
            print("❌ Aucun document dans la base vectorielle.")
            return []
        
        # Générer les requêtes de recherche
        queries_text = self.generate_search_queries(claim)
        queries = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-)\s*(.+?)(?=\n|$)', queries_text)
        if not queries:
            queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
        if not queries:
            queries = [claim]
        
        # Utiliser la première requête pour la recherche
        query_for_embedding = queries[0]
        
        print(f"🔍 Requêtes de recherche générées: {', '.join(queries[:3])}")
        
        # Utiliser Cassandra MMR search
        retrieved_docs = self.cassandra_manager.search_documents_mmr(
            query_for_embedding, 
            n_results=k, 
            lambda_param=lambda_param
        )
        
        if not retrieved_docs:
            print("Aucun document pertinent trouvé dans la base de données.")
            return []
        
        print(f"📊 Documents récupérés: {len(retrieved_docs)}")
        
        # Formater les documents pour l'affichage/traitement
        all_docs = []
        for doc in retrieved_docs:
            doc_content = doc['content']
            all_docs.append(f"[Document]\n{doc_content}\n")
        
        return all_docs

    def analyze_claim(self, claim: str, retrieved_docs: List[str]) -> str:
        """Analyze the claim using retrieved documents."""
        prompt = format_prompt(self.analysis_prompt_template, claim=claim, retrieved_docs='\n\n'.join(retrieved_docs))
        result = self.ollama_client.generate(prompt, temperature=0.1)
        return result

    def generate_summary(self, analysis: str) -> str:
        """Generate a concise summary of the analysis."""
        prompt = format_prompt(self.summary_prompt_template, analysis=analysis)
        result = self.ollama_client.generate(prompt, temperature=0.3)
        return result

    def fact_check_claim(self, claim: str, lambda_param: float = 1.0) -> Dict[str, Any]:
        """Perform a complete fact-check on a claim."""
        print(f"\n🔍 Fact-checking: {claim}")
        
        # Step 1: Retrieve relevant documents
        print("📚 Retrieving relevant information...")
        retrieved_docs = self.retrieve_documents(claim, lambda_param=lambda_param)
        
        if not retrieved_docs:
            return {
                'claim': claim,
                'verdict': 'FALSE',
                'analysis': 'No relevant documents found',
                'summary': 'Cannot verify claim due to lack of relevant evidence',
                'documents_retrieved': 0,
                'error': 'No documents found'
            }
        
        # Step 2: Analyze the claim
        print("🧠 Analyzing claim against evidence...")
        analysis = self.analyze_claim(claim, retrieved_docs)
        
        # Step 3: Generate summary
        print("📝 Generating summary...")
        summary = self.generate_summary(analysis)
        
        # Extract verdict
        verdict = extract_verdict(analysis)
        
        return {
            'claim': claim,
            'verdict': verdict,
            'analysis': analysis,
            'summary': summary,
            'documents_retrieved': len(retrieved_docs),
            'error': None
        }

def load_test_cases() -> List[Dict[str, Any]]:
    import climate_dataset
    return climate_dataset.CLIMATE_DATASET
    # """Load test cases for evaluation."""
    # test_cases = [
    #     {
    #         'claim': 'Is the IPCC a political body?',
    #         'expected_verdict': 'FALSE',
    #         'category': 'controversies',
    #         'expected_output': 'The IPCC is a scientific body that assesses scientific literature, not a political organization.'
    #     },
    #     {
    #         'claim': 'Did warming stop between 1998 and 2013?',
    #         'expected_verdict': 'FALSE',
    #         'category': 'pause',
    #         'expected_output': 'No, warming did not stop between 1998 and 2013. That period was misinterpreted, and warming continued.'
    #     },
    #     {
    #         'claim': 'Is there a scientific consensus on climate change?',
    #         'expected_verdict': 'TRUE',
    #         'category': 'consensus',
    #         'expected_output': 'Yes, there is an overwhelming scientific consensus (97%+) that climate change is caused by human activity.'
    #     },
    #     {
    #         'claim': 'Do solar cycles explain current warming?',
    #         'expected_verdict': 'FALSE',
    #         'category': 'natural_cycles',
    #         'expected_output': 'No, solar cycles cannot explain current climate change. Solar activity has actually slightly decreased.'
    #     },
    #     {
    #         'claim': 'Are climate models reliable?',
    #         'expected_verdict': 'TRUE',
    #         'category': 'models',
    #         'expected_output': 'Climate models are reliable scientific tools that have proven effective in predicting climate changes.'
    #     },
    #     {
    #         'claim': 'Is the Arctic losing ice?',
    #         'expected_verdict': 'TRUE',
    #         'category': 'ice',
    #         'expected_output': 'Yes, the Arctic has been losing sea ice at an accelerated rate for several decades.'
    #     },
    #     {
    #         'claim': 'Is Antarctica gaining ice?',
    #         'expected_verdict': 'FALSE',
    #         'category': 'ice',
    #         'expected_output': 'Antarctica is losing ice mass overall, despite some localized gains.'
    #     },
    #     {
    #         'claim': 'Is CO2 beneficial for plants?',
    #         'expected_verdict': 'TRUE',
    #         'category': 'co2',
    #         'expected_output': 'Although CO2 is necessary for photosynthesis, excessive CO2 levels can have negative effects on some ecosystems.'
    #     },
    #     {
    #         'claim': 'Is sea level rise natural?',
    #         'expected_verdict': 'FALSE',
    #         'category': 'sea_level',
    #         'expected_output': 'While sea levels have fluctuated naturally, the current rise is mainly caused by human-induced climate change.'
    #     },
    #     {
    #         'claim': 'Is climate change part of a natural cycle?',
    #         'expected_verdict': 'FALSE',
    #         'category': 'natural_cycles',
    #         'expected_output': 'Although climate has experienced natural cycles, current warming is primarily caused by human activity.'
    #     }
    # ]
    # return test_cases

def evaluate_verdict_accuracy(predicted_verdict: str, expected_verdict: str) -> bool:
    """Evaluate if the predicted verdict matches the expected verdict."""
    # Normalize verdicts for comparison
    predicted = predicted_verdict.upper().strip()
    expected = expected_verdict.upper().strip()
    
    # Handle variations in verdict naming
    verdict_mapping = {
        'TRUE': ['TRUE'],
        'FALSE': ['FALSE']
    }
    
    # Check if predicted verdict matches expected
    for expected_key, variations in verdict_mapping.items():
        if expected == expected_key and predicted in variations:
            return True
    
    return False

def run_evaluation(lambda_param: float = 1.0) -> Dict[str, Any]:
    """Run the complete evaluation."""
    print("🚀 Starting app.py precision evaluation...")
    
    # Initialize evaluator
    evaluator = AppPrecisionEvaluator()
    
    # Load test cases
    test_cases = load_test_cases()
    
    # Run evaluation
    results = []
    start_time = time.time()
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"Test Case {i+1}/{len(test_cases)}: {test_case['category']}")
        print(f"{'='*60}")
        
        try:
            # Perform fact-check
            result = evaluator.fact_check_claim(test_case['claim'], lambda_param)
            
            # Evaluate accuracy
            verdict_correct = evaluate_verdict_accuracy(result['verdict'], test_case['expected_verdict'])
            
            # Store result
            test_result = {
                'test_case_id': i,
                'category': test_case['category'],
                'claim': test_case['claim'],
                'expected_verdict': test_case['expected_verdict'],
                'predicted_verdict': result['verdict'],
                'verdict_correct': verdict_correct,
                'documents_retrieved': result['documents_retrieved'],
                'analysis': result['analysis'],
                'summary': result['summary'],
                'error': result['error']
            }
            
            results.append(test_result)
            
            # Print result
            status = "✅ CORRECT" if verdict_correct else "❌ INCORRECT"
            print(f"{status} | Expected: {test_case['expected_verdict']} | Predicted: {result['verdict']}")
            print(f"Documents retrieved: {result['documents_retrieved']}")
            
        except Exception as e:
            print(f"❌ Error in test case {i+1}: {e}")
            results.append({
                'test_case_id': i,
                'category': test_case['category'],
                'claim': test_case['claim'],
                'expected_verdict': test_case['expected_verdict'],
                'predicted_verdict': 'ERROR',
                'verdict_correct': False,
                'documents_retrieved': 0,
                'analysis': '',
                'summary': '',
                'error': str(e)
            })
    
    end_time = time.time()
    evaluation_time = end_time - start_time
    
    # Calculate metrics
    total_tests = len(results)
    correct_verdicts = sum(1 for r in results if r['verdict_correct'])
    accuracy = correct_verdicts / total_tests if total_tests > 0 else 0
    
    # Calculate accuracy by category
    category_accuracy = {}
    for result in results:
        category = result['category']
        if category not in category_accuracy:
            category_accuracy[category] = {'correct': 0, 'total': 0}
        category_accuracy[category]['total'] += 1
        if result['verdict_correct']:
            category_accuracy[category]['correct'] += 1
    
    for category in category_accuracy:
        category_accuracy[category]['accuracy'] = (
            category_accuracy[category]['correct'] / category_accuracy[category]['total']
        )
    
    # Compile final results
    evaluation_results = {
        'evaluation_time': evaluation_time,
        'total_tests': total_tests,
        'correct_verdicts': correct_verdicts,
        'accuracy': accuracy,
        'category_accuracy': category_accuracy,
        'lambda_param': lambda_param,
        'test_results': results,
        'model_info': {
            'embedding_model': evaluator.cassandra_manager.embedding_model if evaluator.cassandra_manager else 'Unknown',
            'llm_model': 'llama2:7b (Ollama)',
            'total_questions': total_tests,
            'categories_tested': list(category_accuracy.keys())
        }
    }
    
    return evaluation_results

def save_results(results: Dict[str, Any], filename: str = None):
    """Save evaluation results to a JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"app_precision_eval_{timestamp}.json"
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {filepath}")
    return filepath

def print_summary(results: Dict[str, Any]):
    """Print a summary of the evaluation results."""
    print(f"\n{'='*60}")
    print("📊 EVALUATION SUMMARY")
    print(f"{'='*60}")
    
    print(f"⏱️  Total evaluation time: {results['evaluation_time']:.2f} seconds")
    print(f"📝 Total test cases: {results['total_tests']}")
    print(f"✅ Correct verdicts: {results['correct_verdicts']}")
    print(f"🎯 Overall accuracy: {results['accuracy']:.2%}")
    print(f"🔧 Lambda parameter: {results['lambda_param']}")
    
    print(f"\n📈 Accuracy by category:")
    for category, stats in results['category_accuracy'].items():
        print(f"  {category}: {stats['accuracy']:.2%} ({stats['correct']}/{stats['total']})")
    
    print(f"\n🤖 Model information:")
    print(f"  Embedding model: {results['model_info']['embedding_model']}")
    print(f"  LLM model: {results['model_info']['llm_model']}")
    print(f"  Categories tested: {', '.join(results['model_info']['categories_tested'])}")

def main():
    """Main function to run the evaluation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate app.py precision')
    parser.add_argument('--lambda', type=float, default=1.0, 
                       help='MMR lambda parameter (default: 1.0)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output filename (default: auto-generated)')
    
    args = parser.parse_args()
    
    try:
        # Run evaluation
        results = run_evaluation(args.__dict__['lambda'])
        
        # Print summary
        print_summary(results)
        # Save results
        save_results(results, args.output)
        
        print(f"\n🎉 Evaluation completed successfully!")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 