import asyncio
import json
import logging
from aioredis import from_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.flow_consolidator import consolidate_flow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flow_worker")

async def flow_worker():
    """
    Worker principal consommant les flux bruts depuis Redis
    et effectuant la consolidation dans PostgreSQL.
    """
    logger.info("Démarrage du Flow Worker NetVis...")

    # Setup Database Engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Setup Redis Connection
    redis = from_url(settings.REDIS_URL, decode_responses=True)

    while True:
        try:
            # Récupération d'un flow depuis la queue Redis (BLPOP)
            _, raw_flow_json = await redis.blpop("netvis:raw_flows")
            flow_data = json.loads(raw_flow_json)

            async with async_session() as session:
                await consolidate_flow(session, flow_data)
                await session.commit()

            logger.debug(f"Flow consolidé: {flow_data['ip_src']} -> {flow_data['ip_dst']}")

        except Exception as e:
            logger.error(f"Erreur lors du traitement du flow : {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(flow_worker())
    except KeyboardInterrupt:
        logger.info("Arrêt du worker.")
