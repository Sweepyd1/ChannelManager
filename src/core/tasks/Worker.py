from aiogram import Bot
import asyncio
from contextlib import suppress

class PostScheduler:
    def __init__(self, bot: Bot, max_concurrent=50):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._task = None

    async def _worker(self):
        while True:
            task_data = await self.queue.get()
            async with self.semaphore:  
                try:
                    await self._process_task(task_data)
                except Exception as e:
                    await self._handle_error(e, task_data)
                finally:
                    self.queue.task_done()

    async def add_task(self, task_data):
        await self.queue.put(task_data)

    async def start(self):
        self._task = asyncio.create_task(self._worker())

    async def stop(self):
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _process_task(self, task_data):
 
        await self.bot.send_message(
            chat_id=task_data['channel_id'],
            text=task_data['content'],
            disable_notification=True
        )
 
        await self._mark_as_done(task_data)

    async def _handle_error(self, error, task_data):

        if self._should_retry(error):
            await self.queue.put(task_data)