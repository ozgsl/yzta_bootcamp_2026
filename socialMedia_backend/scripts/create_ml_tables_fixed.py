import sqlite3
conn = sqlite3.connect('dijital_gardrop.db')
sql = '''
CREATE TABLE IF NOT EXISTS kategoriler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tip TEXT NOT NULL,
    deger TEXT NOT NULL,
    UNIQUE(tip, deger)
);
CREATE TABLE IF NOT EXISTS kiyafetler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    tur TEXT NOT NULL,
    renk TEXT,
    marka TEXT,
    beden TEXT,
    kumas TEXT,
    kesim TEXT,
    yaka_tipi TEXT,
    kol_tipi TEXT,
    desen TEXT,
    mevsim TEXT,
    stil_etiketi TEXT,
    kullanim_sikligi TEXT,
    kombin_notu TEXT,
    temiz INTEGER DEFAULT 1,
    foto_url TEXT
);
CREATE TABLE IF NOT EXISTS sohbetler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    rol TEXT NOT NULL,
    mesaj TEXT NOT NULL,
    olusturma_tarihi TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS kombin_oneriler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    baglam_json TEXT,
    onerilen_kiyafet_idleri TEXT,
    aciklama TEXT,
    begenildi INTEGER,
    olusturma_tarihi TEXT DEFAULT CURRENT_TIMESTAMP
);
'''
conn.executescript(sql)
conn.commit()
conn.close()
