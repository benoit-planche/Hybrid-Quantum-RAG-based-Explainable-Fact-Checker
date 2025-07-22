# 📊 App.py Precision Evaluation

Ce script évalue la précision de votre application Streamlit (`app.py`) en testant sa capacité à fact-checker des affirmations sur le changement climatique.

## 🎯 Objectif

Tester la précision des verdicts générés par votre système de fact-checking RAG en comparant les verdicts prédits avec les verdicts attendus pour un ensemble de test d'affirmations sur le climat.

## 📋 Fonctionnalités

- **Test de 10 affirmations** couvrant 8 catégories différentes
- **Évaluation des verdicts** : TRUE ou FALSE seulement
- **Analyse par catégorie** pour identifier les forces et faiblesses
- **Métriques détaillées** : précision globale et par catégorie
- **Sauvegarde des résultats** au format JSON

## 🚀 Utilisation

### Méthode 1 : Script simple

```bash
cd eval
python run_app_precision_eval.py
```

### Méthode 2 : Script avancé avec paramètres

```bash
cd eval
python evaluate_app_precision.py --lambda 0.7 --output my_results.json
```

### Paramètres disponibles

- `--lambda` : Paramètre MMR (0.0-1.0, défaut: 0.5)
- `--output` : Nom du fichier de sortie (défaut: auto-généré)

## 📊 Métriques évaluées

### Précision des verdicts

- **Verdict correct** : Le verdict prédit correspond au verdict attendu
- **Précision globale** : Pourcentage de verdicts corrects sur l'ensemble des tests
- **Précision par catégorie** : Performance sur chaque type d'affirmation

### Catégories testées

1. **controversies** : Controverses sur les organisations scientifiques
2. **pause** : Pause dans le réchauffement climatique
3. **consensus** : Consensus scientifique
4. **natural_cycles** : Cycles naturels et cycles solaires
5. **models** : Fiabilité des modèles climatiques
6. **ice** : Perte de glace (Arctique/Antarctique)
7. **co2** : Effets du CO2 sur les plantes
8. **sea_level** : Élévation du niveau de la mer

## 📈 Interprétation des résultats

### Scores de précision

- **90-100%** : Excellent - Le système fonctionne très bien
- **70-89%** : Bon - Quelques améliorations possibles
- **50-69%** : Moyen - Améliorations nécessaires
- **<50%** : Faible - Problèmes majeurs à résoudre

### Analyse des erreurs

- **Faux positifs** : Verdict TRUE pour une affirmation fausse
- **Faux négatifs** : Verdict FALSE pour une affirmation vraie
- **Verdicts FALSE par défaut** : Manque de preuves pertinentes

## 🔧 Prérequis

1. **Cassandra Vector Store** initialisé avec des documents
2. **Ollama** en cours d'exécution avec le modèle `llama2:7b`
3. **Documents indexés** dans la base vectorielle

### Vérification des prérequis

```bash
# Vérifier qu'Ollama fonctionne
ollama list

# Vérifier que Cassandra est accessible
python -c "from system.cassandra_manager import create_cassandra_manager; cm = create_cassandra_manager(); print(cm.get_collection_info())"
```

## 📁 Structure des résultats

Le script génère un fichier JSON avec :

```json
{
  "evaluation_time": 120.5,
  "total_tests": 10,
  "correct_verdicts": 7,
  "accuracy": 0.7,
  "category_accuracy": {
    "consensus": {"correct": 1, "total": 1, "accuracy": 1.0},
    "ice": {"correct": 1, "total": 2, "accuracy": 0.5}
  },
  "lambda_param": 0.5,
  "test_results": [...],
  "model_info": {...}
}
```

## 🛠️ Dépannage

### Erreur : "Cassandra Vector Store non initialisé"

```bash
# Vérifier la configuration Cassandra
python -c "from system.cassandra_manager import create_cassandra_manager; cm = create_cassandra_manager()"
```

### Erreur : "Aucun document dans la base vectorielle"

```bash
# Indexer des documents
cd system
python index_documents.py
```

### Erreur : "Ollama non accessible"

```bash
# Démarrer Ollama
ollama serve
```

## 📝 Exemple de sortie

```
🚀 Starting app.py precision evaluation...

============================================================
Test Case 1/10: controversies
============================================================
🔍 Fact-checking: Is the IPCC a political body?
📚 Retrieving relevant information...
🔍 Requêtes de recherche générées: IPCC political body, IPCC scientific organization, IPCC intergovernmental panel
📊 Documents récupérés: 3/5 pertinents
🧠 Analyzing claim against evidence...
📝 Generating summary...
✅ CORRECT | Expected: FALSE | Predicted: FALSE
Documents retrieved: 3

============================================================
Test Case 2/10: pause
============================================================
...

📊 EVALUATION SUMMARY
============================================================
⏱️  Total evaluation time: 45.23 seconds
📝 Total test cases: 10
✅ Correct verdicts: 7
🎯 Overall accuracy: 70.00%
🔧 Lambda parameter: 0.5

📈 Accuracy by category:
  controversies: 100.00% (1/1)
  pause: 100.00% (1/1)
  consensus: 100.00% (1/1)
  natural_cycles: 50.00% (1/2)
  models: 100.00% (1/1)
  ice: 50.00% (1/2)
  co2: 100.00% (1/1)
  sea_level: 100.00% (1/1)

🤖 Model information:
  Embedding model: llama2:7b
  LLM model: llama2:7b (Ollama)
  Categories tested: controversies, pause, consensus, natural_cycles, models, ice, co2, sea_level

💾 Results saved to: app_precision_eval_20241216_143022.json

🎉 Evaluation completed successfully!
```

## 🔄 Amélioration continue

1. **Analyser les erreurs** pour identifier les patterns
2. **Ajuster les prompts** selon les résultats
3. **Optimiser les paramètres MMR** (lambda)
4. **Améliorer la qualité des embeddings**
5. **Ajouter plus de documents** à la base de connaissances

## 📞 Support

En cas de problème, vérifiez :

1. Les logs d'erreur dans la console
2. La configuration de Cassandra
3. L'état d'Ollama
4. La présence de documents indexés
