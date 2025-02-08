from typing import TYPE_CHECKING
from ..db_manager import DatabaseManager

if TYPE_CHECKING:
    from .CommonCrud import CommonCRUD
    
class TaskCRUD:
    db: DatabaseManager

    def __init__(self, db: DatabaseManager, common_crud: "CommonCRUD") -> None:
        self.db = db
        self.common = common_crud