from typing import TYPE_CHECKING, List
from ..db_manager import DatabaseManager
from ..models import Post
from datetime import datetime

if TYPE_CHECKING:
    from .CommonCrud import CommonCRUD


class TaskCRUD:
    db: DatabaseManager

    def __init__(self, db: DatabaseManager, common_crud: "CommonCRUD") -> None:
        self.db = db
        self.common = common_crud

    async def create_new_task(
        self,
        groups: list,
        post: list,
        user_id: int,
    ): ...

    async def create_scheduled_task(
        self, content: dict, user_id: int, scheduled_time: datetime
    ):
        async with self.db.get_session() as session:
            new_post = Post()
