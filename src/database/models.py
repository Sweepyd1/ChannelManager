from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    BIGINT,
    JSON,
    TEXT,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db_manager import Base


class TaskStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class BaseModel(Base):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = {"comment": "Пользователи телеграм бота"}

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        index=True,
        comment="Идентификатор пользователя в Telegram"
    )
    posts: Mapped[List["Post"]] = relationship(back_populates="user")
    channels: Mapped[List["Channel"]] = relationship(back_populates="user")
    channel_groups: Mapped[List["ChannelGroup"]] = relationship(back_populates="user")


class ChannelGroup(BaseModel):
    __tablename__ = "channel_groups"
    __table_args__ = {"comment": "Группы каналов для массовой рассылки"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="channel_groups")
    channels: Mapped[List["Channel"]] = relationship(back_populates="group")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class Channel(BaseModel):
    __tablename__ = "channels"
    __table_args__ = (
        Index("idx_telegram_chat_id", "telegram_chat_id", unique=True),
        {"comment": "Телеграм каналы для рассылки"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    telegram_chat_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("channel_groups.id"))
    group: Mapped[Optional["ChannelGroup"]] = relationship(back_populates="channels")
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="channels")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class Post(BaseModel):
    __tablename__ = "posts"
    __table_args__ = {"comment": "Посты для рассылки по каналам"}

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    content: Mapped[dict] = mapped_column(
        JSON, 
        comment="Структура: {'text': str, 'media': list, 'buttons': list}"
    )
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.PENDING)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="posts")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    scheduled_time: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    tasks: Mapped[List["Task"]] = relationship(back_populates="post")


class Task(BaseModel):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_task_status", "status"),
        {"comment": "Задачи на отправку постов в каналы"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("posts.id"))
    post: Mapped["Post"] = relationship(back_populates="tasks")
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.id"))
    channel: Mapped["Channel"] = relationship()
    status: Mapped[TaskStatus] = mapped_column(String(20), default=TaskStatus.PENDING)
    sent_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(TEXT)
    message_id: Mapped[Optional[int]] = mapped_column(BIGINT)