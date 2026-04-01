#!/bin/bash

# Script de réinitialisation de la base de données NetVis V1
# Ce script supprime les volumes Docker pour effacer les données persistantes et redémarre l'infrastructure.

echo "--- Réinitialisation de l'environnement NetVis ---"

# 1. Arrêt des conteneurs et suppression des volumes (-v)
docker-compose down -v

# 2. Nettoyage des fichiers de cache Python (optionnel mais propre)
find . -type d -name "__pycache__" -exec rm -rf {} +

# 3. Relance de l'infrastructure
docker-compose up -d

echo "------------------------------------------------"
echo "Infrastructure redémarrée avec une base propre."
echo "Attente de l'initialisation de PostgreSQL..."
sleep 5
echo "NetVis est prêt !"
