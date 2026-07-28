from fastapi import APIRouter, Depends, Query, HTTPException
import sqlite3
from typing import List, Dict, Any

from app.core.database import get_db

router = APIRouter()

ACHIEVEMENTS = [
    {
        "id": "novice",
        "title": "Acemi Stilist",
        "description": "Spot'a katılan herkese verilir.",
        "icon": "🌱",
        "condition": lambda stats: True
    },
    {
        "id": "collector",
        "title": "Koleksiyoner",
        "description": "Gardırobuna 20'den fazla kıyafet eklendi.",
        "icon": "🛍️",
        "condition": lambda stats: stats.get("total_items", 0) >= 20
    },
    {
        "id": "architect",
        "title": "Kombin Ustası",
        "description": "10'dan fazla kombin oluşturuldu.",
        "icon": "✨",
        "condition": lambda stats: stats.get("total_outfits", 0) >= 10
    },
    {
        "id": "icon",
        "title": "Moda İkonu",
        "description": "Paylaştığın postlarda 50'den fazla beğeni aldın.",
        "icon": "🌟",
        "condition": lambda stats: stats.get("total_likes_received", 0) >= 50
    },
    {
        "id": "social",
        "title": "Sosyal Kelebek",
        "description": "10'dan fazla post beğendin veya etkileşimde bulundun.",
        "icon": "🦋",
        "condition": lambda stats: stats.get("total_likes_given", 0) >= 10
    }
]

@router.get("/{user_id}")
def get_user_analytics(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Kullanıcı istatistiklerini ve kazandığı ünvanları getirir."""
    try:
        # Temel İstatistikler
        items_count = db.execute("SELECT COUNT(*) FROM kiyafetler WHERE user_id = ?", (user_id,)).fetchone()[0]
        outfits_count = db.execute("SELECT COUNT(*) FROM kombin_onerileri WHERE user_id = ?", (user_id,)).fetchone()[0]
        posts_count = db.execute("SELECT COUNT(*) FROM posts WHERE user_id = ?", (user_id,)).fetchone()[0]
        
        likes_received = db.execute("SELECT SUM(likes_count) FROM posts WHERE user_id = ?", (user_id,)).fetchone()[0] or 0
        likes_given = db.execute("SELECT COUNT(*) FROM likes WHERE user_id = ?", (user_id,)).fetchone()[0]
        
        stats = {
            "total_items": items_count,
            "total_outfits": outfits_count,
            "total_posts": posts_count,
            "total_likes_received": likes_received,
            "total_likes_given": likes_given,
        }

        # En çok kullanılan renkler (Top Colors) - Yüzde olarak
        colors_query = db.execute(
            """SELECT renk, COUNT(*) as count 
               FROM kiyafetler 
               WHERE user_id = ? AND renk IS NOT NULL AND renk != '' 
               GROUP BY renk 
               ORDER BY count DESC 
               LIMIT 3""", (user_id,)
        ).fetchall()
        
        # Calculate percentage for colors
        top_colors = []
        if items_count > 0:
            for c in colors_query:
                pct = c["count"] / items_count
                top_colors.append({"label": c["renk"].capitalize(), "percentage": round(pct, 2)})

        # En çok giyilen kategoriler (Top Categories)
        categories_query = db.execute(
            """SELECT tur, COUNT(*) as count 
               FROM kiyafetler 
               WHERE user_id = ? 
               GROUP BY tur 
               ORDER BY count DESC 
               LIMIT 3""", (user_id,)
        ).fetchall()
        
        top_categories = []
        for cat in categories_query:
            top_categories.append({"label": cat["tur"].capitalize(), "count": f"{cat['count']} items"})

        # Ünvanların hesaplanması (Unlocked Achievements)
        unlocked_titles = []
        for ach in ACHIEVEMENTS:
            if ach["condition"](stats):
                unlocked_titles.append({
                    "id": ach["id"],
                    "title": ach["title"],
                    "description": ach["description"],
                    "icon": ach["icon"]
                })

        return {
            "stats": stats,
            "top_colors": top_colors,
            "top_categories": top_categories,
            "unlocked_titles": unlocked_titles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
