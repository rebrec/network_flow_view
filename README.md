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
5. **LTM (Optionnel) :** Utilisez un iRule pour envoyer les événements de connexion au publisher si AFM n'est pas utilisé.

## 🖥️ Guide d'utilisation de la GUI (V1)

### 1. Recherche et Filtrage (Explorateur)
- Utilisez la barre de recherche en haut pour filtrer les flux via le **NVQL**.
  - `src:10.1.1.1` : Voir tout ce qui sort de cette IP.
  - `port:443 and proto:tcp` : Voir le trafic HTTPS.
  - `dst.zone:DMZ` : Voir le trafic entrant en DMZ.
- Les résultats s'affichent sous forme de tableau consolidé (First Seen, Last Seen, Count).

### 2. Cartographie (Graph View)
- Cliquez sur l'onglet **"Graph"**.
- Sélectionnez le mode de regroupement : **Host**, **Subnet** ou **Zone**.
- Les liens entre les noeuds représentent les flux. L'épaisseur du trait est proportionnelle au nombre d'observations (`total_count`).
- Survoler un lien pour voir le détail des ports utilisés.

### 3. Gestion des Alias (Administration)
- Allez dans **"Settings" > "Aliases"**.
- Importez votre fichier CSV issu du F5 ou ajoutez manuellement des noms d'hôtes pour enrichir la vue (ex: `10.1.1.10` -> `DB_PROD_01`).

### 4. Exports
- Utilisez le bouton **"Export CSV"** sur n'importe quelle vue filtrée pour récupérer les données consolidées.

## 📂 Structure du Projet
- `PROPOSAL.md` : Document d'architecture détaillé (18 points).
- `architecture.mermaid` : Diagramme logique des flux de données.
- `init_db.sql` : Schéma PostgreSQL initial.
- `backend/` : FastAPI & Workers de consolidation.

## 🔍 NetVis Query Language (NVQL)
Exemples :
- `src:10.1.1.1 and port:443`
- `dst.zone:DMZ and not proto:UDP`
- `tag:PROD`
