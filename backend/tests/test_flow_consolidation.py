from datetime import datetime, timezone
import pytest
from app.services.flow_consolidator import consolidate_flow
from app.models.flow import ConsolidatedFlow
from sqlalchemy import select

@pytest.mark.asyncio
async def test_consolidate_new_flow(db_session):
    # GIVEN: A raw flow observation
    flow_data = {
        "ip_src": "192.168.1.10",
        "ip_dst": "10.0.0.5",
        "port_dst": 443,
        "protocol": "TCP",
        "timestamp": datetime.now(timezone.utc),
        "bytes": 1000,
        "packets": 10
    }

    # WHEN: We consolidate it for the first time
    await consolidate_flow(db_session, flow_data)
    await db_session.commit()

    # THEN: A new entry is created in consolidated_flows
    stmt = select(ConsolidatedFlow).where(
        ConsolidatedFlow.ip_src == "192.168.1.10",
        ConsolidatedFlow.ip_dst == "10.0.0.5",
        ConsolidatedFlow.port_dst == 443
    )
    result = await db_session.execute(stmt)
    flow = result.scalar_one()

    assert flow.total_count == 1
    assert flow.ip_src == "192.168.1.10"
    assert flow.protocol == "TCP"

@pytest.mark.asyncio
async def test_consolidate_existing_flow_updates_counters(db_session):
    # GIVEN: An existing flow in the DB
    flow_data = {
        "ip_src": "192.168.1.10",
        "ip_dst": "10.0.0.5",
        "port_dst": 443,
        "protocol": "TCP",
        "timestamp": datetime(2023, 10, 27, 10, 0, 0, tzinfo=timezone.utc),
        "bytes": 1000,
        "packets": 10
    }
    await consolidate_flow(db_session, flow_data)
    await db_session.commit()

    # WHEN: Another observation for the same flow arrives later
    later_flow_data = flow_data.copy()
    later_flow_data["timestamp"] = datetime(2023, 10, 27, 11, 0, 0, tzinfo=timezone.utc)
    later_flow_data["bytes"] = 500

    await consolidate_flow(db_session, later_flow_data)
    await db_session.commit()

    # THEN: The existing entry is updated
    stmt = select(ConsolidatedFlow).where(ConsolidatedFlow.ip_src == "192.168.1.10")
    result = await db_session.execute(stmt)
    flow = result.scalar_one()

    assert flow.total_count == 2
    assert flow.last_seen == later_flow_data["timestamp"]
    assert flow.first_seen == flow_data["timestamp"]
