from typing import Optional

from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message

from config import bot, db, description

from ..states.state import RegistrationStates

base_router = Router()
first_channel_id = "-1002401238189"


@base_router.message(CommandStart())
async def send_welcome(message: Message):
    # await message.reply("Hello! Starting task...")
    user = await db.users.new_user(message.from_user.id)
    if user:
        message.reply("такой пользовател уже существует")
        await bot.send_message(chat_id=first_channel_id, text="такой пользовател уже существует")
        return
    await bot.send_message(chat_id=first_channel_id, text="регистрация нового пользоватекля прошла успешан")


@base_router.message(Command('showchannelid'))
async def check_channel_id(message: types.Message, state: FSMContext):
    await message.reply("Отправьте мне публичную ссылку на канал или его username")

    await state.set_state(RegistrationStates.waiting_for_url)  


@base_router.message(RegistrationStates.waiting_for_url)
async def process_channel_info(message: types.Message, state: FSMContext,):
    try:
        
        
        input_text = message.text.lower()
    

        if "t.me/" in input_text:
            username = "@" + input_text.split("t.me/")[1].split("/")[0].strip()
        elif input_text.startswith("@"):
            username = input_text
        else:
            await message.reply("❌ Неверный формат. Пример:\n@channel_name\nhttps://t.me/channel_name")
            await state.clear()
            return
        print(f"username is {username}")

        chat = await bot.get_chat(username)
        
        if chat.type != "channel":
            await message.reply("❌ Это не канал!")
            await state.clear()
            return

        admins = await chat.get_administrators()
        if not any(admin.user.id == bot.id for admin in admins):
            await message.reply("⚠️ Бот не администратор канала!")
            await state.clear()
            return
        
        await message.reply(
            f"✅ ID: <code>{chat.id}</code>\n"
            f"👥 Название: {chat.title}\n"
            f"📝 Описание: {chat.description}"
            f"📝 проверка: {chat.linked_chat_id}", 
            parse_mode="HTML"
        )
        
        await state.clear()

    except Exception as e:
        await message.reply(f"❌ Ошибка: {str(e)}")
        await state.clear()


@base_router.message(Command('about'))
async def cmd_about(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Русский', callback_data='lang_ru'),
         InlineKeyboardButton(text='English', callback_data='lang_en')]
    ])
    await message.answer(description, reply_markup=keyboard)
    
@base_router.callback_query(lambda c: c.data in ['lang_ru', 'lang_en'])
async def process_language_switch(callback_query: CallbackQuery):
    if callback_query.data == 'lang_ru':
        await callback_query.answer("Вы выбрали русский язык.")
    elif callback_query.data == 'lang_en':
        await callback_query.answer("You selected English.")

