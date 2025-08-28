#!/usr/bin/env python3
"""
Évaluation de l'accuracy de l'API Quantum Fact-Checker
Teste l'API avec un dataset de claims et compare les verdicts
"""

import requests
import json
import time
from typing import List, Dict, Any
from climate_dataset import CLIMATE_DATASET, get_dataset_by_category, get_random_subset

class APIEvaluator:
    def __init__(self, api_url="http://localhost:8000/fact-check"):
        """Initialiser l'évaluateur d'API"""
        self.api_url = api_url
        self.results = []
        
    def test_single_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Tester un seul claim avec l'API"""
        try:
            # Préparer la requête
            payload = {
                "message": claim["claim"],
                "language": "en"
            }
            
            # Appeler l'API
            start_time = time.time()
            response = requests.post(self.api_url, json=payload)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                api_response = response.json()
                
                # Extraire les informations
                api_verdict = api_response.get("verdict", "UNKNOWN")
                api_confidence = api_response.get("confidence_level", "UNKNOWN")
                api_score = api_response.get("certainty_score", 0.0)
                api_explanation = api_response.get("explanation", "")
                api_sources = api_response.get("sources_used", [])
                
                # Comparer avec le verdict attendu
                expected_verdict = claim["expected_verdict"]
                is_correct = api_verdict == expected_verdict
                
                result = {
                    "claim": claim["claim"],
                    "category": claim["category"],
                    "expected_verdict": expected_verdict,
                    "api_verdict": api_verdict,
                    "is_correct": is_correct,
                    "api_confidence": api_confidence,
                    "api_score": api_score,
                    "api_explanation": api_explanation[:200] + "..." if len(api_explanation) > 200 else api_explanation,
                    "api_sources": api_sources,
                    "processing_time": processing_time,
                    "status": "success"
                }
                
            else:
                result = {
                    "claim": claim["claim"],
                    "category": claim["category"],
                    "expected_verdict": claim["expected_verdict"],
                    "api_verdict": "ERROR",
                    "is_correct": False,
                    "api_confidence": "ERROR",
                    "api_score": 0.0,
                    "api_explanation": f"HTTP {response.status_code}: {response.text}",
                    "api_sources": [],
                    "processing_time": processing_time,
                    "status": "error"
                }
                
        except Exception as e:
            result = {
                "claim": claim["claim"],
                "category": claim["category"],
                "expected_verdict": claim["expected_verdict"],
                "api_verdict": "EXCEPTION",
                "is_correct": False,
                "api_confidence": "EXCEPTION",
                "api_score": 0.0,
                "api_explanation": f"Exception: {str(e)}",
                "api_sources": [],
                "processing_time": 0.0,
                "status": "exception"
            }
        
        return result
    
    def evaluate_dataset(self, dataset: List[Dict[str, Any]], max_tests: int = None) -> Dict[str, Any]:
        """Évaluer l'API avec un dataset complet"""
        if max_tests:
            dataset = dataset[:max_tests]
        
        print(f"🧪 Évaluation de l'API avec {len(dataset)} claims...")
        print("=" * 60)
        
        correct_count = 0
        total_count = len(dataset)
        
        for i, claim in enumerate(dataset, 1):
            print(f"Test {i}/{total_count}: {claim['claim'][:50]}...")
            
            result = self.test_single_claim(claim)
            self.results.append(result)
            
            if result["is_correct"]:
                correct_count += 1
                print(f"  ✅ Correct: {result['expected_verdict']} == {result['api_verdict']}")
            else:
                print(f"  ❌ Incorrect: {result['expected_verdict']} != {result['api_verdict']}")
            
            # Pause entre les requêtes pour éviter de surcharger l'API
            time.sleep(1)
        
        # Calculer les métriques
        accuracy = correct_count / total_count if total_count > 0 else 0
        
        # Statistiques par catégorie
        category_stats = {}
        for result in self.results:
            cat = result["category"]
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "correct": 0}
            category_stats[cat]["total"] += 1
            if result["is_correct"]:
                category_stats[cat]["correct"] += 1
        
        # Statistiques par verdict
        verdict_stats = {}
        for result in self.results:
            expected = result["expected_verdict"]
            if expected not in verdict_stats:
                verdict_stats[expected] = {"total": 0, "correct": 0}
            verdict_stats[expected]["total"] += 1
            if result["is_correct"]:
                verdict_stats[expected]["correct"] += 1
        
        # Temps de traitement moyen
        avg_processing_time = sum(r["processing_time"] for r in self.results if r["status"] == "success") / len([r for r in self.results if r["status"] == "success"]) if any(r["status"] == "success" for r in self.results) else 0
        
        evaluation_summary = {
            "total_tests": total_count,
            "correct_predictions": correct_count,
            "accuracy": accuracy,
            "avg_processing_time": avg_processing_time,
            "category_stats": category_stats,
            "verdict_stats": verdict_stats,
            "results": self.results
        }
        
        return evaluation_summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Afficher un résumé de l'évaluation"""
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS DE L'ÉVALUATION")
        print("=" * 60)
        
        print(f"🎯 Accuracy globale: {summary['accuracy']:.2%} ({summary['correct_predictions']}/{summary['total_tests']})")
        print(f"⏱️ Temps de traitement moyen: {summary['avg_processing_time']:.2f} secondes")
        
        print("\n📈 Performance par catégorie:")
        for cat, stats in summary["category_stats"].items():
            cat_accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {cat}: {cat_accuracy:.2%} ({stats['correct']}/{stats['total']})")
        
        print("\n🎯 Performance par verdict:")
        for verdict, stats in summary["verdict_stats"].items():
            verdict_accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {verdict}: {verdict_accuracy:.2%} ({stats['correct']}/{stats['total']})")
        
        # Afficher les erreurs
        errors = [r for r in summary["results"] if not r["is_correct"]]
        if errors:
            print(f"\n❌ Erreurs ({len(errors)}):")
            for error in errors[:5]:  # Afficher les 5 premières erreurs
                print(f"  • {error['claim'][:50]}...")
                print(f"    Attendu: {error['expected_verdict']}, Obtenu: {error['api_verdict']}")
        
        # Sauvegarder les résultats
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"api_evaluation_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n💾 Résultats sauvegardés dans: {filename}")

def main():
    """Fonction principale"""
    print("🔬 Évaluateur d'Accuracy de l'API Quantum Fact-Checker")
    print("=" * 60)
    
    # Initialiser l'évaluateur
    evaluator = APIEvaluator()
    
    # Options d'évaluation
    print("Options d'évaluation:")
    print("1. Test complet (tous les claims)")
    print("2. Test par catégorie")
    print("3. Test aléatoire (50 claims)")
    print("4. Test rapide (10 claims)")
    
    choice = input("\nChoisissez une option (1-4): ").strip()
    
    if choice == "1":
        dataset = CLIMATE_DATASET
        print(f"🧪 Test complet avec {len(dataset)} claims")
    elif choice == "2":
        print("\nCatégories disponibles:")
        categories = set(item["category"] for item in CLIMATE_DATASET)
        for i, cat in enumerate(sorted(categories), 1):
            print(f"  {i}. {cat}")
        cat_choice = input("Choisissez une catégorie (numéro): ").strip()
        try:
            cat_index = int(cat_choice) - 1
            selected_cat = sorted(categories)[cat_index]
            dataset = get_dataset_by_category(selected_cat)
            print(f"🧪 Test de la catégorie '{selected_cat}' avec {len(dataset)} claims")
        except (ValueError, IndexError):
            print("❌ Choix invalide, utilisation du dataset complet")
            dataset = CLIMATE_DATASET
    elif choice == "3":
        dataset = get_random_subset(50)
        print(f"🧪 Test aléatoire avec {len(dataset)} claims")
    elif choice == "4":
        dataset = get_random_subset(10)
        print(f"🧪 Test rapide avec {len(dataset)} claims")
    else:
        print("❌ Choix invalide, utilisation du test rapide")
        dataset = get_random_subset(10)
    
    # Confirmer le test
    confirm = input(f"\nConfirmer le test avec {len(dataset)} claims ? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Test annulé")
        return
    
    # Lancer l'évaluation
    summary = evaluator.evaluate_dataset(dataset)
    evaluator.print_summary(summary)

if __name__ == "__main__":
    main()
