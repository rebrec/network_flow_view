from sqlalchemy.dialects.postgresql import insert
from app.models.flow import ConsolidatedFlow
from sqlalchemy.ext.asyncio import AsyncSession

async def consolidate_flow(session: AsyncSession, flow_data: dict):
    # Logique d'upsert pour la consolidation des flux réseaux
    # On utilise ON CONFLICT pour gérer la clé unique (src, dst, port, proto)
    stmt = insert(ConsolidatedFlow).values(
        ip_src=flow_data["ip_src"],
        ip_dst=flow_data["ip_dst"],
        port_dst=flow_data["port_dst"],
        protocol=flow_data["protocol"],
        first_seen=flow_data["timestamp"],
        last_seen=flow_data["timestamp"],
        total_count=1,
        bytes=flow_data.get("bytes", 0),
        packets=flow_data.get("packets", 0)
    )

    # On met à jour les dates et on somme les compteurs/volumes
    update_stmt = stmt.on_conflict_do_update(
        constraint='uq_flow_key',
        set_={
            "last_seen": flow_data["timestamp"],
            "total_count": ConsolidatedFlow.total_count + 1,
            "bytes": ConsolidatedFlow.bytes + flow_data.get("bytes", 0),
            "packets": ConsolidatedFlow.packets + flow_data.get("packets", 0)
        }
    )

    await session.execute(update_stmt)
