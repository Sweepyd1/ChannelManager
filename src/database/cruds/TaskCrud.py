from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import and_, func, select, update
from ..db_manager import DatabaseManager
from ..models import Post, Task, TaskStatus,task_channels, Channel
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from schemas.SheduledPost import SheduledPost

if TYPE_CHECKING:
    from .CommonCrud import CommonCRUD


class TaskCRUD:
    db: DatabaseManager

    def __init__(self, db: DatabaseManager, common_crud: "CommonCRUD") -> None:
        self.db = db
        self.common = common_crud

    async def create_new_task(
            self,
            channels: list,  
            post_content: dict,  
            user_id: int, 
            scheduled_time: Optional[datetime] = None  
        ):
        async with self.db.get_session() as session:
  
            new_post = Post(
                content=post_content,
            )
            session.add(new_post)
            await session.flush() 

            task = Task(
                post_id=new_post.id,
                scheduled_time=scheduled_time,
                status=TaskStatus.PENDING,
                user_id=user_id
            )

            for channel in channels:
                task.channels.append(channel)  

            session.add(task)  

            await session.commit()  
            return new_post, task  

    async def get_tasks_due_in_one_minutes(self) -> List[SheduledPost]:
        async with self.db.get_session() as session:
            print('Начало выполнения запроса')
            
            query = (
                select(task_channels.c.task_id, Post.content, task_channels.c.channel_id, Channel.telegram_chat_id)
                .select_from(Task)
                .join(task_channels, Task.id == task_channels.c.task_id)
                .join(Post, Task.post_id == Post.id)
                .join(Channel,task_channels.c.channel_id == Channel.id )
                .where(
                    and_(
                        Task.status == 'pending',
                        Task.scheduled_time < func.now(),
                        Task.scheduled_time.isnot(None)
                    )
                )
            )
            result = await session.execute(query)

            all_posts = []
            
            tasks = result.all()
            print(f"Найдено задач: {len(tasks)}")
            for i in range(len(tasks)):
               

                post = SheduledPost(
                    task_id = str(tasks[i][0]),
                    description = tasks[i][1]["caption"],
                    media = tasks[i][1]["media"],
                    channel=tasks[i][3]
                )
                
                all_posts.append(post)
            return all_posts

    async def update_task_status(self, task_id, new_status: str) -> bool:
        async with self.db.get_session() as session:
            try:
                stmt = (
                            update(Task)
                            .where(Task.id == task_id)
                            .values(status=new_status)
                            .returning(Task)
                        )
                        
                result = await session.execute(stmt)
                await session.commit()
                        
                return result.scalar_one_or_none() is not None
                        
            except Exception as e:
                print(e)
                await session.rollback()
                return False

        