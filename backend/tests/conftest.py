import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        yield engine
        await engine.dispose()
    except Exception:
        pytest.skip("PostgreSQL non disponible pour les tests d'intégration.")

@pytest.fixture
async def db_session(db_engine):
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        # Override de la dépendance get_db pour FastAPI
        # On injecte la session de test directement
        async def override_get_db():
            yield session
        app.dependency_overrides[app.get_db] = override_get_db

        yield session
        await session.rollback()
        # Clean overrides après chaque test
        app.dependency_overrides.clear()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
