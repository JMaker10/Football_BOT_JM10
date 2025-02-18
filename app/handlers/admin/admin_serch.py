from typing import Any, Dict
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import ADMINS as ADMINS

import app.keyboards as kb
import app.database.requests as rq

router = Router()

class Reg(StatesGroup):
    serch_tg_id = State()


#ПОИСК по TG id
@router.message(F.text == 'Поиск пользователя по TG ID 🔍', F.from_user.id.in_(ADMINS))
async def user_serch_tg(message: Message, state: FSMContext):
    await state.set_state(Reg.serch_tg_id)
    await message.delete()
    bot_message = await message.answer("Ведите пожалуйста TG ID пользователя 🔍:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)

@router.message(Reg.serch_tg_id)
async def user_serch_tg_get_id(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if 'prev_bot_message' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
        except Exception:
            pass  # Якщо повідомлення вже видалене або не існує    
    try:
        tg_id = int(message.text)
    except:
        tg_id = 0
    user = await rq.user(tg_id)
    if user:
        await message.answer(f"👤 Внутриигровой ID: {user.tg_id}\n👤 Телеграм ID: {user.tg_id}\n\nНазвание клуба: {user.username}\nКрутки (Свободные агенты👤): {user.spins} 🔁\nДениги (финансы): {user.cash} 💵\n\n🕓 Дата выдачи крутки: {user.next_spin.strftime('%d.%m.%Y - %H:%M')}", reply_markup=kb.admin_menu)
        await state.clear()
    else:
        await message.answer("Пользователь не найден", reply_markup=kb.admin_menu)
        await state.clear()
