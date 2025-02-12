from aiogram import Bot
from dotenv import load_dotenv
import os
from database.cruds.CommonCrud import CommonCRUD
from database.db_manager import DatabaseManager
from core.parser.Parser import Parser
from core.tasks.schedule import Schedule


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)


DATABASE_URL = os.getenv("DATABASE_URL")

db_manager = DatabaseManager(DATABASE_URL)
db = CommonCRUD(db_manager)

scheduler = Schedule()
parser = Parser()

print("coonect")
description = (
    "Этот бот создан для управления и автоматизации процессов в более чем 1000 каналах одновременно.\n"
    "Он помогает администраторам и владельцам каналов эффективно взаимодействовать с подписчиками, "
    "предоставляя инструменты для планирования публикаций, анализа статистики и автоматического ответа на часто задаваемые вопросы.\n"
    "С помощью нашего бота вы сможете сэкономить время и сосредоточиться на создании качественного контента, "
    "не беспокоясь о рутинных задачах."
)
