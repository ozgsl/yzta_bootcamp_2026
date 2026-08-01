from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import engine
from app.models.outfit import OutfitItem
from app.models.social import Post, TrainingDataExport

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXPORTS_DIR = BASE_DIR / "exports"

def _build_post_records(db: Session, posts: list[Post]) -> list[dict]:
    """
    SQLAlchemy modellerini kullanarak JSON sözleşmesine uygun kayıtlara dönüştürür.
    """
    records = []
    
    for post in posts:
        record = {
            "post_id": str(post.id),
            "image_url": post.image_url,
            "outfit_items": [],
            "created_at": post.created_at.isoformat() if post.created_at else None,
        }
        
        if post.outfit_id:
            outfit_items = db.scalars(select(OutfitItem).where(OutfitItem.outfit_id == post.outfit_id)).all()
            for oi in outfit_items:
                if oi.item and oi.item.subcategory and oi.item.subcategory.category:
                    cat_name = oi.item.subcategory.category.name
                else:
                    cat_name = "Unknown"
                    
                record["outfit_items"].append({
                    "item_id": str(oi.item_id),
                    "category": cat_name,
                    "image_url": oi.item.storage_path if oi.item else None
                })
        
        records.append(record)
        
    return records


def run_export(
    db: Session | None = None,
    exports_dir: Path | None = None,
) -> list[dict]:
    """
    Ana export fonksiyonu.
    """
    own_session = db is None
    session = db or Session(engine)
    
    target_dir = exports_dir or EXPORTS_DIR
    
    try:
        # Get posts that have consent, are not private, and are not in TrainingDataExport
        subq = select(TrainingDataExport.post_id)
        query = select(Post).where(
            Post.ai_training_consent == True,
            Post.visibility != 'private',
            Post.id.not_in(subq)
        ).order_by(Post.created_at.asc())
        
        posts = session.scalars(query).all()
        
        if not posts:
            logger.info("Export edilecek yeni post bulunamadı.")
            return []
            
        records = _build_post_records(session, posts)
        
        # Insert into TrainingDataExport
        exports_to_add = []
        for rec in records:
            exports_to_add.append(TrainingDataExport(
                post_id=rec["post_id"],
                export_data=rec
            ))
            
        session.add_all(exports_to_add)
        session.commit()
        
        # Write to JSON file
        target_dir.mkdir(parents=True, exist_ok=True)
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        file_path = target_dir / f"training_export_{today_str}.json"
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(records, fp, ensure_ascii=False, indent=2)
            
        logger.info(
            "Export tamamlandı: %d post işlendi → %s", len(records), file_path
        )
        return records
        
    except Exception:
        logger.exception("Export sırasında hata oluştu.")
        session.rollback()
        raise
    finally:
        if own_session:
            session.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = run_export()
    print(f"Toplam {len(result)} post export edildi.")
