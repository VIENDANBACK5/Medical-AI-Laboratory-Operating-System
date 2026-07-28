import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import ARRAY

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(element, compiler, **kw):
    return "JSON"

# Force SQLite for database calls during tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_DB"] = "test"
os.environ["SECRET_KEY"] = "test_secret_key"

# Make sure config reads the overridden values
from app.core.config import settings
settings.DATABASE_URL = "sqlite:///./test.db"

from app.models.model_base import Base
from fastapi.testclient import TestClient


# Setup testing engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create the sqlite database and all tables (including User and Volume)
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up and drop the sqlite database after tests complete
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except PermissionError:
            pass


@pytest.fixture(scope="function", autouse=True)
def transaction_cleanup():
    """Ensures each test run is clean by rolling back database writes."""
    connection = engine.connect()
    transaction = connection.begin()
    
    yield
    
    transaction.rollback()
    connection.close()


def _fake_current_user():
    """Stand-in authenticated user injected in place of real JWT auth in tests."""
    from app.models import User
    return User(
        id=1,
        username="tester",
        email="tester@example.com",
        roles=["USER"],
        is_active=True,
    )


@pytest.fixture(scope="module")
def client():
    from app.main import app
    from app.utils.login_manager import login_required

    # Bypass Bearer authentication for API tests by overriding the shared
    # login dependency with a fixed fake user.
    app.dependency_overrides[login_required] = _fake_current_user
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(login_required, None)
