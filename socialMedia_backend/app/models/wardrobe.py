from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String, unique=True, nullable=False)
    gender = Column(String, nullable=True)

    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")

class Subcategory(Base):
    __tablename__ = "subcategories"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

    category = relationship("Category", back_populates="subcategories")
    items = relationship("WardrobeItem", back_populates="subcategory")

class Color(Base):
    __tablename__ = "colors"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String, unique=True, nullable=False)
    hex_code = Column(String, nullable=True)
    rgb = Column(String, nullable=True)
    family = Column(String, nullable=True)
    brightness = Column(String, nullable=True)

class Style(Base):
    __tablename__ = "styles"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String, unique=True, nullable=False)

class Season(Base):
    __tablename__ = "seasons"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String, unique=True, nullable=False)

class Occasion(Base):
    __tablename__ = "occasions"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String, unique=True, nullable=False)

class Attribute(Base):
    __tablename__ = "attributes"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True) # Supabase auth.users(id)
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id", ondelete="SET NULL"), nullable=True)
    primary_color_id = Column(UUID(as_uuid=True), ForeignKey("colors.id", ondelete="SET NULL"), nullable=True)
    brand = Column(String, nullable=True)
    size = Column(String, nullable=True)
    is_clean = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    purchase_date = Column(Date, nullable=True)
    last_worn_at = Column(DateTime(timezone=True), nullable=True)
    wear_count = Column(Integer, default=0, nullable=False)
    favorite = Column(Boolean, default=False, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    storage_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    subcategory = relationship("Subcategory", back_populates="items")
    primary_color = relationship("Color")
    user = relationship("Profile")
    
    
    # Many-to-many relationships
    styles = relationship("Style", secondary="wardrobe_item_styles")
    seasons = relationship("Season", secondary="wardrobe_item_seasons")
    occasions = relationship("Occasion", secondary="wardrobe_item_occasions")
    attributes = relationship("Attribute", secondary="wardrobe_item_attributes")

class WardrobeItemStyle(Base):
    __tablename__ = "wardrobe_item_styles"
    item_id = Column(UUID(as_uuid=True), ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True)
    style_id = Column(UUID(as_uuid=True), ForeignKey("styles.id", ondelete="CASCADE"), primary_key=True)

class WardrobeItemSeason(Base):
    __tablename__ = "wardrobe_item_seasons"
    item_id = Column(UUID(as_uuid=True), ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id", ondelete="CASCADE"), primary_key=True)

class WardrobeItemOccasion(Base):
    __tablename__ = "wardrobe_item_occasions"
    item_id = Column(UUID(as_uuid=True), ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True)
    occasion_id = Column(UUID(as_uuid=True), ForeignKey("occasions.id", ondelete="CASCADE"), primary_key=True)

class WardrobeItemAttribute(Base):
    __tablename__ = "wardrobe_item_attributes"
    item_id = Column(UUID(as_uuid=True), ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("attributes.id", ondelete="CASCADE"), primary_key=True)
