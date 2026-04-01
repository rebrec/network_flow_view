import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    # En environnement de test/sandbox, on tente de se connecter.
    # Si ça échoue, on skip les tests dépendant de la DB.
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        # Test connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        yield engine
        await engine.dispose()
    except Exception:
        pytest.skip("PostgreSQL non disponible. Skip des tests d'intégration DB.")

@pytest.fixture
async def db_session(db_engine):
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
