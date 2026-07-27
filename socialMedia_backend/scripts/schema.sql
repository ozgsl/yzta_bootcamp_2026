-- ============================================================
-- Dijital Gardrop — Sosyal Medya Modülü
-- Veritabanı: SQLite
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id       TEXT PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name  TEXT NOT NULL DEFAULT '',
    avatar_url    TEXT DEFAULT NULL,
    bio           TEXT DEFAULT NULL,
    followers_count INTEGER NOT NULL DEFAULT 0,
    following_count INTEGER NOT NULL DEFAULT 0,
    profile_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (profile_visibility IN ('public', 'private')),
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_users_username
    ON users(username);

-- ============================================================
-- 2. POSTS
-- ============================================================
CREATE TABLE IF NOT EXISTS posts (
    post_id              TEXT PRIMARY KEY,
    user_id              TEXT NOT NULL,
    image_url            TEXT NOT NULL,
    caption              TEXT DEFAULT NULL,
    visibility           TEXT NOT NULL DEFAULT 'public'
        CHECK (visibility IN ('public', 'followers', 'private')),
    ai_training_consent  INTEGER NOT NULL DEFAULT 0
        CHECK (ai_training_consent IN (0, 1)),
    likes_count          INTEGER NOT NULL DEFAULT 0,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Feed + profil sorgusu: kullanıcıya göre filtrele, zamana göre sırala
CREATE INDEX IF NOT EXISTS idx_posts_user_created
    ON posts(user_id, created_at DESC);

-- Genel sıralama
CREATE INDEX IF NOT EXISTS idx_posts_created
    ON posts(created_at DESC);

-- AI export batch job filtresi (partial index)
CREATE INDEX IF NOT EXISTS idx_posts_ai_export
    ON posts(ai_training_consent, visibility)
    WHERE ai_training_consent = 1;

-- ============================================================
-- 3. FOLLOWS  (Many-to-Many, normalised)
-- ============================================================
CREATE TABLE IF NOT EXISTS follows (
    follower_id   TEXT NOT NULL,
    following_id  TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CHECK (follower_id != following_id)
);

-- "Kimi takip ediyorum?"
CREATE INDEX IF NOT EXISTS idx_follows_follower
    ON follows(follower_id);

-- "Beni kim takip ediyor?"
CREATE INDEX IF NOT EXISTS idx_follows_following
    ON follows(following_id);

-- ============================================================
-- 4. LIKES  (Many-to-Many, normalised)
-- ============================================================
CREATE TABLE IF NOT EXISTS likes (
    post_id    TEXT NOT NULL,
    user_id    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id)  REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_likes_post
    ON likes(post_id);

CREATE INDEX IF NOT EXISTS idx_likes_user_post
    ON likes(user_id, post_id);

-- ============================================================
-- 5. POST_OUTFIT_ITEMS  (Post ↔ AI-module item join table)
-- ============================================================
CREATE TABLE IF NOT EXISTS post_outfit_items (
    post_id   TEXT NOT NULL,
    item_id   TEXT NOT NULL,
    category  TEXT NOT NULL DEFAULT 'diğer'
        CHECK (category IN (
            'üst giyim', 'alt giyim', 'ayakkabı',
            'aksesuar', 'dış giyim', 'diğer'
        )),
    image_url TEXT DEFAULT NULL,
    PRIMARY KEY (post_id, item_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_outfit_items_post
    ON post_outfit_items(post_id);

CREATE INDEX IF NOT EXISTS idx_outfit_items_item
    ON post_outfit_items(item_id);

-- ============================================================
-- 6. TRAINING_DATA_EXPORT  (AI export job output — ayrı tablo)
-- ============================================================
CREATE TABLE IF NOT EXISTS training_data_export (
    export_id   TEXT PRIMARY KEY,
    post_id     TEXT NOT NULL,
    export_data TEXT NOT NULL,          -- JSON string
    exported_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_export_post
    ON training_data_export(post_id);

-- ============================================================
-- 7. COMMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    post_id    TEXT NOT NULL,
    user_id    TEXT NOT NULL,
    content    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comments_post
    ON comments(post_id, created_at DESC);

-- ============================================================
-- 8. SAVES (Bookmarks)
-- ============================================================
CREATE TABLE IF NOT EXISTS saves (
    post_id    TEXT NOT NULL,
    user_id    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_saves_user
    ON saves(user_id, created_at DESC);

-- ============================================================
-- 9. KIYAFETLER (Wardrobe Items)
-- ============================================================
CREATE TABLE IF NOT EXISTS kiyafetler (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          TEXT    NOT NULL,
    tur              TEXT    NOT NULL,
    renk             TEXT    NOT NULL,
    marka            TEXT    DEFAULT NULL,
    beden            TEXT    DEFAULT NULL,
    kumas            TEXT    DEFAULT NULL,
    kesim            TEXT    DEFAULT NULL,
    yaka_tipi        TEXT    DEFAULT NULL,
    kol_tipi         TEXT    DEFAULT NULL,
    desen            TEXT    DEFAULT 'düz',
    mevsim           TEXT    DEFAULT 'tüm sezon',
    stil_etiketi     TEXT    DEFAULT NULL,
    kullanim_sikligi TEXT    DEFAULT NULL,
    kombin_notu      TEXT    DEFAULT NULL,
    temiz            INTEGER NOT NULL DEFAULT 1
        CHECK (temiz IN (0, 1)),
    foto_url         TEXT    DEFAULT NULL,
    olusturulma_tarihi TEXT  NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kiyafetler_user
    ON kiyafetler(user_id);

CREATE INDEX IF NOT EXISTS idx_kiyafetler_user_temiz
    ON kiyafetler(user_id, temiz);

-- ============================================================
-- 10. KATEGORİLER (Wardrobe Category Values)
-- ============================================================
CREATE TABLE IF NOT EXISTS kategoriler (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    tip   TEXT NOT NULL,
    deger TEXT NOT NULL,
    UNIQUE (tip, deger)
);

CREATE INDEX IF NOT EXISTS idx_kategoriler_tip
    ON kategoriler(tip);

-- ============================================================
-- 11. SOHBET_GECMİSİ (AI Chat History)
-- ============================================================
CREATE TABLE IF NOT EXISTS sohbet_gecmisi (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL,
    rol        TEXT NOT NULL CHECK (rol IN ('user', 'assistant')),
    icerik     TEXT NOT NULL,
    tarih      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sohbet_user
    ON sohbet_gecmisi(user_id, tarih DESC);

-- ============================================================
-- 12. KOMBİN_ONERİLERİ (Outfit Suggestions)
-- ============================================================
CREATE TABLE IF NOT EXISTS kombin_onerileri (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        TEXT    NOT NULL,
    baglam_json    TEXT    NOT NULL,
    kiyafet_idleri TEXT    NOT NULL,   -- JSON array
    aciklama       TEXT    DEFAULT NULL,
    olusturulma    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kombin_user
    ON kombin_onerileri(user_id, olusturulma DESC);
