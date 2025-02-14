import datetime
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
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db_manager import Base


class TaskStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

task_channels = Table(
    "task_channels",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("channel_id", ForeignKey("channels.id"), primary_key=True),
)

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
        comment="Идентификатор пользователя в Telegram",
    )
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

class Channel(BaseModel):
    __tablename__ = "channels"
    __table_args__ = (
        Index("idx_telegram_chat_id", "telegram_chat_id", unique=True),
        {"comment": "Телеграм каналы для рассылки"},
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    telegram_chat_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("channel_groups.id")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="channels")
    group: Mapped[Optional["ChannelGroup"]] = relationship(back_populates="channels")
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        secondary=task_channels,
        back_populates="channels"
    )

class Post(BaseModel):
     __tablename__ = "posts"
     id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
     content: Mapped[dict] = mapped_column(
        JSON, comment="Структура: {'text': str, 'media': list}"
    )
     tasks: Mapped[List["Task"]] = relationship(back_populates="post")

class Task(BaseModel):
    __tablename__ = "tasks"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )

    post_id:Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("posts.id"))
    post: Mapped["Post"] = relationship(back_populates="tasks")

    channels: Mapped[List["Channel"]] = relationship(
        "Channel",
        secondary=task_channels,
        back_populates="tasks"
    )
    scheduled_time: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    status: Mapped["TaskStatus"] = mapped_column(String(20), default=TaskStatus.PENDING)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"))






    




