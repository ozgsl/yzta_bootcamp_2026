"""Wardrobe (dolap) tablolarını veritabanına ekler."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "dijital_gardrop.db"

WARDROBE_SQL = """
CREATE TABLE IF NOT EXISTS kategoriler (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    tip   TEXT NOT NULL,
    deger TEXT NOT NULL,
    UNIQUE(tip, deger)
);

CREATE TABLE IF NOT EXISTS kiyafetler (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           TEXT NOT NULL,
    tur               TEXT NOT NULL,
    renk              TEXT NOT NULL DEFAULT 'bilinmiyor',
    marka             TEXT,
    beden             TEXT,
    kumas             TEXT,
    kesim             TEXT,
    yaka_tipi         TEXT,
    kol_tipi          TEXT,
    desen             TEXT DEFAULT 'duz',
    mevsim            TEXT DEFAULT 'tum sezon',
    stil_etiketi      TEXT,
    kullanim_sikligi  TEXT,
    kombin_notu       TEXT,
    temiz             INTEGER NOT NULL DEFAULT 1,
    foto_url          TEXT,
    guncelleme_tarihi TEXT
);

CREATE TABLE IF NOT EXISTS sohbetler (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL,
    rol        TEXT NOT NULL,
    mesaj      TEXT NOT NULL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS kombin_oneriler (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 TEXT NOT NULL,
    baglam_json             TEXT NOT NULL,
    onerilen_kiyafet_idleri TEXT NOT NULL,
    aciklama                TEXT NOT NULL,
    begenildi               INTEGER,
    created_at              TEXT
);
"""

conn = sqlite3.connect(str(DB_PATH))
conn.executescript(WARDROBE_SQL)
conn.commit()
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("✅ Tüm tablolar:", [t[0] for t in tables])
conn.close()
