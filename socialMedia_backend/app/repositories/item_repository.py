from __future__ import annotations
from typing import Optional
import sqlite3
import json

KATEGORI_TIPLERI = [
    "tur", "kumas", "kesim", "yaka_tipi", "kol_tipi",
    "desen", "mevsim", "stil_etiketi", "kullanim_sikligi",
]

KIYAFET_ALANLARI = [
    "tur", "renk", "renk_hex", "renk_kategori_id", "marka", "beden", "kumas", "kesim", "yaka_tipi",
    "kol_tipi", "desen", "mevsim", "stil_etiketi", "kullanim_sikligi",
    "kombin_notu", "temiz", "foto_url", "is_favorite",
]

class ItemRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    # ---------- Kategoriler ----------
    def kategorileri_getir(self) -> dict[str, list[str]]:
        rows = self.db.execute("SELECT tip, deger FROM kategoriler ORDER BY tip, deger").fetchall()
        sonuc: dict[str, list[str]] = {tip: [] for tip in KATEGORI_TIPLERI}
        for row in rows:
            sonuc.setdefault(row["tip"], []).append(row["deger"])
        return sonuc

    def kategori_ekle(self, tip: str, deger: str) -> int:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO kategoriler (tip, deger) VALUES (?, ?)",
            (tip, deger.strip()),
        )
        self.db.commit()
        return cur.lastrowid

    def kategori_sil(self, kategori_id: int):
        self.db.execute("DELETE FROM kategoriler WHERE id = ?", (kategori_id,))
        self.db.commit()

    def kategori_deger_ile_sil(self, tip: str, deger: str):
        self.db.execute("DELETE FROM kategoriler WHERE tip = ? AND deger = ?", (tip, deger))
        self.db.commit()

    # ---------- Kıyafetler ----------
    def kiyafet_ekle(self, user_id: str, **alanlar) -> int:
        kolonlar = [k for k in alanlar if k in KIYAFET_ALANLARI]
        degerler = [alanlar[k] for k in kolonlar]

        if "temiz" in kolonlar:
            idx = kolonlar.index("temiz")
            degerler[idx] = int(bool(degerler[idx]))
        if "is_favorite" in kolonlar:
            idx = kolonlar.index("is_favorite")
            degerler[idx] = int(bool(degerler[idx]))

        kolon_str = ", ".join(["user_id"] + kolonlar)
        soru_isaretleri = ", ".join(["?"] * (len(kolonlar) + 1))
        
        cur = self.db.execute(
            f"INSERT INTO kiyafetler ({kolon_str}) VALUES ({soru_isaretleri})",
            [user_id] + degerler,
        )
        self.db.commit()
        return cur.lastrowid

    def kiyafetleri_getir(self, user_id: str, sadece_temiz: bool = False) -> list[dict]:
        if sadece_temiz:
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

    def kiyafet_getir(self, kiyafet_id: int) -> Optional[dict]:
        row = self.db.execute("SELECT * FROM kiyafetler WHERE id = ?", (kiyafet_id,)).fetchone()
        return dict(row) if row else None

    def kiyafet_guncelle(self, kiyafet_id: int, **alanlar) -> bool:
        kolonlar = [k for k in alanlar if k in KIYAFET_ALANLARI]
        if not kolonlar:
            return False

        degerler = [alanlar[k] for k in kolonlar]
        if "temiz" in kolonlar:
            idx = kolonlar.index("temiz")
            degerler[idx] = int(bool(degerler[idx]))
        if "is_favorite" in kolonlar:
            idx = kolonlar.index("is_favorite")
            degerler[idx] = int(bool(degerler[idx]))

        set_ifadesi = ", ".join([f"{k} = ?" for k in kolonlar])
        cur = self.db.execute(
            f"UPDATE kiyafetler SET {set_ifadesi} WHERE id = ?",
            degerler + [kiyafet_id],
        )
        self.db.commit()
        return cur.rowcount > 0

    def kiyafet_durumunu_guncelle(self, kiyafet_id: int, temiz: bool):
        self.kiyafet_guncelle(kiyafet_id, temiz=temiz)

    def kiyafet_sil(self, kiyafet_id: int) -> bool:
        cur = self.db.execute("DELETE FROM kiyafetler WHERE id = ?", (kiyafet_id,))
        self.db.commit()
        return cur.rowcount > 0

    # ---------- Sohbet ve Kombin ----------
    def mesaj_kaydet(self, user_id: str, rol: str, mesaj: str):
        self.db.execute(
            "INSERT INTO sohbet_gecmisi (user_id, rol, icerik) VALUES (?, ?, ?)",
            (user_id, rol, mesaj),
        )
        self.db.commit()

    def sohbet_gecmisini_getir(self, user_id: str, limit: int = 20) -> list[dict]:
        rows = self.db.execute(
            "SELECT rol, icerik AS mesaj FROM sohbet_gecmisi WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def kombin_onerisi_kaydet(self, user_id: str, baglam_json: str, kiyafet_idleri: list[int], aciklama: str) -> int:
        import json as _json
        cur = self.db.execute(
            "INSERT INTO kombin_onerileri (user_id, baglam_json, kiyafet_idleri, aciklama) VALUES (?, ?, ?, ?)",
            (user_id, baglam_json, _json.dumps(kiyafet_idleri), aciklama),
        )
        self.db.commit()
        return cur.lastrowid

    def kombin_geri_bildirim_kaydet(self, oneri_id: int, begenildi: bool):
        self.db.execute(
            "UPDATE kombin_onerileri SET begenildi = ? WHERE id = ?",
            (int(begenildi), oneri_id),
        )
        self.db.commit()

    def kombin_onerilerini_getir(self, user_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM kombin_onerileri WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
        
        sonuc = []
        for row in rows:
            kombin = dict(row)
            try:
                import json as _json
                # kiyafet_idleri'ni çözümle ve kıyafetleri getir
                kiyafet_idleri = _json.loads(kombin["kiyafet_idleri"])
                
                kiyafetler = []
                for k_id in kiyafet_idleri:
                    k = self.kiyafet_getir(k_id)
                    if k:
                        kiyafetler.append(k)
                        
                kombin["kiyafetler"] = kiyafetler
                sonuc.append(kombin)
            except:
                pass
        return sonuc

    def kombin_onerisini_getir(self, oneri_id: int) -> Optional[dict]:
        row = self.db.execute("SELECT * FROM kombin_onerileri WHERE id = ?", (oneri_id,)).fetchone()
        if not row:
            return None
            
        kombin = dict(row)
        try:
            import json as _json
            kiyafet_idleri = _json.loads(kombin["kiyafet_idleri"])
            kiyafetler = []
            for k_id in kiyafet_idleri:
                k = self.kiyafet_getir(k_id)
                if k:
                    kiyafetler.append(k)
            kombin["kiyafetler"] = kiyafetler
        except:
            kombin["kiyafetler"] = []
        return kombin

    def kombin_sil(self, oneri_id: int) -> bool:
        cur = self.db.execute("DELETE FROM kombin_onerileri WHERE id = ?", (oneri_id,))
        self.db.commit()
        return cur.rowcount > 0
