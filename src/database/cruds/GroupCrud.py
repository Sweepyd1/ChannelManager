from typing import TYPE_CHECKING

from CommonCrud import CommonCRUD

from ..db_manager import DatabaseManager

if TYPE_CHECKING:
    from CommonCrud import CommonCRUD

class GroupCRUD:
    db: DatabaseManager

    def __init__(self, db: DatabaseManager, common_crud: "CommonCRUD") -> None:
        self.db = db
        self.common = common_crud


    async def create_new_group(self,):
        async with self.db.get_session() as session:
            ...