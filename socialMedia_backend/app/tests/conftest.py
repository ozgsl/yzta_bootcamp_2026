import os
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic import command

# 1. Guard against using Production URL in tests
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    TEST_DATABASE_URL = "postgresql://postgres:testpassword@localhost:5433/spot_test"

if "supabase" in TEST_DATABASE_URL.lower() or "production" in TEST_DATABASE_URL.lower():
    raise ValueError("CRITICAL ERROR: Tests must not be run against a production or Supabase database!")

# Use synchronous connection for testing
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_database():
    """
    Session-level fixture to run Alembic migrations before the test suite starts.
    """
    # Proje kök dizinini bul
    root_dir = Path(__file__).resolve().parent.parent.parent
    alembic_ini_path = root_dir / "alembic.ini"
    alembic_dir = root_dir / "alembic"
    
    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"alembic.ini not found at {alembic_ini_path}")
        
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(alembic_dir))
    
    # Overwrite the sqlalchemy.url in alembic.ini with the test database URL
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")
    
    yield engine
    
    # Teardown: Optionally downgrade or drop tables if desired, but not strictly necessary 
    # since each test is rolled back and database is dedicated for tests.

@pytest.fixture(scope="function")
def db(setup_database):
    """
    Function-level fixture that runs each test in a transaction,
    then rolls back at the end of the test.
    """
    connection = engine.connect()
    # Begin a nested transaction (using SAVEPOINT).
    transaction = connection.begin()
    
    # Bind the session to the connection so it uses the same transaction
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Rollback the transaction after the test is complete
    session.close()
    transaction.rollback()
    connection.close()

# Include common fixtures directly if needed, or they can be imported
 
pytest_plugins = ["app.tests.fixtures.users", "app.tests.fixtures.posts"] 

