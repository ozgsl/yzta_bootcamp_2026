import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Yalnizca PostgreSQL (Supabase) baglantisi desteklenecek
# Onerilen format: postgresql://[user]:[password]@[host]:[port]/[db]
SUPABASE_URL = os.getenv("SUPABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres")
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
