import os
import tempfile

# Define JWT_SECRET_KEY antes de qualquer import do app
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
_original_cwd = os.getcwd()
_test_cwd = tempfile.TemporaryDirectory()
os.chdir(_test_cwd.name)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, engine as app_engine, get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.services import thingspeak_client
from app.routers import clima as clima_router
from main import app

# Desliga rate limiter para testes
limiter.enabled = False

# SQLite em memória com StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    app_engine.dispose()
    os.chdir(_original_cwd)
    _test_cwd.cleanup()


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_thingspeak(monkeypatch):
    """Garante que thingspeak_client nunca acesse a internet por padrão."""
    default_leitura = {
        "entry_id": 1001,
        "temperatura": 25.0,
        "umidade": 60.0,
        "umidade_solo": 40.0,
        "registrado_em": "2026-10-18T12:00:00Z",
    }
    monkeypatch.setattr(
        thingspeak_client, "get_ultima_leitura", lambda: default_leitura
    )
    monkeypatch.setattr(
        thingspeak_client,
        "get_historico",
        lambda resultados=100: [default_leitura],
    )
    clima_router._ultimo_sync = 0.0


@pytest.fixture
def token_produtor():
    return create_access_token(
        subject="produtor@vinicola.com", role="produtor_exportador"
    )


@pytest.fixture
def token_analista():
    return create_access_token(
        subject="analista@vinicola.com", role="analista_dados"
    )


@pytest.fixture
def token_admin():
    return create_access_token(
        subject="admin@vinicola.com", role="administrador"
    )
