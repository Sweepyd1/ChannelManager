import asyncio
import logging
import sys


import uvloop
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import bot
from bots.routes.base import base_router
from bots.routes.group import group_router
from bots.routes.tasks import tasks
from config import parser, worker

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(base_router)
dp.include_router(group_router)
dp.include_router(tasks)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await asyncio.gather(
        dp.start_polling(bot),
        worker.start_database_polling()
    )


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
