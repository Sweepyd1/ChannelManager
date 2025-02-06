from datetime import datetime
from typing import Any, List
from uuid import UUID

from sqlalchemy import (
    BIGINT,
    JSON,
    TEXT,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db_manager import Base


class BaseModel(Base):
    __abstract__ = True
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
class User(BaseModel):
    __tablename__: str = "users"
    __tableargs__: dict = {"comment": "Пользователи нашего телеграм бота"}
    


class ChannelGroup(BaseModel):
    __tablename__ = 'channel_groups'
    __tableargs__: dict = {"comment": "Группы каналов, в одной группе может быть множетсво каналов, по которым ведется рассылка"}
    
    
class Tasks(BaseModel):
    __tablename__: str = "tasks"
    __tableargs__: dict = {"comment": "Пользователи нашего телеграм бота"}
    
