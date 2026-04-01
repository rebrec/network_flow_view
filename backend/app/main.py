from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.flow import ConsolidatedFlow
from app.services.nvql_parser import parse_nvql

# Setup Database Engine pour FastAPI
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI(title="NetVis API V1", description="Observabilité Réseau On-Prem")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/v1/flows/search")
async def search_flows(query_req: dict, db: AsyncSession = Depends(get_db)):
    """
    Recherche de flux consolidés avec filtrage NVQL.
    V1 : Filtrage basique sur IP source/destination et port.
    """
    query_string = query_req.get("query_string", "")
    filters = parse_nvql(query_string)

    stmt = select(ConsolidatedFlow)

    # Application des filtres NVQL si présents
    if "ip_src" in filters:
        stmt = stmt.where(ConsolidatedFlow.ip_src == filters["ip_src"])
    if "ip_dst" in filters:
        stmt = stmt.where(ConsolidatedFlow.ip_dst == filters["ip_dst"])
    if "port_dst" in filters:
        stmt = stmt.where(ConsolidatedFlow.port_dst == filters["port_dst"])
    if "protocol" in filters:
        stmt = stmt.where(ConsolidatedFlow.protocol == filters["protocol"])

    # Exclusions (Simple 'not')
    if "exclude_protocol" in filters:
        stmt = stmt.where(ConsolidatedFlow.protocol != filters["exclude_protocol"])

    # Tri par défaut par dernière observation
    stmt = stmt.order_by(ConsolidatedFlow.last_seen.desc()).limit(100)

    result = await db.execute(stmt)
    flows = result.scalars().all()

    return {
        "total": len(flows),
        "filters_parsed": filters,
        "data": flows
    }

@app.get("/api/v1/stats/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    # Simuler des stats pour la V1 (top talkers)
    stmt = select(ConsolidatedFlow).order_by(ConsolidatedFlow.total_count.desc()).limit(5)
    result = await db.execute(stmt)
    top_flows = result.scalars().all()

    return {
        "active_flows": len(top_flows),
        "top_talkers": top_flows
    }
