from __future__ import annotations
from typing import Optional
import sqlite3
import json

CATEGORY_TYPES = [
    "tur", "kumas", "kesim", "yaka_tipi", "kol_tipi",
    "desen", "mevsim", "stil_etiketi", "kullanim_sikligi",
]

CLOTH_FIELDS = [
    "tur", "renk", "renk_hex", "renk_kategori_id", "marka", "beden", "kumas", "kesim", "yaka_tipi",
    "kol_tipi", "desen", "mevsim", "stil_etiketi", "kullanim_sikligi",
    "kombin_notu", "temiz", "foto_url", "is_favorite",
]

class ItemRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    # ---------- Categories ----------
    def get_categories(self) -> dict[str, list[str]]:
        rows = self.db.execute("SELECT tip, deger FROM kategoriler ORDER BY tip, deger").fetchall()
        result: dict[str, list[str]] = {t: [] for t in CATEGORY_TYPES}
        for row in rows:
            result.setdefault(row["tip"], []).append(row["deger"])
        return result

    def add_category(self, category_type: str, value: str) -> int:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO kategoriler (tip, deger) VALUES (?, ?)",
            (category_type, value.strip()),
        )
        self.db.commit()
        return cur.lastrowid

    def delete_category(self, category_id: int):
        self.db.execute("DELETE FROM kategoriler WHERE id = ?", (category_id,))
        self.db.commit()

    def delete_category_by_value(self, category_type: str, value: str):
        self.db.execute("DELETE FROM kategoriler WHERE tip = ? AND deger = ?", (category_type, value))
        self.db.commit()

    # ---------- Clothes / Items ----------
    def add_cloth(self, user_id: str, **fields) -> int:
        columns = [k for k in fields if k in CLOTH_FIELDS]
        values = [fields[k] for k in columns]

        if "temiz" in columns:
            idx = columns.index("temiz")
            values[idx] = int(bool(values[idx]))
        if "is_favorite" in columns:
            idx = columns.index("is_favorite")
            values[idx] = int(bool(values[idx]))

        column_str = ", ".join(["user_id"] + columns)
        placeholders = ", ".join(["?"] * (len(columns) + 1))
        
        cur = self.db.execute(
            f"INSERT INTO kiyafetler ({column_str}) VALUES ({placeholders})",
            [user_id] + values,
        )
        self.db.commit()
        return cur.lastrowid

    def get_clothes(self, user_id: str, clean_only: bool = False) -> list[dict]:
        if clean_only:
            rows = self.db.execute(
                "SELECT * FROM kiyafetler WHERE user_id = ? AND temiz = 1 ORDER BY id DESC",
                (user_id,)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT * FROM kiyafetler WHERE user_id = ? ORDER BY id DESC",
                (user_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def get_cloth(self, item_id: int) -> Optional[dict]:
        row = self.db.execute("SELECT * FROM kiyafetler WHERE id = ?", (item_id,)).fetchone()
        return dict(row) if row else None

    def update_cloth(self, item_id: int, **fields) -> bool:
        columns = [k for k in fields if k in CLOTH_FIELDS]
        if not columns:
            return False

        values = [fields[k] for k in columns]
        if "temiz" in columns:
            idx = columns.index("temiz")
            values[idx] = int(bool(values[idx]))
        if "is_favorite" in columns:
            idx = columns.index("is_favorite")
            values[idx] = int(bool(values[idx]))

        set_clause = ", ".join([f"{k} = ?" for k in columns])
        cur = self.db.execute(
            f"UPDATE kiyafetler SET {set_clause} WHERE id = ?",
            values + [item_id],
        )
        self.db.commit()
        return cur.rowcount > 0

    def update_cloth_status(self, item_id: int, clean: bool):
        self.update_cloth(item_id, temiz=clean)

    def delete_cloth(self, item_id: int) -> bool:
        cur = self.db.execute("DELETE FROM kiyafetler WHERE id = ?", (item_id,))
        self.db.commit()
        return cur.rowcount > 0

    # ---------- Chat & Outfits ----------
    def create_chat_session(self, user_id: str, session_id: str, title: str):
        self.db.execute(
            "INSERT INTO sohbet_oturumlar (session_id, user_id, title) VALUES (?, ?, ?)",
            (session_id, user_id, title),
        )
        self.db.commit()

    def get_chat_sessions(self, user_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT session_id, title, created_at FROM sohbet_oturumlar WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def save_chat_message(self, user_id: str, role: str, message: str, session_id: str = None):
        self.db.execute(
            "INSERT INTO sohbet_gecmisi (session_id, user_id, rol, icerik) VALUES (?, ?, ?, ?)",
            (session_id, user_id, role, message),
        )
        self.db.commit()

    def get_chat_history(self, user_id: str, limit: int = 20, session_id: str = None) -> list[dict]:
        import json
        if session_id:
            rows = self.db.execute(
                "SELECT rol, icerik AS mesaj FROM sohbet_gecmisi WHERE user_id = ? AND session_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, session_id, limit),
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT rol, icerik AS mesaj FROM sohbet_gecmisi WHERE user_id = ? AND session_id IS NULL ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
            
        result = []
        for row in reversed(rows):
            try:
                content = json.loads(row["mesaj"])
                if isinstance(content, dict) and "text" in content:
                    result.append({
                        "rol": row["rol"],
                        "mesaj": content["text"],
                        "outfit_items": content.get("outfit_items", [])
                    })
                else:
                    result.append({"rol": row["rol"], "mesaj": row["mesaj"], "outfit_items": []})
            except json.JSONDecodeError:
                result.append({"rol": row["rol"], "mesaj": row["mesaj"], "outfit_items": []})
        return result

    def save_outfit_recommendation(self, user_id: str, context_json: str, item_ids: list[int], description: str) -> int:
        cur = self.db.execute(
            "INSERT INTO kombin_onerileri (user_id, baglam_json, kiyafet_idleri, aciklama) VALUES (?, ?, ?, ?)",
            (user_id, context_json, json.dumps(item_ids), description),
        )
        self.db.commit()
        return cur.lastrowid

    def save_outfit_feedback(self, recommendation_id: int, liked: bool):
        self.db.execute(
            "UPDATE kombin_onerileri SET begenildi = ? WHERE id = ?",
            (int(liked), recommendation_id),
        )
        self.db.commit()

    def get_outfit_recommendations(self, user_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM kombin_onerileri WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
        
        result = []
        for row in rows:
            outfit = dict(row)
            try:
                item_ids = json.loads(outfit["kiyafet_idleri"])
                clothes = []
                for k_id in item_ids:
                    k = self.get_cloth(k_id)
                    if k:
                        clothes.append(k)
                outfit["kiyafetler"] = clothes
                result.append(outfit)
            except Exception:
                pass
        return result

    def get_outfit_recommendation(self, recommendation_id: int) -> Optional[dict]:
        row = self.db.execute("SELECT * FROM kombin_onerileri WHERE id = ?", (recommendation_id,)).fetchone()
        if not row:
            return None
            
        outfit = dict(row)
        try:
            item_ids = json.loads(outfit["kiyafet_idleri"])
            clothes = []
            for k_id in item_ids:
                k = self.get_cloth(k_id)
                if k:
                    clothes.append(k)
            outfit["kiyafetler"] = clothes
        except Exception:
            outfit["kiyafetler"] = []
        return outfit

    def delete_outfit(self, recommendation_id: int) -> bool:
        cur = self.db.execute("DELETE FROM kombin_onerileri WHERE id = ?", (recommendation_id,))
        self.db.commit()
        return cur.rowcount > 0

    # Backwards compatibility aliases
    kategorileri_getir = get_categories
    kategori_ekle = add_category
    kategori_sil = delete_category
    kategori_deger_ile_sil = delete_category_by_value
    kiyafet_ekle = add_cloth
    kiyafetleri_getir = get_clothes
    kiyafet_getir = get_cloth
    kiyafet_guncelle = update_cloth
    kiyafet_durumunu_guncelle = update_cloth_status
    kiyafet_sil = delete_cloth
    mesaj_kaydet = save_chat_message
    sohbet_gecmisini_getir = get_chat_history
    kombin_onerisi_kaydet = save_outfit_recommendation
    kombin_geri_bildirim_kaydet = save_outfit_feedback
    kombin_onerilerini_getir = get_outfit_recommendations
    kombin_onerisini_getir = get_outfit_recommendation
    kombin_sil = delete_outfit
