from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.flow import ConsolidatedFlow
from app.services.nvql_parser import parse_nvql

app = FastAPI(title="NetVis API V1", description="Observabilité Réseau On-Prem")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/v1/flows/search")
async def search_flows(query: dict):
    """
    Recherche de flux consolidés avec filtrage NVQL.
    """
    query_string = query.get("query_string", "")
    filters = parse_nvql(query_string)

    # Simuler le retour de données pour la démo V1
    # Dans une version réelle, on construirait une requête SQLAlchemy complexe ici
    return {
        "total": 0,
        "filters_parsed": filters,
        "data": [],
        "message": "Recherche initialisée. Connectez une base de données avec des flux réels."
    }

@app.get("/api/v1/stats/summary")
def get_summary():
    return {
        "active_flows": 0,
        "observations_24h": 0,
        "top_zones": []
    }
