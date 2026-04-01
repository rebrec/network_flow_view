# NetVis V1 - Observatoire de Flux Réseau On-Prem

NetVis est un outil d'observabilité réseau conçu pour offrir une vision consolidée des flux réels observés (Nexus, F5) au sein d'un SI.

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Python 3.11+ (pour les tests locaux)

### Lancer l'infrastructure (PostgreSQL, Redis, API, Worker)
```bash
docker-compose up --build
```
L'API sera disponible sur `http://localhost:8000/health`.

## 🧪 Tests

Le projet suit une approche **TDD**. Pour lancer les tests unitaires du backend :

1. Créer un environnement virtuel :
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Exécuter pytest :
   ```bash
   PYTHONPATH=. pytest tests/
   ```

## 📂 Structure du Projet

- `PROPOSAL.md` : Document d'architecture détaillé (18 points).
- `architecture.mermaid` : Diagramme logique des flux de données.
- `init_db.sql` : Schéma PostgreSQL initial (types `inet`, indexation GIST).
- `api_contracts.json` : Contrats d'API pour la recherche et les graphes.
- `backend/` : Code Python (FastAPI & Workers).
    - `app/services/flow_consolidator.py` : Logique d'UPSERT pour la consolidation.
    - `app/services/nvql_parser.py` : Parser de requêtes NetVis (NVQL).
    - `workers/flow_worker.py` : Worker asynchrone consommant Redis.

## 🔍 NetVis Query Language (NVQL)

Exemples de requêtes supportées par le parser V1 :
- `src:10.1.1.1 and port:443`
- `dst.zone:DMZ and not proto:UDP`
- `tag:PROD`

## 🛠️ Prochaines étapes (Roadmap V1)
1. Implémenter le collecteur IPFIX réel (Scapy/Pyshark).
2. Développer le Frontend React/Vue avec Cytoscape.js.
3. Intégrer l'import automatique des alias depuis F5.
