-- Initial Database Schema for NetVis V1

-- Extension pour le support CIDR avancé et performance (optionnelle)
-- CREATE EXTENSION IF NOT EXISTS btree_gist;

-- 1. Réseau et Topologie
CREATE TABLE IF NOT EXISTS network_topology (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cidr INET NOT NULL, -- Format standard 10.1.0.0/24
    type VARCHAR(50) CHECK (type IN ('zone', 'subnet', 'site')),
    parent_id INTEGER REFERENCES network_topology(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_cidr_type UNIQUE (cidr, type)
);

-- 2. Hôtes et Résolution de noms
CREATE TABLE IF NOT EXISTS hostname_aliases (
    ip INET PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    source VARCHAR(50) DEFAULT 'dns' CHECK (source IN ('dns', 'firewall', 'manual')),
    last_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tag VARCHAR(100) -- Pour l'association applicative simple
);

-- 3. Observations Brutes (Rétention 24h)
CREATE TABLE IF NOT EXISTS raw_observations (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_src INET NOT NULL,
    ip_dst INET NOT NULL,
    port_dst INTEGER NOT NULL,
    protocol VARCHAR(10) NOT NULL,
    bytes BIGINT DEFAULT 0,
    packets BIGINT DEFAULT 0,
    collector_id VARCHAR(50)
);

-- 4. Flux Consolidés (Le coeur de la V1)
CREATE TABLE IF NOT EXISTS consolidated_flows (
    id BIGSERIAL PRIMARY KEY,
    ip_src INET NOT NULL,
    ip_dst INET NOT NULL,
    port_dst INTEGER NOT NULL,
    protocol VARCHAR(10) NOT NULL,

    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    total_count BIGINT DEFAULT 1,

    -- Cache de zone pour accélerer les requêtes (calculé lors de l'insertion)
    src_zone_id INTEGER REFERENCES network_topology(id),
    dst_zone_id INTEGER REFERENCES network_topology(id),

    CONSTRAINT uq_flow_key UNIQUE (ip_src, ip_dst, port_dst, protocol)
);

-- 5. Requêtes et Configuration
CREATE TABLE IF NOT EXISTS saved_queries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    query_string TEXT NOT NULL, -- NVQL String
    query_json JSONB, -- Version parsée
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exclusion_rules (
    id SERIAL PRIMARY KEY,
    pattern VARCHAR(255) NOT NULL, -- ex: "port:137", "ip:10.0.0.0/8"
    reason TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 6. Indexation pour Performance
CREATE INDEX idx_raw_timestamp ON raw_observations (timestamp DESC);
CREATE INDEX idx_flow_ip_src ON consolidated_flows USING GIST (ip_src inet_ops);
CREATE INDEX idx_flow_ip_dst ON consolidated_flows USING GIST (ip_dst inet_ops);
CREATE INDEX idx_flow_port_dst ON consolidated_flows (port_dst);
CREATE INDEX idx_flow_last_seen ON consolidated_flows (last_seen DESC);

-- 7. Vue Matérialisée pour les stats globales (Top 100 Flows)
CREATE MATERIALIZED VIEW mv_top_flows AS
SELECT * FROM consolidated_flows
ORDER BY total_count DESC
LIMIT 100;

CREATE INDEX idx_mv_top_flows_count ON mv_top_flows (total_count DESC);
