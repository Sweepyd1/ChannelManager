from aiogram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
