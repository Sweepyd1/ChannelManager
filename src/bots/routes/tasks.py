from typing import Optional

from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message

from config import bot, description

from ..states.state import RegistrationStates

tasks = Router()



@tasks.message(Command("newtask"))
async def send_welcome(message: Message):
    await message.answer("таска принята")
 