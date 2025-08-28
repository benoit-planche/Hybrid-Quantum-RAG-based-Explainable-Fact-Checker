#!/bin/bash

# Script de lancement pour l'API Quantum Fact Checker (Version Complète)
# Utilise l'environnement conda qrag_api avec Python 3.11

echo "🚀 Lancement de l'API Quantum Fact Checker (Version Complète)"
echo "=============================================================="

# Vérifier si conda est disponible
if ! command -v conda &> /dev/null; then
    echo "❌ Conda n'est pas installé ou n'est pas dans le PATH"
    exit 1
fi

# Vérifier si l'environnement existe
if ! conda env list | grep -q "qrag_api"; then
    echo "❌ L'environnement 'qrag_api' n'existe pas"
    echo "💡 Créez-le avec: conda create -n qrag_api python=3.11 -y"
    exit 1
fi

# Activer l'environnement
echo "🔧 Activation de l'environnement conda 'qrag_api'..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate qrag_api

if [ $? -ne 0 ]; then
    echo "❌ Impossible d'activer l'environnement 'qrag_api'"
    exit 1
fi

echo "✅ Environnement activé: $(python --version)"

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."
python -c "import fastapi, cassandra, llama_index" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Certaines dépendances sont manquantes"
    echo "💡 Installez-les avec: pip install -r requirements_api.txt && pip install cassandra-driver[libev] llama-index"
    exit 1
fi

echo "✅ Toutes les dépendances sont installées"

# Vérifier si Ollama est en cours d'exécution
echo "🔍 Vérification d'Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama ne semble pas être en cours d'exécution"
    echo "💡 Lancez Ollama avec: ollama serve"
    echo "   Puis téléchargez un modèle: ollama pull llama2"
fi

# Lancer l'API
echo "🚀 Lancement de l'API..."
echo "📡 L'API sera accessible sur: http://localhost:8000"
echo "📖 Documentation: http://localhost:8000/docs"
echo ""
echo "⏹️  Pour arrêter l'API, appuyez sur Ctrl+C"
echo ""

python quantum_fact_checker_api.py
