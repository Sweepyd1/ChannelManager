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
from config import parser

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(base_router)
dp.include_router(group_router)
dp.include_router(tasks)

async def main():

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)
    await parser.start_parsing(random=True, period=2, parsing_channel_id="-1002401238189")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
