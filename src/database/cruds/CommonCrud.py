from GroupCrud import GroupCRUD
from TaskCrud import TaskCRUD

from ..db_manager import DatabaseManager


class CommonCRUD:
    __slots__ = (
        "db_manager",
        "tasks",
        "group",
    )

    tasks: TaskCRUD
    group: GroupCRUD

    def __init__(self, db_manager: DatabaseManager) -> None:
        
        self.db_manager = db_manager
        self.tasks = TaskCRUD(self.db_manager, self)
        self.groups = GroupCRUD(self.db_manager, self)
