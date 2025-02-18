from typing import Any, Dict
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import ADMINS as ADMINS

from app.handlers.admin.admin_card_adding import find_best_match as find_best_match


import app.keyboards as kb
import app.database.requests as rq
import app.dictionary as dic

router = Router()

class Reg(StatesGroup):
    search_options = State()
    search_ID_full_name = State()
    search_approximately_name = State()



async def update_and_send_card_info_callback(callback: CallbackQuery, state: FSMContext, card):
    """Обновляет данные карты и отправляет сообщение с информацией о карте."""
    await state.update_data(card=card)
    nationality = await rq.get_nationality_by_id(card.nationality_id)
    club = await rq.get_club_by_id(card.club_id)
    await callback.message.answer_photo(
        photo=card.file_id, 
        caption=f'Карта найдена ✅\n\n'
                f'👤 Имя: {card.name}\n'
                f'🔝 Рейтинг: {card.rating}\n'
                f'🧩 Позиция: {dic.positions[card.position]}\n'
                f'⚽ Клуб: {club.name} (ID: {card.club_id})\n'
                f'🌍 Национальность: {nationality.name} (ID: {card.nationality_id})', 
        reply_markup=kb.options_for_change)
    
async def update_and_send_card_info_message(message: Message, state: FSMContext, card):
    await state.update_data(card=card)
    nationality = await rq.get_nationality_by_id(card.nationality_id)
    club = await rq.get_club_by_id(card.club_id)
    await message.answer_photo(
        photo=card.file_id, 
        caption=f'Карта найдена ✅\n\n'
                f'👤 Имя: {card.name}\n'
                f'🔝 Рейтинг: {card.rating}\n'
                f'🧩 Позиция: {dic.positions[card.position]}\n'
                f'⚽ Клуб: {club.name} (ID: {card.club_id})\n'
                f'🌍 Национальность: {nationality.name} (ID: {card.nationality_id})', 
        reply_markup=kb.options_for_change)

# Редактирование карты
@router.message(F.text == 'Редактировать карту ⚙️', F.from_user.id.in_(ADMINS))
async def card_changing_get_card_id(message: Message, state: FSMContext):
    await state.set_state(Reg.search_options)
    await message.answer("Выберете способ поиска:", reply_markup=kb.search_options)

@router.callback_query(F.data == "ID_full_name", Reg.search_options)
async def search_by_ID_full_name(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("Введите ID карты или полное Имя:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.search_ID_full_name)

@router.message(Reg.search_ID_full_name)
async def card_changing(message: Message, state: FSMContext):
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    card_id_or_name = message.text
    if card_id_or_name.isdecimal():  
        card = await rq.search_card_by_id(card_id_or_name)
    else:
        card = await rq.search_card_by_name(card_id_or_name)
    
    if card:
        # Сохраняем найденную карту в состоянии
        await update_and_send_card_info_message(message, state, card)
    else:
        await message.answer(f"Карта с ID/Именем {card_id_or_name} не найдена ⚠️", reply_markup=kb.admin_menu)



@router.callback_query(F.data == "approximately_name", Reg.search_options)
async def search_by_approximately_name(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.set_state(Reg.search_approximately_name)
    await callback.message.answer("Пожалуйста, введите приблизительное имя:")

@router.message(Reg.search_approximately_name)
async def search_by_approximately_name_check(message: Message, state: FSMContext):
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id -1)
    card_name = message.text.strip()
    existing_names = await rq.get_all_cards_names()
    best_match = await find_best_match(card_name, existing_names)

    if best_match:
        await message.answer(f"Вы имели в виду '{best_match}'?", reply_markup=kb.name_confirmation(best_match))
    else:
        await message.answer("Карточка не найдена. Пожалуйста, введите приблизительное имя снова.")

@router.callback_query(F.data.startswith("nameforsearch_"), Reg.search_approximately_name)
async def search_by_approximately_name_fin(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id) 
    if callback.data == "nameforsearch_again":
        await callback.message.answer("Введите приблизительное имя снова:")
        await callback.answer()
    else:
        card_name = callback.data.split("_")[1]
        card = await rq.search_card_by_name(card_name)
        await update_and_send_card_info_callback(callback, state, card)



# Обработка кнопки "Назад 🚪"
@router.callback_query(F.data == "card_editing_back", Reg.search_options)
@router.callback_query(F.data == "card_editing_back", Reg.search_ID_full_name)
@router.callback_query(F.data == "card_editing_back", Reg.search_approximately_name)
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("...", reply_markup=kb.admin_menu)
    await state.clear()

   