from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Outfit(Base):
    __tablename__ = "outfits"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    context_json = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    liked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    user = relationship("Profile")

class OutfitItem(Base):
    __tablename__ = "outfit_items"
    outfit_id = Column(UUID(as_uuid=True), ForeignKey("outfits.id", ondelete="CASCADE"), primary_key=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True)
    
    outfit = relationship("Outfit", back_populates="items")
    item = relationship("WardrobeItem")
