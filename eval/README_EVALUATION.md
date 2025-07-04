# 🧪 Guide d'évaluation du fact-checker avec DeepEval

## 📋 Vue d'ensemble

Ce guide vous explique comment évaluer votre système de fact-checking sur le changement climatique avec DeepEval.

## 🎯 Objectifs de l'évaluation

1. **Comparer les performances** RAG vs Direct
2. **Évaluer la précision** des réponses
3. **Mesurer la pertinence** du contexte utilisé
4. **Tester la fidélité** aux sources

## 📊 Dataset d'évaluation

Le dataset contient **100+ questions** réparties en catégories :

- **Consensus scientifique** (10 questions)
- **Températures** (15 questions)
- **CO2 et gaz à effet de serre** (15 questions)
- **Modèles climatiques** (10 questions)
- **Pause du réchauffement** (10 questions)
- **Cycles naturels** (15 questions)
- **Glace et glaciers** (10 questions)
- **Niveau de la mer** (10 questions)
- **Événements extrêmes** (10 questions)
- **Océans** (10 questions)
- **Controverses** (10 questions)

## 🚀 Installation

```bash
# Installer DeepEval et dépendances
pip install -r requirements_eval.txt

# Vérifier l'installation
python -c "import deepeval; print('DeepEval installé avec succès')"
```

## 🔧 Configuration

Assurez-vous que votre fichier `.env` contient :

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b

# Pinecone Configuration
PINECONE_API_KEY=votre_cle_api_pinecone
PINECONE_INDEX_NAME=fact-checker-index
```

## 🧪 Exécution des évaluations

### 1. Évaluation complète (recommandée)

```bash
python evaluate_with_dataset.py
```

Cette évaluation :

- Teste **30 questions** avec RAG
- Teste **30 questions** sans RAG
- Compare les performances
- Sauvegarde les résultats détaillés

### 2. Évaluation par catégorie

```python
from climate_dataset import get_dataset_by_category

# Évaluer seulement les questions sur le consensus
consensus_questions = get_dataset_by_category("consensus")
```

### 3. Évaluation personnalisée

```python
from evaluate_with_dataset import ComprehensiveFactCheckerEvaluator

evaluator = ComprehensiveFactCheckerEvaluator(use_rag=True)
results = await evaluator.evaluate_model(max_questions=20)
```

## 📈 Métriques évaluées

### AnswerRelevancy

- **Objectif** : La réponse est-elle pertinente à la question ?
- **Seuil** : 0.7
- **Interprétation** : Score > 0.8 = Excellent

### ContextRelevancy

- **Objectif** : Le contexte utilisé est-il pertinent ?
- **Seuil** : 0.7
- **Interprétation** : Score > 0.8 = Excellent

### Faithfulness

- **Objectif** : La réponse est-elle fidèle au contexte fourni ?
- **Seuil** : 0.7
- **Interprétation** : Score > 0.8 = Excellent

## 📊 Interprétation des résultats

### Scores par métrique

- **0.8-1.0** : Excellent
- **0.7-0.8** : Bon
- **0.6-0.7** : Acceptable
- **< 0.6** : À améliorer

### Comparaison RAG vs Direct

- **RAG > Direct** : Le système RAG améliore les performances
- **RAG ≈ Direct** : Le RAG n'apporte pas d'amélioration significative
- **RAG < Direct** : Le RAG dégrade les performances

## 📁 Fichiers de sortie

### comprehensive_evaluation_results.json

Contient :

- Métriques détaillées pour RAG et Direct
- Toutes les questions testées
- Réponses attendues vs obtenues
- Analyse par catégorie

### Structure des résultats

```json
{
  "rag_results": {
    "metrics": {
      "AnswerRelevancy": 0.85,
      "ContextRelevancy": 0.78,
      "Faithfulness": 0.82
    },
    "test_cases": [...]
  },
  "direct_results": {
    "metrics": {...},
    "test_cases": [...]
  }
}
```

## 🔍 Analyse des résultats

### 1. Performance globale

```python
import json

with open("comprehensive_evaluation_results.json", "r") as f:
    results = json.load(f)

rag_score = results["rag_results"]["metrics"]["AnswerRelevancy"]
direct_score = results["direct_results"]["metrics"]["AnswerRelevancy"]

print(f"Amélioration RAG: {rag_score - direct_score:.3f}")
```

### 2. Analyse par catégorie

```python
# Analyser les performances par catégorie
categories = {}
for test_case in results["rag_results"]["test_cases"]:
    cat = test_case["category"]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(test_case)

for cat, cases in categories.items():
    print(f"{cat}: {len(cases)} questions")
```

## 🚨 Dépannage

### Erreur : "DeepEval not found"

```bash
pip install deepeval
```

### Erreur : "Pinecone connection failed"

- Vérifiez votre API key
- Vérifiez que l'index existe
- Testez la connexion : `python test_pinecone_serverless.py`

### Erreur : "Ollama not responding"

- Vérifiez qu'Ollama est démarré : `ollama serve`
- Testez la connexion : `python test_ollama_connection.py`

## 📈 Optimisation

### Améliorer les scores

1. **Ajuster les prompts** pour plus de précision
2. **Optimiser la recherche** dans Pinecone
3. **Améliorer le chunking** des documents
4. **Utiliser un modèle plus performant**

### Ajouter des métriques

```python
from deepeval.metrics import ContextRecall

metrics = [
    AnswerRelevancy(threshold=0.7),
    ContextRelevancy(threshold=0.7),
    Faithfulness(threshold=0.7),
    ContextRecall(threshold=0.7)  # Nouvelle métrique
]
```

## 🎯 Prochaines étapes

1. **Exécuter l'évaluation** dès que votre script de chargement se termine
2. **Analyser les résultats** par catégorie
3. **Identifier les points d'amélioration**
4. **Itérer** sur le système

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs d'erreur
2. Testez chaque composant individuellement
3. Consultez la documentation DeepEval
4. Vérifiez la configuration Ollama et Pinecone
