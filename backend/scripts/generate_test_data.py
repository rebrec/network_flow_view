import json
import random
import time
import uuid
from datetime import datetime, timezone
import redis

# Configuration Redis (utiliser l'IP du conteneur en prod, localhost en dev local)
REDIS_URL = "redis://localhost:6379/0"

# Liste d'équipements fictifs pour varier les flux
IPS_PROD = [f"10.1.1.{i}" for i in range(10, 20)]
IPS_WEB = [f"172.16.50.{i}" for i in range(100, 110)]
IPS_INTERNET = ["8.8.8.8", "1.1.1.1", "20.30.40.50", "93.184.216.34"]
DMZ_SERVERS = ["192.168.10.1", "192.168.10.2"]

PROTOCOLS = ["TCP", "UDP"]
COMMON_PORTS = [443, 80, 22, 53, 3306, 5432, 161]

def generate_nexus_flow():
    """Génère un flux simulant un record NetFlow/IPFIX provenant d'un Nexus 9000."""
    src = random.choice(IPS_PROD + IPS_WEB)
    dst = random.choice(IPS_WEB + IPS_INTERNET + DMZ_SERVERS)
    port = random.choice(COMMON_PORTS)
    proto = random.choice(PROTOCOLS)

    return {
        "collector_id": "nexus-dc-01",
        "ip_src": src,
        "ip_dst": dst,
        "port_dst": port,
        "protocol": proto,
        "bytes": random.randint(500, 50000),
        "packets": random.randint(10, 100),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def simulate_ingestion(count=50):
    """Pousse 'count' flux dans la queue Redis 'netvis:raw_flows'."""
    try:
        r = redis.from_url(REDIS_URL)
        print(f"--- Simulation d'ingestion de {count} flux ---")

        for i in range(count):
            flow = generate_nexus_flow()
            r.rpush("netvis:raw_flows", json.dumps(flow))
            if (i+1) % 10 == 0:
                print(f"Injecté {i+1}/{count} flux...")
            time.sleep(0.1) # Simuler un petit délai

        print("Simulation terminée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la simulation : {e}")

if __name__ == "__main__":
    simulate_ingestion(100)
