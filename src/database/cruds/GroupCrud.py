from typing import TYPE_CHECKING, List

from sqlalchemy import select

from ..db_manager import DatabaseManager
from ..models import Channel, ChannelGroup, Task, User

if TYPE_CHECKING:
    from .CommonCrud import CommonCRUD

class GroupCRUD:
    db: DatabaseManager

    def __init__(self, db: DatabaseManager, common_crud: "CommonCRUD") -> None:
        self.db = db
        self.common = common_crud


    async def create_new_group(
        self, 
        group_name: str, 
        channels_ids: List[int], 
        links: List[str], 
        user_id: int
    ) -> ChannelGroup:
        
        async with self.db.get_session() as session:
            async with session.begin():
 
                existing_group = await session.execute(
                    select(ChannelGroup).where(
                        ChannelGroup.user_id == user_id,
                        ChannelGroup.name == group_name
                    )
                )
                if existing_group.scalar_one_or_none():
                    raise ValueError("Группа с таким именем уже существует")


                new_group = ChannelGroup(
                    name=group_name,
                    user_id=user_id
                )
                session.add(new_group)
                await session.flush()


                for chat_id, link in zip(channels_ids, links):

                    username = self.extract_username_from_link(link)
                    

                    existing_channel = await session.execute(
                        select(Channel).where(
                            Channel.telegram_chat_id == chat_id,
                            Channel.user_id == user_id
                        )
                    )
                    channel = existing_channel.scalar_one_or_none()

                    if channel:

                        channel.group_id = new_group.id
                        channel.username = username
                    else:

                        session.add(Channel(
                            telegram_chat_id=chat_id,
                            name=username, 
                            user_id=user_id,
                            group_id=new_group.id,
                            is_active=True,

                        ))

                await session.commit()
                return new_group

    def extract_username_from_link(self, link: str) -> str:
        if link.startswith("https://t.me/"):
            return link.split("https://t.me/")[1].split("/")[0].strip()
        if link.startswith("@"):
            return link[1:].split()[0].strip()
        raise ValueError("Некорректный формат ссылки")
                
    async def get_my_group(self, user_id: int) -> List[ChannelGroup]:
        async with self.db.get_session() as session:
        
            query = select(ChannelGroup).where(ChannelGroup.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()
        
    async def get_channels_for_group(self, group_id, user_id)->List[Channel]:
         async with self.db.get_session() as session:
            query = select(Channel).where(Channel.group_id == group_id, Channel.user_id==user_id)
            result = await session.execute(query)
            return result.scalars().all()

        
    
            
    