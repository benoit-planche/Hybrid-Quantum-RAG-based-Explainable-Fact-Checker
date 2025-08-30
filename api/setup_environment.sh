#!/bin/bash

echo "🚀 Création de l'environnement Python pour l'API QRAG..."

# Vérifier si conda est installé
if command -v conda &> /dev/null; then
    echo "✅ Conda détecté, création de l'environnement..."
    
    # Créer l'environnement conda
    conda env create -f environment.yml
    
    if [ $? -eq 0 ]; then
        echo "🎉 Environnement conda créé avec succès !"
        echo "📝 Pour l'activer: conda activate qrag_api"
    else
        echo "❌ Erreur lors de la création de l'environnement conda"
        exit 1
    fi
    
elif command -v python3 &> /dev/null; then
    echo "✅ Python3 détecté, création d'environnement virtuel..."
    
    # Vérifier la version Python
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    echo "🐍 Version Python détectée: $PYTHON_VERSION"
    
    # Créer l'environnement virtuel
    python3 -m venv qrag_api
    
    if [ $? -eq 0 ]; then
        echo "🎉 Environnement virtuel créé avec succès !"
        echo "📝 Pour l'activer: source qrag_api_env/bin/activate"
        
        # Activer et installer les dépendances
        source qrag_api_env/bin/activate
        pip install --upgrade pip
        pip install -r requirements_api.txt
        
        if [ $? -eq 0 ]; then
            echo "✅ Toutes les dépendances installées !"
        else
            echo "❌ Erreur lors de l'installation des dépendances"
            exit 1
        fi
    else
        echo "❌ Erreur lors de la création de l'environnement virtuel"
        exit 1
    fi
    
else
    echo "❌ Aucun environnement Python détecté"
    echo "💡 Installez Python3 ou Conda d'abord"
    exit 1
fi

echo ""
echo "🎯 Prochaines étapes:"
echo "1. Activer l'environnement:"
if command -v conda &> /dev/null; then
    echo "   conda activate qrag_api"
else
    echo "   source qrag_api_env/bin/activate"
fi
echo "2. Vérifier l'installation: python -c 'import qiskit; print(\"✅ Qiskit OK\")'"
echo "3. Lancer l'API: python quantum_fact_checker_api.py"
echo ""
