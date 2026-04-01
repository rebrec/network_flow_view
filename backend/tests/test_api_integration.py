import pytest
from httpx import AsyncClient
from datetime import datetime, timezone
from app.main import app
from app.models.flow import ConsolidatedFlow

@pytest.mark.asyncio
async def test_search_api_returns_filtered_flows(db_session):
    # GIVEN: Some flows in the database
    f1 = ConsolidatedFlow(
        ip_src="10.1.1.1", ip_dst="8.8.8.8", port_dst=53, protocol="UDP",
        first_seen=datetime.now(timezone.utc), last_seen=datetime.now(timezone.utc),
        total_count=10, bytes=5000, packets=50
    )
    f2 = ConsolidatedFlow(
        ip_src="10.2.2.2", ip_dst="1.1.1.1", port_dst=443, protocol="TCP",
        first_seen=datetime.now(timezone.utc), last_seen=datetime.now(timezone.utc),
        total_count=5, bytes=10000, packets=100
    )
    db_session.add_all([f1, f2])
    await db_session.commit()

    # WHEN: We search for the first flow via API using NVQL
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"query_string": "src:10.1.1.1 and proto:UDP"}
        response = await ac.post("/api/v1/flows/search", json=payload)

    # THEN: The API returns the correct flow with the right metrics
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    flow = data["data"][0]
    assert flow["ip_src"] == "10.1.1.1"
    assert flow["port_dst"] == 53
    assert flow["total_count"] == 10
    assert flow["bytes"] == 5000

@pytest.mark.asyncio
async def test_search_api_exclusion(db_session):
    # GIVEN: Multiple flows
    f1 = ConsolidatedFlow(
        ip_src="10.1.1.1", ip_dst="8.8.8.8", port_dst=443, protocol="TCP",
        first_seen=datetime.now(timezone.utc), last_seen=datetime.now(timezone.utc)
    )
    f2 = ConsolidatedFlow(
        ip_src="10.1.1.1", ip_dst="8.8.8.8", port_dst=53, protocol="UDP",
        first_seen=datetime.now(timezone.utc), last_seen=datetime.now(timezone.utc)
    )
    db_session.add_all([f1, f2])
    await db_session.commit()

    # WHEN: We search for source 10.1.1.1 EXCLUDING UDP
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"query_string": "src:10.1.1.1 and not proto:UDP"}
        response = await ac.post("/api/v1/flows/search", json=payload)

    # THEN: Only the TCP flow is returned
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["protocol"] == "TCP"
