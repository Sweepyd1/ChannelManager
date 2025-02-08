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
        input_text = message.text
        await state.update_data(channels=message.text)
        parts = re.split(r'[\s,]+', input_text)
     
        
        valid_channels = []
        errors = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            try:
            
                if "t.me/" in part.lower():
                    username_part = part.split("t.me/")[1].split("/")[0].strip()
                    # print(username_part)
                    username = f"@{username_part}"
                elif part.startswith("@"):
                    username = part.split()[0].strip()
                else:
                    raise ValueError("❌ Неверный формат")
                

                chat = await bot.get_chat(username)
                if chat.type != "channel":
                    raise ValueError("❌ Это не канал")
                

                admins = await chat.get_administrators()
                if not any(admin.user.id == bot.id for admin in admins):
                    raise ValueError("⚠️ Бот не администратор")
                
                valid_channels.append(chat)
                
            except Exception as e:
                errors.append(f"• {part}: {str(e)}")
        

        response = []
        if valid_channels:
            response.append("✅ Успешно обработанные каналы:\n")
            for chat in valid_channels:
                response.append(
                    f"ID: <code>{chat.id}</code>\n"
                    f"Название: {chat.title}\n"
                    f"Описание: {chat.description}\n\n"
                )
            name, channels = await get_state_data(state)
            print(name, channels)
            await db.groups.create_new_group(name, channels,message.from_user.id)
                
        
        if errors:
            response.append("\n❌ Ошибки при обработке:\n")
            response.extend(errors)
        
        if not valid_channels and not errors:
            await message.reply("⚠️ Не найдено валидных ссылок")
        else:
            await message.reply("".join(response), parse_mode="HTML")
        
        await state.clear()
        
    except Exception as e:
        await message.reply(f"❌ Критическая ошибка: {str(e)}")
        await state.clear()
    