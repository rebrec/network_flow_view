# NetVis V1 - Observatoire de Flux Réseau On-Prem

NetVis est un outil d'observabilité réseau conçu pour offrir une vision consolidée des flux réels observés (Nexus, F5) au sein d'un SI.

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Python 3.11+ (pour les tests locaux)

### Lancer l'infrastructure (PostgreSQL, Redis, API, Worker, Collector)
```bash
docker-compose up --build
```
L'API sera disponible sur `http://localhost:8000/health`.

## 🧪 Tests & Simulation de données

### 1. Tests Unitaires & Intégration
Le projet suit une approche **TDD**. Pour valider que l'API retourne bien les bons flux consolidés :
```bash
cd backend
PYTHONPATH=. pytest tests/
```
*Note: Les tests d'intégration API (`tests/test_api_integration.py`) nécessitent une instance PostgreSQL accessible pour s'exécuter.*

### 2. Simulation de trafic (Nexus/F5)
Pour tester l'ingestion réelle avec de fausses données réalistes :
```bash
cd backend
# Lancer le script de génération
python scripts/generate_test_data.py
```
Le script injecte 100 flux dans Redis, traités par le `worker-flow` et consultables via l'API.

## ⚙️ Configuration des équipements (Ingestion)

### Cisco Nexus 9000 (NetFlow/IPFIX)
Configurez l'exportation des flux vers l'IP de votre serveur NetVis (UDP/9995).
*(Voir `README.md` complet pour les blocs de configuration Nexus/F5)*

## 🖥️ Guide d'utilisation de la GUI (V1)

### 1. Recherche et Filtrage (Explorateur)
- Utilisez la barre de recherche via le **NVQL**.
  - `src:10.1.1.1` : Voir tout ce qui sort de cette IP.
  - `port:443 and proto:tcp` : Voir le trafic HTTPS.
- Les résultats s'affichent sous forme de tableau consolidé avec **Total Count**, **Bytes** et **Packets**.

### 2. Cartographie (Graph View)
- Les liens entre les noeuds représentent les flux réels.
- Agrégations possibles par **Host**, **Subnet** ou **Zone**.

## 📂 Structure du Projet
- `PROPOSAL.md` : Architecture détaillée.
- `backend/workers/collector.py` : Collecteur UDP écoutant sur 9995.
- `backend/workers/flow_worker.py` : Moteur de consolidation (UPSERT).
- `backend/app/main.py` : API de recherche et stats.

## 🔍 NetVis Query Language (NVQL)
- `src:10.1.1.1 and port:443`
- `dst.zone:DMZ and not proto:UDP`
- `tag:PROD`
