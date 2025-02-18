from typing import Any, Dict
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import ADMINS as ADMINS

from app.handlers.admin.admin_card_adding import find_best_match as find_best_match
from app.handlers.admin.admin_card_editing_search import update_and_send_card_info_callback as update_and_send_card_info_callback
from app.handlers.admin.admin_card_editing_search import update_and_send_card_info_message as update_and_send_card_info_message

import app.keyboards as kb
import app.database.requests as rq
import app.dictionary as dic

router = Router()

class Reg(StatesGroup):
    change_name = State()
    change_rating = State()
    change_position = State()
    change_club = State()


# Обработка выбора параметра для редактирования
@router.callback_query(F.data == "edit_name", F.from_user.id.in_(ADMINS))
async def change_name(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await state.update_data(current_state=current_state)
    await state.set_state(Reg.change_name)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("Введите новое имя карты:")

@router.message(Reg.change_name)
async def process_new_name(message: Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    card = data.get("card")
    if card:
        result = await rq.update_card_name(card.id, new_name)  # Обновляем имя карты
        if result == True:
            await message.answer(f"Имя карты обновлено на {new_name}")
            card = await rq.search_card_by_id(card.id)
            await update_and_send_card_info_message(message, state, card)
            current_state = data.get("current_state")
            await state.set_state(current_state)
        else:
            await message.answer(f"Что-то пошло не так...", reply_markup=kb.admin_menu)
            await state.clear()
    


@router.callback_query(F.data == "edit_rating", F.from_user.id.in_(ADMINS))
async def change_rating(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await state.update_data(current_state=current_state)
    await state.set_state(Reg.change_rating)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("Введите новый рейтинг карты (от 1 до 100):")

@router.message(Reg.change_rating)
async def process_new_rating(message: Message, state: FSMContext):
    try:
        new_rating = int(message.text)
        if 1 <= new_rating <= 100:
            data = await state.get_data()
            card = data.get("card")
            if card:
                await rq.update_card_rating(card.id, new_rating)  # Обновляем рейтинг карты
                await message.answer(f"Рейтинг карты обновлен на {new_rating}")
                card = await rq.search_card_by_id(card.id)
                await update_and_send_card_info_message(message, state, card)
                current_state = data.get("current_state")
                await state.set_state(current_state)
        else:
            await message.answer("Рейтинг должен быть от 1 до 100. Попробуйте снова.")
    except ValueError:
        await message.answer("Пожалуйста, введите число. Попробуйте снова.")



@router.callback_query(F.data == "edit_position", F.from_user.id.in_(ADMINS))
async def change_position(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await state.update_data(current_state=current_state)
    await state.set_state(Reg.change_position)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer('Выберете позицию:', reply_markup=kb.positions)

@router.callback_query(F.data.startswith("position_"), Reg.change_position)
async def process_new_position(callback: CallbackQuery, state: FSMContext):
    new_position = callback.data.split("_")[1]
    data = await state.get_data()
    if new_position == "back":
        card = data.get("card")
        await update_and_send_card_info_callback(callback, state, card)
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        current_state = data.get("current_state")
        await state.set_state(current_state)
    else: 
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)   
        card = data.get("card")
        if card:
            await rq.update_card_position(card.id, new_position)  # Обновляем позицию карты
            await callback.message.answer(f"Позиция карты обновлена на {new_position}")
            card = await rq.search_card_by_id(card.id)
            await update_and_send_card_info_callback(callback, state, card)
            current_state = data.get("current_state")
            await state.set_state(current_state)
