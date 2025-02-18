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
    giving = State()
    giving_spins = State()
    giving_cash = State()
    giving_card = State()
    giving_card_age = State()



#ВЫДАЧА
@router.message(F.text == 'Выдача 📩', F.from_user.id.in_(ADMINS))
async def giving_start(message: Message, state: FSMContext):
    await state.set_state(Reg.giving)
    await message.delete()
    bot_message = await message.answer("Ведите ID пользователя:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)

@router.message(Reg.giving)
async def giving_get_id(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if 'prev_bot_message' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
        except Exception:
            pass  # Якщо повідомлення вже видалене або не існує    
    try:
        user_id = int(message.text)
        print(f"ID введен пользователем: {user_id}")
    except:
        await message.answer("Введи цыфры.", reply_markup=kb.admin_menu)
    
    user_id = message.text
    print(f"Повторная инициализация: {user_id}")
    user = await rq.user(user_id)
    print(f"Через тг айди нашли игрока: {user}")

    if user:
        await state.update_data(user_id=user.tg_id)
        await message.answer(f"Выбери что выдать пользователю с ТG ID {user.tg_id}", reply_markup=kb.admin_values)
    else:
        await message.answer("Пользователь не найден", reply_markup=kb.admin_menu)
        await state.clear()



#КРУТКИ
@router.callback_query(F.data.in_(["giving_spins"]))
async def giving_spins(callback: CallbackQuery, state: FSMContext):  
    await state.set_state(Reg.giving_spins)
    await callback.answer()
    bot_message = await callback.message.answer("Ведите количество:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)

@router.message(Reg.giving_spins)
async def giving_spins_finish(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if 'prev_bot_message' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
        except Exception:
            pass  # Якщо повідомлення вже видалене або не існує        
    user_id = data.get("user_id")  # Получаем user_id из состояния
    spins_amount = 0
    try:
        spins_amount = int(message.text)
    except:
        pass
    await rq.add_some_spins(user_id, spins_amount)



#ДЕНЬГИ
@router.callback_query(F.data.in_(["giving_cash"]))
async def giving_spins(callback: CallbackQuery, state: FSMContext):  
    await state.set_state(Reg.giving_cash)
    await callback.answer()
    bot_message = await callback.message.answer("Ведите количество:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)

@router.message(Reg.giving_cash)
async def giving_cash_finish(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if 'prev_bot_message' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
        except Exception:
            pass  # Якщо повідомлення вже видалене або не існує        
    user_id = data.get("user_id")  # Получаем user_id из состояния
    cash_amount = 0
    try:
        cash_amount = int(message.text)
    except:
        pass
    await rq.add_some_cash(user_id, cash_amount)



#КАРТЫ
@router.callback_query(F.data.in_(["giving_card"]))
async def giving_card(callback: CallbackQuery, state: FSMContext):  
    await state.set_state(Reg.giving_card)
    await callback.answer()
    bot_message = await callback.message.answer("Веди ID карточки:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)
    

@router.message(Reg.giving_card)
async def giving_card_age(message: Message, state: FSMContext):
    await state.update_data(card_id=message.text)
    await message.delete()
    data = await state.get_data()
    if 'prev_bot_message' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
        except Exception:
            pass  # Якщо повідомлення вже видалене або не існує        
    bot_message = await message.answer("Напиши возраст карточки:")
    await state.update_data(prev_bot_message=bot_message.message_id)
    await state.set_state(Reg.giving_card_age)

@router.message(Reg.giving_card_age)
async def giving_card_finish(message: Message, state: FSMContext):    
    data = await state.get_data()
    if 'prev_bot_message' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
        except Exception:
            pass  # Якщо повідомлення вже видалене або не існує     
    card_age = int(message.text)
    await message.delete()
    card_id = data.get("card_id")
    user_id = data.get("user_id")
    await rq.add_card_to_user_admin(user_id, card_id, card_age)

#НАЗАД
@router.callback_query(F.data.in_(["giving_back"]))
async def giving_back(callback: CallbackQuery, state: FSMContext):
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await callback.message.answer("Продолжим...", reply_markup=kb.admin_menu)
        await state.clear()
