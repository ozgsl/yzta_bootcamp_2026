import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

@event.listens_for(Engine, "connect")
def set_sqlite_functions(dbapi_connection, connection_record):
    if hasattr(dbapi_connection, "create_function") and dbapi_connection.__class__.__module__.startswith("sqlite3"):
        dbapi_connection.create_function("gen_random_uuid", 0, lambda: str(uuid.uuid4()))

# Google Cloud Run (K_SERVICE) üzerinde çalışırken veya yerel testlerde SQLite yedeklemesi
is_cloud_run = "K_SERVICE" in os.environ or os.getenv("USE_SQLITE") == "true"

if is_cloud_run:
    SUPABASE_URL = "sqlite:///./dijital_gardrop_cloud.db"
    engine = create_engine(SUPABASE_URL, connect_args={"check_same_thread": False})
else:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "postgresql+psycopg://postgres:testpassword@localhost:5433/spot_test")
    if SUPABASE_URL.startswith("postgres://"):
        SUPABASE_URL = SUPABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif SUPABASE_URL.startswith("postgresql://"):
        SUPABASE_URL = SUPABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(SUPABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
