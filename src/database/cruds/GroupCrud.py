from typing import TYPE_CHECKING, List

from CommonCrud import CommonCRUD

from ..db_manager import DatabaseManager
from ..models import User, Task, ChannelGroup
from sqlalchemy import select

if TYPE_CHECKING:
    from CommonCrud import CommonCRUD

class GroupCRUD:
    db: DatabaseManager

    def __init__(self, db: DatabaseManager, common_crud: "CommonCRUD") -> None:
        self.db = db
        self.common = common_crud


    async def create_new_group(self, group_name:str, channels_links:List[str], user_id:int)->None:
        async with self.db.get_session() as session:
            exist_group = await session.execute(select(ChannelGroup.name).where(User.id == user_id))

            if exist_group:
                return "такая группа уже существует"
            new_group = ChannelGroup(
                name=group_name,
                user_id=user_id,
                channels=channels_links

            )
            session.add(new_group)
            await session.commit()
            await session.refresh(new_group)
            return new_group
            
    async def get_my_group(self, user_id:int):
        async with self.db.get_session() as session:
            groups = await session.execute(select(ChannelGroup).where(User.id == user_id))
            return groups.scalars().all()
        
    