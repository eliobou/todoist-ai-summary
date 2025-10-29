#!/bin/bash
# Script d'installation automatique pour Todoist AI Summary

set -e  # Arrêt en cas d'erreur

echo "=========================================="
echo "📊 Todoist AI Summary - Installation"
echo "=========================================="
echo ""

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "Installez Python 3 avec : sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION détecté"

# Création de l'environnement virtuel
echo ""
echo "📦 Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Environnement virtuel créé"
else
    echo "⚠ Environnement virtuel déjà existant"
fi

# Activation de l'environnement
source venv/bin/activate

# Installation des dépendances
echo ""
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dépendances installées"

# Création de la structure de dossiers
echo ""
echo "📁 Création de la structure de dossiers..."
mkdir -p data/summaries
mkdir -p logs
mkdir -p src
echo "✓ Dossiers créés"

# Création du fichier __init__.py si inexistant
if [ ! -f "src/__init__.py" ]; then
    touch src/__init__.py
    echo "✓ src/__init__.py créé"
fi

# Copie du fichier .env.example si .env n'existe pas
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Fichier .env créé depuis .env.example"
        echo ""
        echo "⚠️  IMPORTANT : Éditez le fichier .env avec vos clés API !"
        echo "   nano .env"
    else
        echo "⚠ .env.example introuvable"
    fi
else
    echo "⚠ Fichier .env déjà existant (non modifié)"
fi

# Test de l'installation
echo ""
echo "🧪 Test de l'installation..."
python3 -c "import requests, openai, dotenv; print('✓ Modules importés avec succès')" || {
    echo "❌ Erreur lors de l'import des modules"
    exit 1
}

echo ""
echo "=========================================="
echo "✅ Installation terminée !"
echo "=========================================="
echo ""
echo "📝 Prochaines étapes :"
echo ""
echo "1. Configurez vos clés API dans .env :"
echo "   nano .env"
echo ""
echo "2. Obtenez votre token Todoist :"
echo "   https://todoist.com/app/settings/integrations/developer"
echo ""
echo "3. Obtenez votre clé OpenAI :"
echo "   https://platform.openai.com/api-keys"
echo ""
echo "4. Configurez un mot de passe d'application Gmail :"
echo "   https://myaccount.google.com/apppasswords"
echo ""
echo "5. Testez le script :"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "6. Configurez cron pour l'exécution automatique (voir README.md)"
echo ""
echo "🚀 Bonne utilisation !"
