-- Initial Database Schema for NetVis V1

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

    -- Métriques sommables (doivent matcher le modèle SQLAlchemy)
    bytes BIGINT DEFAULT 0,
    packets BIGINT DEFAULT 0,

    -- Cache de zone pour accélerer les requêtes
    src_zone_id INTEGER REFERENCES network_topology(id),
    dst_zone_id INTEGER REFERENCES network_topology(id),

    CONSTRAINT uq_flow_key UNIQUE (ip_src, ip_dst, port_dst, protocol)
);

-- 5. Requêtes et Configuration
CREATE TABLE IF NOT EXISTS saved_queries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    query_string TEXT NOT NULL,
    query_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Indexation pour Performance
CREATE INDEX idx_raw_timestamp ON raw_observations (timestamp DESC);
CREATE INDEX idx_flow_ip_src ON consolidated_flows USING GIST (ip_src inet_ops);
CREATE INDEX idx_flow_ip_dst ON consolidated_flows USING GIST (ip_dst inet_ops);
CREATE INDEX idx_flow_port_dst ON consolidated_flows (port_dst);
CREATE INDEX idx_flow_last_seen ON consolidated_flows (last_seen DESC);
