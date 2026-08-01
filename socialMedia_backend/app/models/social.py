from sqlalchemy import (
    JSON,
    Boolean,
    Column,
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


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()) # We generate UUID since no Supabase Auth yet
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True) # nullable for OAuth
    totp_secret = Column(String, nullable=True)
    two_fa_enabled = Column(Boolean, default=False, nullable=False)
    username = Column(String, unique=True, nullable=True)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    followers_count = Column(Integer, default=0, nullable=False)
    following_count = Column(Integer, default=0, nullable=False)
    profile_visibility = Column(String, default="public", nullable=False)
    height = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    chest = Column(String, nullable=True)
    waist = Column(String, nullable=True)
    hips = Column(String, nullable=True)
    location = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True) # FK to auth.users(id) conceptually
    image_url = Column(String, nullable=True) # or storage_path
    content = Column(Text, nullable=True)
    outfit_id = Column(UUID(as_uuid=True), nullable=True)
    visibility = Column(String, default='public', nullable=False)
    ai_training_consent = Column(Boolean, default=False, nullable=False)
    likes_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    saves = relationship("Save", back_populates="post", cascade="all, delete-orphan")
    user = relationship("Profile", primaryjoin="Post.user_id == foreign(Profile.id)", uselist=False)

class Follow(Base):
    __tablename__ = "follows"
    follower_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    following_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Like(Base):
    __tablename__ = "likes"
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    post = relationship("Post", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content = Column(Text, nullable=False)
    parent_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    post = relationship("Post", back_populates="comments")

class Save(Base):
    __tablename__ = "saves"
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    post = relationship("Post", back_populates="saves")

class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class CommentReport(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    reporter_user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    comment = relationship("Comment")
    reporter = relationship("Profile")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("Profile", foreign_keys=[user_id])
    actor = relationship("Profile", foreign_keys=[actor_id])
    post = relationship("Post")
    comment = relationship("Comment")

class TrainingDataExport(Base):
    __tablename__ = "training_data_export"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    export_data = Column(JSON, nullable=False)
    exported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
