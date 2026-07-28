"""
Users Router — Kullanıcı profili ve istatistikleri.
Python 3.9 uyumlu.
"""
from __future__ import annotations

import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from typing import Optional

from app.core.database import get_db
from app.domain.schemas import UserResponse, UserStatsResponse, ProfileUpdateRequest, PrivacySettingsRequest, MessageResponse

router = APIRouter()


def _get_user_row(db: sqlite3.Connection, user_id: str):
    """Kullanıcı satırını getirir, yoksa 404 fırlatır."""
    row = db.execute(
        """
        SELECT user_id, email, username, display_name, avatar_url, bio,
               followers_count, following_count, created_at, profile_visibility,
               height, weight, chest, waist, hips, location, timezone, active_title
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return row


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    viewer_id: Optional[str] = Query(None, description="Görüntüleyen kullanıcı ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """Kullanıcı profil bilgisini döndürür."""
    try:
        row = _get_user_row(db, user_id)

        # Gizlilik kontrolü: private profil, takipçi olmayan kişilere kısıtlı
        if row["profile_visibility"] == "private" and viewer_id and viewer_id != user_id:
            follow_check = db.execute(
                "SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?",
                (viewer_id, user_id),
            ).fetchone()
            if not follow_check:
                raise HTTPException(status_code=403, detail="Bu profil gizli.")

        is_following = False
        if viewer_id and viewer_id != user_id:
            follow_check = db.execute(
                "SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?",
                (viewer_id, user_id),
            ).fetchone()
            is_following = follow_check is not None

        return UserResponse(
            user_id=row["user_id"],
            email=row["email"],
            username=row["username"],
            display_name=row["display_name"],
            avatar_url=row["avatar_url"],
            bio=row["bio"],
            followers_count=row["followers_count"],
            following_count=row["following_count"],
            created_at=row["created_at"],
            is_following=is_following,
            profile_visibility=row["profile_visibility"],
            height=row["height"],
            weight=row["weight"],
            chest=row["chest"],
            waist=row["waist"],
            hips=row["hips"],
            location=row["location"],
            timezone=row["timezone"],
            active_title=row["active_title"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı getirilirken hata: {str(e)}")


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Kullanıcı istatistiklerini döndürür."""
    try:
        row = db.execute(
            """
            SELECT u.user_id, u.followers_count, u.following_count,
                   (SELECT COUNT(*) FROM posts WHERE user_id = u.user_id) AS posts_count
            FROM users u
            WHERE u.user_id = ?
            """,
            (user_id,),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        return UserStatsResponse(
            user_id=row["user_id"],
            followers_count=row["followers_count"],
            following_count=row["following_count"],
            posts_count=row["posts_count"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistikler getirilirken hata: {str(e)}")


@router.put("/me", response_model=MessageResponse)
def update_profile(
    body: ProfileUpdateRequest,
    authorization: Optional[str] = Header(None),
    db: sqlite3.Connection = Depends(get_db),
):
    """Kullanıcı profil bilgilerini günceller. Authorization: Bearer <user_id>"""
    user_id = _extract_user_id(authorization)
    try:
        updates = []
        values = []
        if body.username is not None:
            # Check if username is taken
            check = db.execute("SELECT 1 FROM users WHERE username = ? AND user_id != ?", (body.username, user_id)).fetchone()
            if check:
                raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış.")
            updates.append("username = ?")
            values.append(body.username)
        if body.display_name is not None:
            updates.append("display_name = ?")
            values.append(body.display_name)
        if body.bio is not None:
            updates.append("bio = ?")
            values.append(body.bio)
        if body.avatar_url is not None:
            updates.append("avatar_url = ?")
            values.append(body.avatar_url)
        if body.height is not None:
            updates.append("height = ?")
            values.append(body.height)
        if body.weight is not None:
            updates.append("weight = ?")
            values.append(body.weight)
        if body.chest is not None:
            updates.append("chest = ?")
            values.append(body.chest)
        if body.waist is not None:
            updates.append("waist = ?")
            values.append(body.waist)
        if body.hips is not None:
            updates.append("hips = ?")
            values.append(body.hips)
        if body.location is not None:
            updates.append("location = ?")
            values.append(body.location)
        if body.timezone is not None:
            updates.append("timezone = ?")
            values.append(body.timezone)

        if not updates:
            return MessageResponse(success=True, message="Güncellenecek alan yok.")

        values.append(user_id)
        db.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?", values)
        db.commit()
        return MessageResponse(success=True, message="Profil güncellendi.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me/privacy", response_model=MessageResponse)
def update_privacy(
    body: PrivacySettingsRequest,
    authorization: Optional[str] = Header(None),
    db: sqlite3.Connection = Depends(get_db),
):
    """Gizlilik ayarını günceller (public/private)."""
    user_id = _extract_user_id(authorization)
    try:
        db.execute(
            "UPDATE users SET profile_visibility = ? WHERE user_id = ?",
            (body.profile_visibility, user_id),
        )
        db.commit()
        return MessageResponse(success=True, message=f"Gizlilik ayarı '{body.profile_visibility}' olarak güncellendi.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me", response_model=MessageResponse)
def delete_account(
    authorization: Optional[str] = Header(None),
    db: sqlite3.Connection = Depends(get_db),
):
    """Hesabı siler."""
    user_id = _extract_user_id(authorization)
    try:
        db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        db.commit()
        return MessageResponse(success=True, message="Hesap silindi.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/title", response_model=MessageResponse)
def set_active_title(
    user_id: str,
    title: Optional[str] = Query(None, description="Seçilen ünvan başlığı. Boş bırakılırsa kaldırılır."),
    db: sqlite3.Connection = Depends(get_db),
):
    """Kullanıcının aktif ünvanını ayarlar veya kaldırır."""
    try:
        db.execute(
            "UPDATE users SET active_title = ? WHERE user_id = ?",
            (title, user_id),
        )
        db.commit()
        msg = f"Ünvan '{title}' olarak güncellendi." if title else "Ünvan kaldırıldı."
        return MessageResponse(success=True, message=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _extract_user_id(authorization: Optional[str]) -> str:
    """Authorization: Bearer <user_id> header'ından user_id çıkarır."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Yetkilendirme gerekli.")
    return authorization.removeprefix("Bearer ").strip()
