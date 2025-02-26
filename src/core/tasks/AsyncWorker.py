import asyncio
from typing import TYPE_CHECKING
from aiogram import Bot
from schemas import SheduledPost
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
if TYPE_CHECKING:
    from config import db

class AsyncWorker:
    def __init__(self, db, bot:Bot):
        self.db = db
        self.bot = bot
     
    async def start_database_polling(self,):
        try:
            while True:
                await asyncio.sleep(5)
                await self.get_schedule_task()
        except asyncio.CancelledError:
            print("Worker остановлен")


    async def send_to_channel(self, post: SheduledPost):
        try:
      
            if post.media:
               
                media_group = []
                for idx, file_id in enumerate(post.media):
                   
                    media_type = InputMediaDocument
                    
                    if file_id.startswith('AgAC'):
                        media_type = InputMediaPhoto
                    
                    elif file_id.startswith(('BAAC', 'CgAC')):
                        media_type = InputMediaVideo

                    media = media_type(
                        media=file_id,
                        caption=post.description if idx == 0 else None,
                        parse_mode="HTML"
                    )
                    media_group.append(media)


                await self.bot.send_media_group(
                    chat_id=post.channel,
                    media=media_group,
                    
                )
                
         
            else:
                await self.bot.send_message(
                    chat_id=post.channel,
                    text=post.description,
                    
                    
                )

       
            await self.db.tasks.update_task_status(
                task_id=post.task_id, 
                new_status="sent"
            )

        except Exception as e:
            print(f"Ошибка отправки поста {post.task_id}: {str(e)}")
            await self.db.tasks.update_task_status(
                task_id=post.task_id, 
                new_status="failed"
            )
           
    async def get_schedule_task(self):
        posts = await self.db.tasks.get_tasks_due_in_one_minutes()
        if posts:

            await asyncio.gather(
                *[self.send_to_channel(post) for post in posts]
            ) 
      
        



