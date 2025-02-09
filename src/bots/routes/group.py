import logging
import re

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import bot, db

from ..states.state import NewGroupState

group_router = Router()



async def get_state_data(state:FSMContext):
    group_data = await state.get_data()
    name = group_data.get("name")
    channels = group_data.get("channels")
    return name, list(channels.split())



    

@group_router.message(Command('newgroup'))
async def create_new_group(message: types.Message, state: FSMContext):
    await message.reply("Придумайте название для вашей группы")
    await state.set_state(NewGroupState.waiting_for_name) 



@group_router.message(NewGroupState.waiting_for_name)
async def get_name_for_group(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(NewGroupState.waiting_for_channel)
    await message.reply("Пришлите каналы которые хотите видеть в группе(присылайте ссылки на каналы через пробел)")


@group_router.message(NewGroupState.waiting_for_channel)
async def get_channels_for_group(message: types.Message, state: FSMContext):
    try:
        input_text = message.text.strip()
        await state.update_data(channels=input_text)
        
        channels, errors = await process_channel_links(input_text)
        
        if channels:
            await save_group_data(state, message.from_user.id, channels)
        
        await send_processing_result(message, channels, errors)
        
    except Exception as e:
        await handle_processing_error(message, e)
    finally:
        await state.clear()


async def process_channel_links(input_text: str) -> tuple[list, list]:
    parts = re.split(r'[\s,]+', input_text)
    valid_channels = []
    errors = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        try:
            chat = await validate_channel_link(part)
            await check_bot_admin(chat)
            valid_channels.append(chat)
        except Exception as e:
            errors.append(f"• {part}: {str(e)}")
    
    return valid_channels, errors

async def validate_channel_link(link: str) -> types.Chat:
    if "t.me/" in link.lower():
        username_part = link.split("t.me/")[1].split("/")[0].strip()
        username = f"@{username_part}"
    elif link.startswith("@"):
        username = link.split()[0].strip()
    else:
        raise ValueError("❌ Неверный формат")

    chat = await bot.get_chat(username)
    if chat.type != "channel":
        raise ValueError("❌ Это не канал")
    
    return chat

async def check_bot_admin(chat: types.Chat):
    admins = await chat.get_administrators()
    if not any(admin.user.id == bot.id for admin in admins):
        raise ValueError("⚠️ Бот не администратор")

async def save_group_data(state: FSMContext, user_id: int, channels: list):
    data = await state.get_data()
    group_name = data.get('name')
    
    channel_ids = [channel.id for channel in channels]
    links = [f"https://t.me/{channel.username}" for channel in channels]
    
    await db.groups.create_new_group(
        group_name=group_name,
        channels_ids=channel_ids,
        links=links,
        user_id=user_id
    )

async def send_processing_result(message: types.Message, channels: list, errors: list):
    response = []
    
    if channels:
        response.append("✅ Успешно обработанные каналы:\n")
        for chat in channels:
            response.append(
                f"ID: <code>{chat.id}</code>\n"
                f"Название: {chat.title}\n"
                f"Описание: {chat.description}\n\n"
            )

    if errors:
        response.append("\n❌ Ошибки при обработке:\n")
        response.extend(errors)

    if not response:
        await message.reply("⚠️ Не найдено валидных ссылок")
    else:
        await message.reply("".join(response), parse_mode="HTML")

async def handle_processing_error(message: types.Message, error: Exception):
    error_message = f"❌ Критическая ошибка: {str(error)}"
    await message.reply(error_message)
    logging.error("Error processing channels", exc_info=error)
    