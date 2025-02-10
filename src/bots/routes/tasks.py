from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import bot, db, description

from ..states.state import RegistrationStates, NewPostForGroup

tasks = Router()

@tasks.message(Command("newtask"))
async def new_task(message: Message):
    groups = await db.groups.get_my_group(message.from_user.id)
  
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=group.name, 
            callback_data=f"task_{group.id}" 
        )] for group in groups
    ])
    
    await message.answer("Выберите для какой группы будет задача", reply_markup=keyboard)
 
@tasks.callback_query(F.data.startswith("task_"))  
async def handle_group_for_task(callback: types.CallbackQuery, state: FSMContext):
    try:
        group_id = int(callback.data.split("_")[1])
        await state.update_data(group_id=group_id)
        
        text = "Выберите действие для новой задачи..."
        
     
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data=f"create_post_{group_id}")],
            [InlineKeyboardButton(text="⏰ Запланировать", callback_data=f"schedule_{group_id}")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)


@tasks.callback_query(F.data.startswith("create_post_"))  
async def create_post_for_group(callback: types.CallbackQuery, state: FSMContext):
    try:
     
        text = "будет создан пост для группы...Скидывай готовый пост для группы и он будет выложен сразу во все каналы группы"
        await state.set_state(NewPostForGroup.waiting_for_post)
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)

@tasks.message(NewPostForGroup.waiting_for_post)
async def get_post_for_group(message:types.Message, state: FSMContext):
   
    data = await state.get_data()

    group_id = data.get("group_id")
 
    channels = await db.groups.get_channels_for_group(group_id=group_id, user_id=message.from_user.id)
    
    for channel in channels:
        await forward_to_channel(channel_id=channel.telegram_chat_id, user_message=message)
    await state.clear()

async def forward_to_channel(channel_id: str, user_message: types.Message):
    await user_message.copy_to(
        chat_id=channel_id, 
        allow_sending_without_reply=True
    )