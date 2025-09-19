#!/bin/bash

# Script pour démarrer l'application complète
# Ce script lance tous les services nécessaires

echo "🚀 Démarrage de l'application de classification de documents..."

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose d'abord."
    exit 1
fi

# Créer le fichier .env.secrets s'il n'existe pas
if [ ! -f .env.secrets ]; then
    echo "📝 Création du fichier .env.secrets..."
    cp env.secrets.template .env.secrets
    echo "⚠️  Veuillez modifier le fichier .env.secrets avec vos valeurs de production"
fi

# Créer le fichier config.yaml s'il n'existe pas
if [ ! -f config.yaml ]; then
    echo "📝 Création du fichier config.yaml..."
    cp config.yaml.template config.yaml
fi

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p data/raw data/processed models/clip-vit-base mlruns

# Construire et démarrer les services
echo "🔨 Construction des images Docker..."
docker-compose -f docker-compose.dev.yml build

echo "🚀 Démarrage des services..."
docker-compose -f docker-compose.dev.yml up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 10

# Vérifier le statut des services
echo "🔍 Vérification du statut des services..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "✅ Application démarrée avec succès!"
echo ""
echo "🌐 URLs des services:"
echo "   📄 Streamlit App:     http://localhost:8501"
echo "   🔌 API:               http://localhost:8000"
echo "   🔐 Auth Service:      http://localhost:7000"
echo "   📊 MLflow UI:         http://localhost:5000"
echo "   📈 Prometheus:        http://localhost:9090"
echo "   📊 Grafana:           http://localhost:3000"
echo ""
echo "🔑 Identifiants par défaut:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "📖 Documentation API: http://localhost:8000/docs"
echo ""
echo "Pour arrêter les services: docker-compose -f docker-compose.dev.yml down"
