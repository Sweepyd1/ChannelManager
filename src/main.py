from aiogram import Dispatcher, types
from core.tasks import async_task
import asyncio
import uvloop
from config import bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Hello! Starting task...")
    async_task.delay()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())

