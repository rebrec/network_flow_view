import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.core.config import settings
from app.models.flow import ConsolidatedFlow
from app.services.nvql_parser import parse_nvql

# Setup Database Engine pour FastAPI
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure schema is up to date (V1 schema update for bytes/packets)
    async with engine.begin() as conn:
        try:
            # Check if bytes column exists
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='consolidated_flows' AND column_name='bytes'"
            ))
            if not result.fetchone():
                await conn.execute(text("ALTER TABLE consolidated_flows ADD COLUMN bytes BIGINT DEFAULT 0"))
                await conn.execute(text("ALTER TABLE consolidated_flows ADD COLUMN packets BIGINT DEFAULT 0"))
        except Exception as e:
            print(f"Startup schema check error (ignoring if DB not ready): {e}")
    yield

app = FastAPI(
    title="NetVis API V1",
    description="Observabilité Réseau On-Prem",
    lifespan=lifespan
)

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
    stmt = select(ConsolidatedFlow).order_by(ConsolidatedFlow.total_count.desc()).limit(10)
    result = await db.execute(stmt)
    top_flows = result.scalars().all()

    return {
        "active_flows": len(top_flows),
        "top_talkers": top_flows
    }

@app.get("/api/v1/graphs/dependency")
async def get_dependency_graph(db: AsyncSession = Depends(get_db)):
    """
    Génère les données au format Cytoscape pour le graphe de dépendances.
    """
    stmt = select(ConsolidatedFlow).order_by(ConsolidatedFlow.last_seen.desc()).limit(200)
    result = await db.execute(stmt)
    flows = result.scalars().all()

    nodes = set()
    elements = []

    for flow in flows:
        # Ajout des noeuds source et destination
        if flow.ip_src not in nodes:
            elements.append({"data": {"id": flow.ip_src, "label": flow.ip_src}})
            nodes.add(flow.ip_src)

        if flow.ip_dst not in nodes:
            elements.append({"data": {"id": flow.ip_dst, "label": flow.ip_dst}})
            nodes.add(flow.ip_dst)

        # Ajout de l'arête (flux)
        elements.append({
            "data": {
                "id": f"{flow.ip_src}-{flow.ip_dst}-{flow.port_dst}",
                "source": flow.ip_src,
                "target": flow.ip_dst,
                "port": str(flow.port_dst)
            }
        })

    return elements

# Serve static files and SPA
static_path = os.path.join(os.path.dirname(__file__), "..", "static")

if os.path.exists(static_path):
    # Mount the entire static directory to serve assets and other files safely
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    # Explicitly serve index.html for common root/SPA paths
    @app.get("/")
    @app.get("/explorer")
    @app.get("/topology")
    async def serve_index():
        return FileResponse(os.path.join(static_path, "index.html"))

    # Optional: Catch-all for other non-API routes to support SPA routing
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)

        # Check if the file exists in static directory first
        potential_file = os.path.join(static_path, full_path)
        if os.path.isfile(potential_file):
             return FileResponse(potential_file)

        return FileResponse(os.path.join(static_path, "index.html"))
