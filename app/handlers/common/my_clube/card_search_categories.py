from typing import Any, Dict
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import ADMINS
from app.handlers.admin.admin_card_adding import find_best_match
from app.handlers.admin.admin_card_editing_search import update_and_send_card_info_callback

import app.keyboards as kb
import app.database.requests as rq
import app.dictionary as dic

router = Router()

class Reg(StatesGroup):
    search_options = State()
    search_parameters = State()
    search_min_rating = State()
    search_max_rating = State()
    search_club = State()
    search_nationality = State()
    search_results = State()

async def categories_update(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = event.from_user.id
    user_id = await state.update_data(user_id=user_id)

    position = data.get("position") or "-"
    min_rating = data.get("min_rating", 1)
    max_rating = data.get("max_rating", 100)
    club_name = data.get("club_name") or "-"
    nationality_name = data.get("nationality_name") or "-"

    if isinstance(event, CallbackQuery):
        message = event.message
    else:
        message = event

    await message.answer(
        f"Параметры для поиска:\n\n"
        f"🧩 Позиция: {position}\n"
        f"🔝 Рейтинг: {min_rating} - {max_rating}\n"
        f"⚽ Клуб: {club_name}\n"
        f"🌍 Национальность: {nationality_name}\n\n"
        f"Выберите параметр, который нужно изменить 👇",
        reply_markup=kb.search_parameters()
    )

@router.callback_query(F.data == "categories", Reg.search_options)
async def search_by_categories(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("...", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.search_parameters)
    await categories_update(callback, state)

@router.callback_query(F.data == "position", Reg.search_parameters)
async def search_by_categories_position(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("Выберите позицию:", reply_markup=kb.positions)

@router.callback_query(F.data.startswith("position_"), Reg.search_parameters)
async def search_by_categories_position_reg(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    position = callback.data.split("_")[1]
    if position != "back":
        await state.update_data(position=position)
    await categories_update(callback, state)




@router.callback_query(F.data == "min_rating", Reg.search_parameters)
async def search_by_categories_min_rating(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    data = await state.get_data()
    max_rating = data.get("max_rating", 100)
    await callback.message.answer(f"Введите минимальное значение ретинга (от 1 до {max_rating}):")
    await state.set_state(Reg.search_min_rating)

@router.message(Reg.search_min_rating)
async def search_by_categories_min_rating_reg(message: Message, state: FSMContext):  
    min_rating = message.text
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.delete()
    data = await state.get_data()
    max_rating = data.get("max_rating", 100)
    if min_rating.isdigit() and int(min_rating) >= 1 and int(min_rating) <= int(max_rating):
        await state.update_data(min_rating=min_rating)
        await state.set_state(Reg.search_parameters)
        await categories_update(message, state)
    else:
        await message.answer(f"⚠️ Число должно быть от 1 до {max_rating}. Напиши рейтинг еще раз: ")




@router.callback_query(F.data == "max_rating", Reg.search_parameters)
async def search_by_categories_max_rating(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    data = await state.get_data()
    min_rating = data.get("min_rating", 1)
    await callback.message.answer(f"Введите максимальное значение ретинга (от {min_rating} до 100):")
    await state.set_state(Reg.search_max_rating)

@router.message(Reg.search_max_rating)
async def search_by_categories_max_rating_reg(message: Message, state: FSMContext):  
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.delete()
    max_rating = message.text
    data = await state.get_data()
    min_rating = int(data.get("min_rating", 1))
    if max_rating.isdigit() and int(max_rating) >= int(min_rating) and int(max_rating) <= 100:
        await state.update_data(max_rating=max_rating)
        await state.set_state(Reg.search_parameters)
        await categories_update(message, state)
    else:
        await message.answer(f"⚠️ Число должно быть от {min_rating} до 100. Напиши рейтинг еще раз: ")




@router.callback_query(F.data == "club", Reg.search_parameters)
async def search_by_clubs(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.set_state(Reg.search_club)
    countries = await rq.get_all_countries()
    await callback.message.answer("Выберите срану клуба:", reply_markup=kb.countries_buttons(countries))

@router.callback_query(F.data.startswith("countries_"),Reg.search_club)
async def search_by_club(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    country_id = callback.data.split("_")[1]
    if country_id == "back":
        await state.set_state(Reg.search_parameters)
        await categories_update(callback, state)        
    else:
        clubs = await rq.clubs_from_country(country_id)
        await callback.message.answer("Выберите клуб:", reply_markup=kb.clubs_buttons(clubs))

@router.callback_query(F.data.startswith("clubs_"),Reg.search_club)
async def search_by_club_add(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    club_id = callback.data.split("_")[1]
    if club_id == "back":
        countries = await rq.get_all_countries()
        await callback.message.answer("Выберите срану клуба:", reply_markup=kb.countries_buttons(countries))
    else:
        club_name = callback.data.split("_")[2]
        await state.update_data(club_id=club_id, club_name=club_name)
        await state.set_state(Reg.search_parameters)
        await categories_update(callback, state)




@router.callback_query(F.data == "nationality", Reg.search_parameters)
async def search_by_nationality(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer("Напиши нужную национальность:")
    await state.set_state(Reg.search_nationality)

@router.message(Reg.search_nationality)
async def search_by_nationality_check(message: Message, state: FSMContext):  
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.delete()
    nationality = message.text.strip()
    existing_nationalities = await rq.get_all_nationalities()
    best_match = await find_best_match(nationality, existing_nationalities)
    if best_match:
        await message.answer(f"Вы имели в виду '{best_match}'?", reply_markup=kb.nationality_confirmation(best_match))
    else:
        await message.answer("Национальность не найдена. Пожалуйста, введите национальность снова.")

@router.callback_query(F.data.startswith("nationality_"), Reg.search_nationality)
async def search_by_nationality_add(callback: CallbackQuery, state: FSMContext): 
    if callback.data == "nationality_again":
        await callback.message.answer("Введите национальность снова:")
        await callback.answer()
    else:
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)        
        nationality_name = callback.data.split("_")[1]
        nationality = await rq.get_nationality_by_name(nationality_name)
        nationality_id = nationality.id
        await state.update_data(nationality_id=nationality_id, nationality_name=nationality_name)
        await state.set_state(Reg.search_parameters)
        await categories_update(callback, state)


async def update_cards_display(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 1)
    offset = (current_page - 1) * 6  # Вычисляем новый offset для запроса

    cards = await rq.search_user_cards(**data, offset=offset)
    default_file_id = "AgACAgIAAxkBAAIs5mewijWZSY--JhTvHwwLSl2Img-hAAKe8TEbG_iBSd_8nsK-q8V4AQADAgADeQADNgQ"

    num_photos = 6
    file_ids = [card["file_id"] for card in cards]
    while len(file_ids) < num_photos:
        file_ids.append(default_file_id)

    media = [InputMediaPhoto(media=file_ids[i]) for i in range(num_photos)]

    # Удаляем предыдущую медиагруппу
    m_id=callback.message.message_id
    await callback.bot.delete_messages(chat_id=callback.message.chat.id, message_ids=[m_id, m_id-1, m_id-2, m_id-3, m_id-4, m_id-5, m_id-6,])

    # Отправляем новую медиагруппу
    await callback.bot.send_media_group(
        chat_id=callback.message.chat.id,
        media=media
    )

    await callback.message.answer("Выберите карту 👇", reply_markup=kb.cards_buttons(cards, current_page))



@router.callback_query(F.data == "search", Reg.search_parameters)
async def search(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.set_state(Reg.search_results)
    await state.update_data(current_page=1)  # Устанавливаем первую страницу
    data_for_search = await state.get_data()
    cards = await rq.search_user_cards(**data_for_search, offset=0)
    default_file_id = "AgACAgIAAxkBAAIs5mewijWZSY--JhTvHwwLSl2Img-hAAKe8TEbG_iBSd_8nsK-q8V4AQADAgADeQADNgQ"
    num_photos = 6
    file_ids = [card["file_id"] for card in cards]
    while len(file_ids) < num_photos:
        file_ids.append(default_file_id)
    media = [InputMediaPhoto(media=file_ids[i]) for i in range(num_photos)]
    await callback.bot.send_media_group(
        chat_id=callback.message.chat.id,
        media=media
    )
    await callback.message.answer("Выберите карту 👇", reply_markup=kb.cards_buttons(cards))
        

@router.callback_query(F.data == "previous_six", Reg.search_results)
async def previous_cards(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 1)

    if current_page > 1:
        await state.update_data(current_page=current_page - 1)
        await update_cards_display(callback, state)
    else:
        await callback.answer("Вы на первой странице.")
        

@router.callback_query(F.data == "next_six", Reg.search_results)
async def next_cards(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 1)
    
    # Проверяем, есть ли еще карты на следующей странице
    new_offset = current_page * 6
    cards = await rq.search_user_cards(**data, offset=new_offset)

    if cards:
        await state.update_data(current_page=current_page + 1)
        current_page = data.get("current_page", 1)
        await update_cards_display(callback, state)
    else:
        await callback.answer("Это последняя страница.")


@router.callback_query(F.data == "card_editing_back", Reg.search_results)
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    data_for_search = await state.get_data()
    current_page = data_for_search.get("current_page", 1)
    offset = (current_page - 1) * 6
    cards = await rq.search_user_cards(**data_for_search, offset=offset)
    default_file_id = "AgACAgIAAxkBAAIs5mewijWZSY--JhTvHwwLSl2Img-hAAKe8TEbG_iBSd_8nsK-q8V4AQADAgADeQADNgQ"
    # images\Cards\not_found.png
    num_photos = 6
    file_ids = [card["file_id"] for card in cards]
    while len(file_ids) < num_photos:
        file_ids.append(default_file_id)
    media = [InputMediaPhoto(media=file_ids[i]) for i in range(num_photos)]
    await callback.bot.send_media_group(
        chat_id=callback.message.chat.id,
        media=media
    )
    await callback.message.answer("Выберите карту 👇", reply_markup=kb.cards_buttons(cards))    

@router.callback_query(F.data == "clear", Reg.search_parameters)
async def search_clear(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)   
    await state.set_data({})
    await categories_update(callback, state)  


@router.callback_query(F.data == "close_search", Reg.search_parameters)
async def close_search(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)   
    await state.clear()
    user_id = callback.from_user.id
    user = await rq.user(user_id)
    if not user:
        await callback.message.answer("❌ Тут такоє дело... Тебя не существует🥲")
        return

    full_text = (
        f"🏟️ ФК «{user.username}»\n\n"
        f"💵 Бюджет: {user.cash}\n"
        f"🔄👤 Свободные агенты: {user.spins}\n\n"
    )
    
    await callback.message.answer(full_text, reply_markup=kb.my_clube)