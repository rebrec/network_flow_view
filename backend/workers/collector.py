import asyncio
import json
import logging
from redis.asyncio import from_url
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("collector_udp")

class NetFlowCollectorProtocol(asyncio.DatagramProtocol):
    def __init__(self, redis_client):
        self.redis = redis_client

    def connection_made(self, transport):
        self.transport = transport
        logger.info("Collector UDP écoutant sur le port 9995...")

    def datagram_received(self, data, addr):
        """
        Réception brute d'un paquet UDP (NetFlow/IPFIX).
        V1 Boilerplate : Simulation de parsing pour démontrer l'architecture.
        """
        logger.debug(f"Paquet reçu de {addr} (taille: {len(data)})")

        # NOTE : Pour une V1 réelle, on utiliserait ici une lib de parsing
        # type 'scapy' ou un parser binaire NetFlow v9/IPFIX.
        # Ici on simule un flow valide pour démontrer l'ingestion vers Redis.

        try:
            # Simulation d'un flow parsé à partir de la donnée brute
            simulated_flow = {
                "collector_id": f"nexus-{addr[0]}",
                "ip_src": "192.168.1.10", # En prod, issu du parsing binaire
                "ip_dst": "10.0.0.5",
                "port_dst": 443,
                "protocol": "TCP",
                "bytes": len(data) * 10,
                "packets": 1,
                "timestamp": "2023-10-27T10:00:00Z" # En prod, timestamp réel
            }

            asyncio.create_task(self.redis.rpush("netvis:raw_flows", json.dumps(simulated_flow)))

        except Exception as e:
            logger.error(f"Erreur lors de l'ingestion Redis : {e}")

async def start_collector():
    redis = from_url(settings.REDIS_URL, decode_responses=True)
    loop = asyncio.get_running_loop()

    # Écoute UDP sur 0.0.0.0:9995
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: NetFlowCollectorProtocol(redis),
        local_addr=('0.0.0.0', 9995)
    )

    try:
        while True:
            await asyncio.sleep(3600)  # Maintenir en vie
    finally:
        transport.close()

if __name__ == "__main__":
    try:
        asyncio.run(start_collector())
    except KeyboardInterrupt:
        logger.info("Arrêt du collector.")
