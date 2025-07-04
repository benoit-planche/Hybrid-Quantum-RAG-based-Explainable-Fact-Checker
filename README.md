# 🌍 RAG-based Explainable Fact Checker

Un système de fact-checking basé sur RAG (Retrieval-Augmented Generation) pour détecter la désinformation sur le changement climatique.

## 🎯 Fonctionnalités

- **Fact-checking automatique** sur le changement climatique
- **Recherche dans une base de connaissances** scientifique
- **Réponses explicables** avec sources
- **Interface Streamlit** intuitive
- **Évaluation complète** avec DeepEval

## 🏗️ Architecture

```
├── app.py                    # Application principale Streamlit
├── ollama_utils.py           # Utilitaires Ollama (LLM + Embeddings)
├── ollama_config.py          # Configuration Ollama
├── data_loader_ollama.py     # Chargeur de données avec Pinecone
├── pdf_loader.py             # Chargeur de documents PDF
├── evaluate_with_dataset.py  # Script d'évaluation DeepEval
├── climate_dataset.py        # Dataset d'évaluation (100+ questions)
└── requirements.txt          # Dépendances principales
```

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <repository-url>
cd RAG-based-Explainable-Fact-Checker
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration Ollama

```bash
# Installer Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Démarrer Ollama
ollama serve

# Télécharger le modèle
ollama pull llama2:7b
```

### 4. Configuration Pinecone

1. Créer un compte sur [Pinecone](https://www.pinecone.io/)
2. Créer un index Serverless
3. Copier l'API key

### 5. Configuration environnement

```bash
cp env_example.txt .env
# Éditer .env avec vos clés API
```

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2000

# Pinecone Serverless Configuration
PINECONE_API_KEY=votre_cle_api_pinecone
PINECONE_INDEX_NAME=fact-checker-index
```

## 📊 Chargement des données

### 1. Préparer les documents

Placez vos fichiers PDF dans le dossier `rapport/`

### 2. Charger vers Pinecone

```bash
python data_loader_ollama.py
```

## 🎮 Utilisation

### Lancer l'application

```bash
streamlit run app.py
```

### Utiliser l'interface

1. **Posez une question** sur le changement climatique
2. **Obtenez une réponse** fact-checkée
3. **Consultez les sources** utilisées
4. **Explorez les explications** détaillées

## 🧪 Évaluation

### Installation DeepEval

```bash
pip install -r requirements_eval.txt
```

### Évaluation complète

```bash
python evaluate_with_dataset.py
```

### Métriques évaluées

- **AnswerRelevancy** : Pertinence de la réponse
- **ContextRelevancy** : Pertinence du contexte
- **Faithfulness** : Fidélité aux sources

## 📁 Structure des fichiers

### Core du système

- `app.py` - Application Streamlit principale
- `ollama_utils.py` - Utilitaires Ollama (LLM + Embeddings)
- `ollama_config.py` - Configuration Ollama
- `data_loader_ollama.py` - Chargeur de données avec Pinecone
- `pdf_loader.py` - Chargeur de documents PDF

### Évaluation

- `evaluate_with_dataset.py` - Script d'évaluation DeepEval
- `climate_dataset.py` - Dataset d'évaluation (100+ questions)
- `requirements_eval.txt` - Dépendances évaluation
- `README_EVALUATION.md` - Guide d'évaluation détaillé

### Configuration

- `requirements.txt` - Dépendances principales
- `env_example.txt` - Exemple de configuration
- `.gitignore` - Fichiers à ignorer

## 🔍 Fonctionnalités avancées

### Recherche RAG

- **Embeddings** avec Ollama
- **Stockage vectoriel** Pinecone Serverless
- **Recherche sémantique** pour contexte pertinent

### Interface utilisateur

- **Interface Streamlit** moderne
- **Réponses explicables** avec sources
- **Historique des questions**
- **Export des résultats**

### Évaluation automatique

- **Dataset de 100+ questions** sur le climat
- **Métriques DeepEval** standardisées
- **Comparaison RAG vs Direct**
- **Analyse par catégorie**

## 🚨 Dépannage

### Ollama ne répond pas

```bash
# Vérifier qu'Ollama est démarré
ollama serve

# Tester la connexion
curl http://localhost:11434/api/tags
```

### Pinecone erreur de connexion

- Vérifiez votre API key
- Vérifiez que l'index existe
- Testez avec `python test_pinecone_serverless.py`

### Erreur de dépendances

```bash
pip install --upgrade -r requirements.txt
```

## 📈 Performance

### Temps de traitement

- **Embeddings** : ~30 secondes par chunk
- **Génération de réponse** : ~10-20 secondes
- **Recherche RAG** : ~5-10 secondes

### Optimisations possibles

- Utiliser un modèle plus rapide pour les embeddings
- Paralléliser les requêtes
- Optimiser la taille des chunks

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :

1. Vérifiez la documentation
2. Consultez les logs d'erreur
3. Testez chaque composant individuellement
4. Ouvrez une issue sur GitHub
