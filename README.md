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

## 🧪 Tests & Simulation de données

Le projet suit une approche **TDD**.

### 1. Tests Unitaires
Pour lancer les tests unitaires du backend :
```bash
cd backend
PYTHONPATH=. pytest tests/
```

### 2. Simulation de trafic (Nexus/F5)
Pour tester l'ingestion et la consolidation avec de fausses données réalistes :
```bash
cd backend
# Installer redis-py si besoin
pip install redis
# Lancer le script de génération
python scripts/generate_test_data.py
```
Le script injectera 100 flux dans Redis, qui seront immédiatement traités par le `worker-flow` et consolidés dans la base de données.

## ⚙️ Configuration des équipements (Ingestion)

### Cisco Nexus 9000 (NetFlow/IPFIX)
Configurez l'exportation des flux vers l'IP de votre serveur NetVis (UDP/9995) :
```text
feature netflow

flow exporter NETVIS_EXPORTER
  destination <IP_SERVEUR_NETVIS>
  transport udp 9995
  source <INTERFACE_SOURCE>
  version 9

flow record NETVIS_RECORD
  match ipv4 source address
  match ipv4 destination address
  match transport destination-port
  match ipv4 protocol
  collect counter bytes
  collect counter packets
  collect timestamp sys-uptime first
  collect timestamp sys-uptime last

flow monitor NETVIS_MONITOR
  record NETVIS_RECORD
  exporter NETVIS_EXPORTER

interface <VLAN_OU_INTERFACE_A_SURVEILLER>
  ip flow monitor NETVIS_MONITOR input
```

### F5 AFM/LTM (HSL / IPFIX)
1. **Pool :** Créez un pool contenant l'IP du serveur NetVis sur le port UDP 9995.
2. **Log Destination :** Créez une destination de type `IPFIX` pointant vers ce pool.
3. **Log Publisher :** Créez un publisher incluant cette destination.
4. **AFM Policy :** Dans votre Network Firewall Policy, activez le logging et sélectionnez ce publisher.

## 🖥️ Guide d'utilisation de la GUI (V1)

### 1. Recherche et Filtrage (Explorateur)
- Utilisez la barre de recherche en haut pour filtrer les flux via le **NVQL**.
  - `src:10.1.1.1` : Voir tout ce qui sort de cette IP.
  - `port:443 and proto:tcp` : Voir le trafic HTTPS.
- Les résultats s'affichent sous forme de tableau consolidé (First Seen, Last Seen, Count).

### 2. Cartographie (Graph View)
- Cliquez sur l'onglet **"Graph"**.
- Sélectionnez le mode de regroupement : **Host**, **Subnet** ou **Zone**.
- Les liens entre les noeuds représentent les flux. L'épaisseur du trait est proportionnelle au nombre d'observations (`total_count`).

### 3. Gestion des Alias (Administration)
- Allez dans **"Settings" > "Aliases"**.
- Importez votre fichier CSV issu du F5 ou ajoutez manuellement des noms d'hôtes pour enrichir la vue (ex: `10.1.1.10` -> `DB_PROD_01`).

## 📂 Structure du Projet
- `PROPOSAL.md` : Architecture détaillée.
- `init_db.sql` : Schéma PostgreSQL.
- `backend/scripts/generate_test_data.py` : Script de génération de données de test.
- `backend/workers/flow_worker.py` : Moteur de consolidation asynchrone.

## 🔍 NetVis Query Language (NVQL)
- `src:10.1.1.1 and port:443`
- `dst.zone:DMZ and not proto:UDP`
- `tag:PROD`
