from typing import Any, Dict
from rapidfuzz import process
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
    search_options = State()
    change_club = State()
    change_nationality = State()
    edit_file_id = State()
    edit_delete_card = State()


@router.callback_query(F.data == "edit_club", F.from_user.id.in_(ADMINS))
async def change_club(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    current_state = await state.get_state()
    await state.update_data(current_state=current_state)
    await state.set_state(Reg.change_club)
    await callback.message.answer("Введите название нового клуба:")

@router.message(Reg.change_club)
async def process_new_club(message: Message, state: FSMContext):
    club_name = message.text.strip()
    existing_clubs = await rq.get_all_clubs()  # Получаем список клубов из БД
    best_match = await find_best_match(club_name, existing_clubs)

    if best_match:
        await message.answer(f"Вы имели в виду '{best_match}'?", reply_markup=kb.club_confirmation(best_match))
    else:
        await message.answer("Клуб не найден. Пожалуйста, введите название клуба снова.")

@router.callback_query(F.data.startswith("club_"), Reg.change_club)
async def new_club_add(callback: CallbackQuery, state: FSMContext): 
    if callback.data == "club_again":
        await callback.message.answer("Введите название клуба снова:")
        await callback.answer()
    else:
        club_name = callback.data.split("_")[1]
        new_club = await rq.get_club_by_name(club_name)
    data = await state.get_data()
    card = data.get("card")
    if card:
        await rq.update_card_club(card.id, new_club)  # Обновляем клуб карты
        await callback.answer(f"Клуб карты обновлен.")
        card = await rq.search_card_by_id(card.id)
        await update_and_send_card_info_callback(callback, state, card)
        current_state = data.get("current_state")
        await state.set_state(current_state)



@router.callback_query(F.data == "edit_nationality", F.from_user.id.in_(ADMINS))
async def change_nationality(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await state.update_data(current_state=current_state)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.set_state(Reg.change_nationality)
    await callback.message.answer("Введите новую национальность:")

@router.message(Reg.change_nationality)
async def process_new_club(message: Message, state: FSMContext):
    new_nationality = message.text.strip()
    existing_nationalities = await rq.get_all_nationalities()
    best_match = await find_best_match(new_nationality, existing_nationalities)

    if best_match:
        await message.answer(f"Вы имели в виду '{best_match}'?", reply_markup=kb.nationality_confirmation(best_match))
    else:
        await message.answer("Национальность не найдена. Пожалуйста, введите национальность снова.")

@router.callback_query(F.data.startswith("nationality_"), Reg.change_nationality)
async def new_club_add(callback: CallbackQuery, state: FSMContext): 
    if callback.data == "nationality_again":
        await callback.message.answer("Введите национальность снова:")
        await callback.answer()
    else:
        nationality_name = callback.data.split("_")[1]
        new_nationality = await rq.get_nationality_by_name(nationality_name)
    data = await state.get_data()
    card = data.get("card")
    if card:
        await rq.update_card_nationality(card.id, new_nationality)  # Обновляем клуб карты
        await callback.answer(f"Клуб карты обновлен.")
        card = await rq.search_card_by_id(card.id)
        await update_and_send_card_info_callback(callback, state, card)
        current_state = data.get("current_state")
        await state.set_state(current_state)



@router.callback_query(F.data == "edit_file_id", F.from_user.id.in_(ADMINS))
async def edit_file_id(callback: CallbackQuery, state: FSMContext): 
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    current_state = await state.get_state()
    await state.update_data(current_state=current_state)
    await state.set_state(Reg.edit_file_id)
    await callback.message.answer("Отправьте новую картинку.")

@router.message(Reg.edit_file_id, F.photo)
async def edit_file_id_reg(message: Message, state: FSMContext):
    await message.delete()
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)    
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    card = data.get("card")
    card_id = card.id
    await rq.update_card_file_id(card_id, file_id)
    card = await rq.search_card_by_id(card.id)
    await state.update_data(card=card)
    await update_and_send_card_info_message(message, state, card)
    current_state = data.get("current_state")
    await state.set_state(current_state)



@router.callback_query(F.data == "edit_delete_card", F.from_user.id.in_(ADMINS))
async def edit_delete_card(callback: CallbackQuery, state: FSMContext): 
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    current_state = await state.get_state()
    await state.update_data(current_state=current_state)
    await state.set_state(Reg.edit_delete_card)
    await callback.message.answer("Подтвердите удаление карты", reply_markup=kb.delite_card)

@router.callback_query(F.data.startswith("delite_card_"), Reg.edit_delete_card)
async def edit_delete_card_true_false(callback: CallbackQuery, state: FSMContext): 
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    data = await state.get_data()
    card = data.get("card")
    if callback.data == "delite_card_false":
        await update_and_send_card_info_callback(callback, state, card)
        current_state = data.get("current_state")
        await state.set_state(current_state)
    else:
        card_id = card.id
        await rq.delete_card(card_id)
        await state.set_state(Reg.search_options)
        await callback.message.answer("Карта удалина ✅🗑️", reply_markup=kb.admin_menu)
