# Évaluation MMR (Maximum Marginal Relevance)

Ce dossier contient les scripts pour évaluer votre modèle RAG avec MMR (Maximum Marginal Relevance) et comparer les performances avec la recherche simple.

## Scripts disponibles

### 1. `evaluate_rag_chromadb_mmr.py`

Script d'évaluation complet avec MMR qui utilise DeepEval pour mesurer toutes les métriques importantes.

**Fonctionnalités :**

- Évaluation avec DeepEval (AnswerRelevancy, ContextualRelevancy, Faithfulness, etc.)
- Utilisation de MMR pour la sélection de documents
- Calcul des métriques de diversité
- Comparaison avec la recherche simple
- Sauvegarde des résultats en JSON

### 2. `test_mmr_comparison.py`

Script de test rapide pour comparer MMR vs recherche simple sur quelques questions.

**Fonctionnalités :**

- Test rapide avec 3-5 questions
- Comparaison des métriques de diversité
- Test avec différents paramètres λ
- Affichage détaillé des résultats

### 3. `run_mmr_evaluation.py`

Script principal pour exécuter les évaluations MMR avec différents paramètres.

**Options :**

- `--lambda_param` : Paramètre MMR (0.0 = max diversité, 1.0 = max pertinence)
- `--questions` : Nombre de questions à tester
- `--comparison` : Étude comparative avec différents λ

## Utilisation

### Test rapide de comparaison

```bash
cd eval
python test_mmr_comparison.py
```

### Évaluation complète avec MMR

```bash
cd eval
python run_mmr_evaluation.py --lambda_param 0.5 --questions 10
```

### Étude comparative complète

```bash
cd eval
python run_mmr_evaluation.py --comparison
```

### Évaluation directe

```bash
cd eval
python evaluate_rag_chromadb_mmr.py
```

## Paramètres MMR

Le paramètre λ (lambda) contrôle l'équilibre entre pertinence et diversité :

- **λ = 0.0** : Maximum de diversité (documents très différents)
- **λ = 0.25** : Plus de diversité que de pertinence
- **λ = 0.5** : Équilibre entre pertinence et diversité
- **λ = 0.75** : Plus de pertinence que de diversité
- **λ = 1.0** : Maximum de pertinence (comme la recherche simple)

## Métriques calculées

### Métriques DeepEval

- **AnswerRelevancy** : Pertinence de la réponse
- **ContextualRelevancy** : Pertinence du contexte
- **Faithfulness** : Fidélité à la source
- **ContextualRecall** : Rappel du contexte
- **ContextualPrecision** : Précision du contexte

### Métriques MMR

- **Score de diversité** : Mesure de la diversité des documents sélectionnés
- **Similarité moyenne** : Similarité moyenne avec la requête
- **Overlap ratio** : Proportion de documents communs avec la recherche simple
- **Score MMR** : Score combiné pertinence + diversité

## Interprétation des résultats

### Comparaison MMR vs Recherche simple

1. **Diversité** : MMR devrait avoir un score de diversité plus élevé
2. **Pertinence** : La recherche simple devrait avoir une similarité moyenne plus élevée
3. **Overlap** : Plus λ est proche de 1.0, plus l'overlap avec la recherche simple est élevé

### Choix du paramètre λ

- **Pour des questions complexes** : λ = 0.25-0.5 (plus de diversité)
- **Pour des questions spécifiques** : λ = 0.75-1.0 (plus de pertinence)
- **Équilibre général** : λ = 0.5

## Fichiers de résultats

Les résultats sont sauvegardés dans des fichiers JSON avec le format :

- `rag_eval_mmr_lambda{λ}_{timestamp}.json`

Ces fichiers contiennent :

- Résultats DeepEval complets
- Métriques MMR détaillées
- Analyse par catégorie
- Détails de chaque question testée

## Exemple de sortie

```
🧪 Évaluation du RAG avec ChromaDB et MMR
🤖 Modèle d'embedding: llama2:7b
📊 Paramètre MMR (λ): 0.5
📋 10 cas de test
============================================================

🔍 RÉSULTATS DEEPEVAL:
  AnswerRelevancy: 0.823
  ContextualRelevancy: 0.756
  Faithfulness: 0.891
  ContextualRecall: 0.734
  ContextualPrecision: 0.812

📈 MÉTRIQUES MMR:
  Similarité moyenne: 0.745
  Score MMR moyen: 0.678
  Diversité moyenne: 0.234
  Longueur contexte moyenne: 2847 caractères
  Overlap MMR/Simple: 0.456
```

## Troubleshooting

### Erreur "Aucun embedding trouvé"

Assurez-vous que votre base de données ChromaDB contient des documents indexés :

```bash
cd system
python index_documents.py
```

### Erreur de connexion Ollama

Vérifiez qu'Ollama est en cours d'exécution :

```bash
ollama serve
```

### Erreur de dépendances

Installez les dépendances d'évaluation :

```bash
pip install -r requirements_eval.txt
```
