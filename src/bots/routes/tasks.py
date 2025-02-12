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
from aiogram.utils.media_group import MediaGroupBuilder

from config import bot, db, description

from ..states.state import NewPostForGroup, RegistrationStates, ScheduleNewPostForGroup
from ..utils.AlbumMiddleware import AlbumMiddleware
from config import scheduler
tasks = Router()
tasks.message.middleware(AlbumMiddleware())


@tasks.message(Command("newtask"))
async def new_task(message: Message):
    groups = await db.groups.get_my_group(message.from_user.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=group.name, callback_data=f"task_{group.id}")]
            for group in groups
        ]
    )

    await message.answer(
        "Выберите для какой группы будет задача", reply_markup=keyboard
    )


@tasks.callback_query(F.data.startswith("task_"))
async def handle_group_for_task(callback: types.CallbackQuery, state: FSMContext):
    try:
        group_id = int(callback.data.split("_")[1])
        await state.update_data(group_id=group_id)

        text = "Выберите действие для новой задачи..."

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📝 Создать пост", callback_data=f"create_post_{group_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⏰ Запланировать", callback_data=f"schedule_{group_id}"
                    )
                ],
            ]
        )

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
async def get_post_for_group(
    message: types.Message, state: FSMContext, album: list = None
):
    data = await state.get_data()
    group_id = data.get("group_id")
    channels = await db.groups.get_channels_for_group(
        group_id=group_id, user_id=message.from_user.id
    )

    caption = ""
    if album:
        caption = album[0].caption or ""
    else:
        caption = message.caption or message.text or ""

    for channel in channels:
        try:
            chat_id = channel.telegram_chat_id
            if album:
                media_group = MediaGroupBuilder(caption=caption)
                for msg in album:
                    if msg.photo:
                        file_id = msg.photo[-1].file_id
                        media_group.add_photo(media=file_id)
                    elif msg.video:
                        file_id = msg.video.file_id
                        media_group.add_video(media=file_id)
                    elif msg.document:
                        file_id = msg.document.file_id
                        media_group.add_document(media=file_id)
                await message.bot.send_media_group(
                    chat_id=chat_id, media=media_group.build()
                )
            else:
                if message.photo:
                    await message.bot.send_photo(
                        chat_id=chat_id,
                        photo=message.photo[-1].file_id,
                        caption=caption,
                    )
                elif message.video:
                    await message.bot.send_video(
                        chat_id=chat_id, video=message.video.file_id, caption=caption
                    )
                elif message.document:
                    await message.bot.send_document(
                        chat_id=chat_id,
                        document=message.document.file_id,
                        caption=caption,
                    )
                else:
                    await message.bot.send_message(chat_id=chat_id, text=caption)
        except Exception as e:
            print(f"Ошибка отправки в канал {chat_id}: {e}")

    await state.clear()


###планирование постов
@tasks.callback_query(F.data.startswith("schedule_"))
async def schedule_post_for_froup(callback: types.CallbackQuery, state: FSMContext):
    try:
        text = "будет запланирован пост для группы...Скидывай время"#указать в каком виде кидать время
        await state.set_state(ScheduleNewPostForGroup.waiting_for_date)

        await callback.message.edit_text(text)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)


@tasks.message(ScheduleNewPostForGroup.waiting_for_date)
async def handle_new_schedule_date(
    message: types.Message, state: FSMContext, album: list = None
):
    await state.update_data(date=message.text)
    await state.set_state(ScheduleNewPostForGroup.waiting_for_post)
    await message.answer("окей, теперь пост")


@tasks.message(ScheduleNewPostForGroup.waiting_for_post)
@scheduler.new_scheduler()
async def handle_new_schedule_post(
    message: types.Message, state: FSMContext, album: list = None
):
    data = await state.get_data()
    group_id = data.get("group_id")
    channels = await db.groups.get_channels_for_group(
        group_id=group_id, user_id=message.from_user.id
    )

    caption = ""
    if album:
        caption = album[0].caption or ""
    else:
        caption = message.caption or message.text or ""

    for channel in channels:
        try:
            chat_id = channel.telegram_chat_id
            if album:
                media_group = MediaGroupBuilder(caption=caption)
                for msg in album:
                    if msg.photo:
                        file_id = msg.photo[-1].file_id
                        media_group.add_photo(media=file_id)
                    elif msg.video:
                        file_id = msg.video.file_id
                        media_group.add_video(media=file_id)
                    elif msg.document:
                        file_id = msg.document.file_id
                        media_group.add_document(media=file_id)
                await message.bot.send_media_group(
                    chat_id=chat_id, media=media_group.build()
                )
            else:
                if message.photo:
                    await message.bot.send_photo(
                        chat_id=chat_id,
                        photo=message.photo[-1].file_id,
                        caption=caption,
                    )
                elif message.video:
                    await message.bot.send_video(
                        chat_id=chat_id, video=message.video.file_id, caption=caption
                    )
                elif message.document:
                    await message.bot.send_document(
                        chat_id=chat_id,
                        document=message.document.file_id,
                        caption=caption,
                    )
                else:
                    await message.bot.send_message(chat_id=chat_id, text=caption)
        except Exception as e:
            print(f"Ошибка отправки в канал {chat_id}: {e}")

    await state.clear()
