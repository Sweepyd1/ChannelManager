from typing import TYPE_CHECKING
from ..db_manager import DatabaseManager
from sqlalchemy import select
from ..models import User
if TYPE_CHECKING:
    from .CommonCrud import CommonCRUD
    
class UserCRUD:
    db: DatabaseManager

    def __init__(self, db: DatabaseManager, common_crud: "CommonCRUD") -> None:
        self.db = db
        self.common = common_crud
    
    async def new_user(self, user_id:int) -> bool:
       async with self.db.get_session() as session:
                existing_user = await session.execute(select(User).where(User.id == user_id))
                existing_user = existing_user.scalar()

                if existing_user:
                    return True
                
                new_user = User(id=user_id)

                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return False