# Proposition Technique V1 : Observatoire de Flux Réseau On-Prem (NetVis)

## 1. Reformulation du besoin
L'objectif est de concevoir un outil d'observabilité réseau open source, 100% on-premise, permettant aux administrateurs firewall et équipes de production de visualiser les interactions réelles entre équipements (VLANs, Zones, Internet, DMZ). L'outil doit consolider les flux observés (IP source, IP destination, Port destination, Protocole) pour offrir une vision historique (première/dernière vue) et graphique (dépendances applicatives) sans la complexité d'un SIEM ou d'un ELK, en s'appuyant sur PostgreSQL.

## 2. Hypothèses et limites
*   **Périmètre :** IPv4 uniquement.
*   **Sources :** Cisco Nexus 9000 (NetFlow/IPFIX) et F5 AFM/LTM (HSL/IPFIX).
*   **Rétention :** 24 heures pour les données brutes (`raw_observations`), illimitée (ou longue durée) pour les flux consolidés (`consolidated_flows`).
*   **Hors-périmètre V1 :** IPv6, analyse de règles firewall, détection d'anomalies, Multi-tenancy, Haute Disponibilité (HA).
*   **Performance :** Optimisé pour une instance unique (8 vCPU / 32 Go RAM).

## 3. Architecture globale
L'architecture repose sur une stack Python/FastAPI avec une base de données PostgreSQL et un tampon Redis pour absorber les pics d'ingestion.

*   **Ingestion (Collectors) :** Workers Python légers recevant les flux NetFlow/IPFIX et les poussant dans une file Redis.
*   **Normalisation & Consolidation (Workers) :** Processus asynchrones consommant Redis pour :
    *   Parser les paquets.
    *   Enrichir avec les zones/subnets définis.
    *   Effectuer un `UPSERT` dans PostgreSQL pour la consolidation.
*   **Stockage (PostgreSQL) :** Coeur du système pour les flux, les alias et la configuration.
*   **API (FastAPI) :** Fournit les endpoints pour le frontend et les exports.
*   **Frontend (React/Vue) :** Interface SPA pour la recherche, les tableaux et les graphes Cytoscape.js.
*   **DNS Worker :** Tâche de fond résolvant les IP inconnues de manière asynchrone.

## 4. Flux de données de bout en bout
1.  **Émission :** Le Nexus ou F5 envoie un flow IPFIX vers le Collector NetVis (UDP/9995).
2.  **Tampon :** Le Collector écrit le JSON brut du flow dans Redis (List ou Stream).
3.  **Traitement :** Un Worker récupère le flow, identifie les zones (ex: `10.1.0.0/24` -> `ZONE_PROD`) et le subnet.
4.  **Consolidation :** Le Worker exécute un `INSERT ... ON CONFLICT` sur la table `consolidated_flows` en mettant à jour `last_seen` et `observation_count`.
5.  **Enrichissement :** Si l'IP n'a pas de nom DNS, elle est ajoutée à la file `dns_pending`.
6.  **Visualisation :** L'utilisateur lance une recherche via l'API, qui agrège les flux consolidés pour générer le JSON compatible Cytoscape.js.

## 5. Modèle de données PostgreSQL
*   **`raw_observations`** : `id, timestamp, ip_src, ip_dst, port_dst, protocol, bytes, packets, collector_id`.
*   **`consolidated_flows`** : `id, ip_src, ip_dst, port_dst, protocol, first_seen, last_seen, total_count, bytes_sum, packets_sum, src_zone_id, dst_zone_id`.
*   **`hostname_aliases`** : `ip, hostname, source (firewall/manual/dns), last_update`.
*   **`network_topology`** : `id, cidr, name, type (zone/subnet/site), parent_id`.
*   **`saved_queries`** : `id, name, query_json, user_id`.
*   **`exclusion_rules`** : `id, pattern (ip/port/proto), reason`.

## 6. Stratégie de consolidation
La clé d'unicité métier est le tuple : `(ip_src, ip_dst, port_dst, protocol)`.
```sql
INSERT INTO consolidated_flows (ip_src, ip_dst, port_dst, protocol, first_seen, last_seen, total_count)
VALUES (%s, %s, %s, %s, %s, %s, 1)
ON CONFLICT (ip_src, ip_dst, port_dst, protocol)
DO UPDATE SET
    last_seen = EXCLUDED.last_seen,
    total_count = consolidated_flows.total_count + 1;
```
*Note : Pour la V1, on pourra agréger par fenêtres de 5 minutes dans le worker avant l'UPSERT pour réduire la charge DB.*

## 7. Stratégie d'indexation
*   **B-Tree** sur `(ip_src)`, `(ip_dst)`, `(port_dst)`.
*   **GIST/GIN** pour la recherche par CIDR (via type `inet` de Postgres).
*   **Index composite** sur `(last_seen DESC)` pour les tris de fraîcheur.
*   **Vue matérialisée** `mv_zone_traffic` pour les cartographies zone-à-zone, rafraîchie toutes les heures.

## 8. API backend
*   `GET /api/v1/flows/search` : Recherche avec filtres (JSON body).
*   `GET /api/v1/flows/export/csv` : Stream CSV des résultats filtrés.
*   `GET /api/v1/graphs/dependency` : Retourne `{ nodes: [], edges: [] }` pour Cytoscape.
*   `POST /api/v1/admin/aliases/import` : Upload de l'export F5 host list.
*   `GET /api/v1/stats/top-talkers` : Statistiques rapides par zone/IP.

## 9. Langage de requête V1 (NetVis Query Language - NVQL)
Un langage simple de type clé-valeur :
*   `src:10.1.1.1 and port:443`
*   `dst.zone:DMZ and proto:tcp`
*   `host ~ "db-prod"` (recherche floue sur alias)
*   `exclude port:137,138,139`
*   **Traduction :** Le backend parse cette string vers un objet de filtres SQLAlchemy/SQL.

## 10. UX / écrans V1
*   **Dashboard :** KPIs (nombre de flux actifs, volume 24h, alertes sur flux inconnus).
*   **Explorateur :** Table dynamique avec filtres "à la Wireshark" en haut de colonne.
*   **Graph View :** Vue interactive permettant de grouper par Hôte, Subnet ou Zone. Clic sur un lien = détails des ports.
*   **Manager d'Objets :** Gestion des zones (import CIDR) et des alias (import F5).

## 11. Visualisation graphique
*   Utilisation de **Cytoscape.js** avec le layout `cola` ou `dagre`.
*   **Agrégation :** L'utilisateur choisit le niveau d'abstraction. En mode "Zone", toutes les IPs d'une zone sont fusionnées en un seul noeud.
*   **Filtrage :** Limiter l'affichage aux flux ayant eu une activité dans les dernières X heures pour éviter les "chevelus" (hairballs).

## 12. Collecte et connecteurs
*   **Nexus :** Configuration NetFlow Export v9 pointant vers l'IP de la VM.
*   **F5 :** Utilisation du Log Publisher vers un pool de nodes (nos collectors) en format IPFIX.
*   **Alternative V1 :** Un script Python "Syslog-to-Redis" pour les logs F5 si l'IPFIX est trop complexe à configurer initialement.

## 13. Ordonnancement et traitements asynchrones
Utilisation de **Celery** avec Redis :
*   `task_consolidate` : Exécutée en continu (consomme Redis).
*   `task_dns_resolve` : Toutes les 5 minutes sur les IPs sans hostname.
*   `task_cleanup` : Toutes les heures (efface `raw_observations` > 24h).
*   `task_refresh_mv` : Rafraîchissement des vues matérialisées.

## 14. Stack technique détaillée
*   **Backend :** Python 3.11, FastAPI, SQLAlchemy 2.0 (Async).
*   **Database :** PostgreSQL 15 + TimescaleDB (optionnel, mais recommandé pour la rétention).
*   **Cache/Queue :** Redis 7.
*   **Frontend :** Vite.js + Vue 3 (Composition API) + TailwindCSS.
*   **Graphes :** Cytoscape.js.
*   **Packaging :** Docker Compose (containers: `api`, `worker-flow`, `worker-dns`, `db`, `redis`, `frontend`).

## 15. Arborescence projet
```text
netvis/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints
│   │   ├── core/         # Config, DB connection
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic models
│   │   └── services/     # Business logic (Consolidation, Query parser)
│   ├── workers/          # Celery tasks / Flow collectors
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/   # Graph, Table, Filters
│   │   ├── views/
│   │   └── store/
├── data/                 # GeoIP, local DB backups
└── deploy/               # Dockerfile, docker-compose.yml, nginx.conf
```

## 16. Plan d'implémentation
*   **Lot 0 :** Setup Docker, DB Schema et ingestion brute NetFlow -> Redis.
*   **Lot 1 :** Logique de consolidation (Upsert) et API de recherche simple.
*   **Lot 2 :** Frontend (Tableau des flux) et système d'alias (Import F5/DNS).
*   **Lot 3 :** Visualisation graphique Cytoscape et filtres avancés (NVQL).
*   **Lot 4 :** Exports CSV et finalisation de l'UX (Saved queries).

## 17. Risques et arbitrages
*   **Volume SQL :** L'indexation massive peut ralentir les inserts. Arbitrage : consolidation en mémoire (batch de 5s) avant l'insert.
*   **Bruit réseau :** Des millions de flux NetBIOS/DNS. Solution : Liste d'exclusion par défaut "bruit blanc" pré-configurée.
*   **Complexité Graphe :** Trop de noeuds = illisible. Solution : Forcer l'agrégation par subnet au-delà de 50 noeuds.

## 18. V2 (Évolutions)
*   Interrogation API F5 pour corrélation temps réel avec les VIPs.
*   Détection de flux "orphelins" (flux observés mais sans règle firewall correspondante).
*   Support IPv6.
*   Alerting sur apparition de nouveaux flux entre zones sensibles.
