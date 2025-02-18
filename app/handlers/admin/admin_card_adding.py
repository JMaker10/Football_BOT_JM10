from typing import Any, Dict
from rapidfuzz import process
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import ADMINS as ADMINS

import app.keyboards as kb
import app.database.requests as rq
import app.dictionary as dic

router = Router()

class Reg(StatesGroup):
    name = State()
    rating = State()
    position = State()
    club = State()
    nationality = State()
    photo = State()

async def find_best_match(user_input: str, choices: list) -> str | None:
    """Находит самый похожий вариант из списка"""
    best_match = process.extractOne(user_input, choices, score_cutoff=60)  # 60% схожести
    return best_match[0] if best_match else None

#Добавление карт
@router.message(F.text == 'Добавить карту ➕', F.from_user.id.in_(ADMINS))
async def add_card_menu(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.delete()
    bot_message = await message.answer('Введите имя карты:', reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)

@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.rating)
    await message.delete()
        # Видаляємо попереднє повідомлення бота (якщо воно є)
    data = await state.get_data()
    if 'prev_bot_message' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
        except Exception:
            pass  # Якщо повідомлення вже видалене або не існує
    bot_message = await message.answer('Введите рейтинг карты (от 1 до 100):', reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)

@router.message(Reg.rating)
async def reg_rating(message: Message, state: FSMContext):
    try:
        rating = int(message.text)
        if 1 <= rating <= 100:
            await state.update_data(rating=rating)
            await state.set_state(Reg.position)
            await message.delete()
            data = await state.get_data()
            if 'prev_bot_message' in data:
                try:
                    await message.bot.delete_message(chat_id=message.chat.id, message_id=data['prev_bot_message'])
                except Exception:
                    pass

            bot_message = await message.answer('Выберете позицию:', reply_markup=kb.positions)
            await state.update_data(prev_bot_message=bot_message.message_id)
        else:
            await message.answer('Рейтинг должен быть от 1 до 100. Попробуйте снова.')
    except ValueError:
        await message.answer('Пожалуйста, введите число. Попробуйте снова.')

@router.callback_query(F.data.startswith("position_"), Reg.position)
async def reg_position(callback: CallbackQuery, state: FSMContext):
    position = callback.data.split("_")[1]  # Отримуємо ім'я після "name_"
    if position == "back":
        pass
    else:
        await state.update_data(position=position)
        await state.set_state(Reg.club)
        data = await state.get_data()
        if 'prev_bot_message' in data:
            try:
                await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=data['prev_bot_message'])
            except Exception:
                pass
        bot_message = await callback.message.answer("Введите название клуба игрока:", reply_markup=ReplyKeyboardRemove())
        await state.update_data(prev_bot_message=bot_message.message_id)
        await callback.answer()

@router.message(Reg.club)
async def reg_club(message: Message, state: FSMContext):
    club_name = message.text.strip()
    existing_clubs = await rq.get_all_clubs()  # Получаем список клубов из БД
    best_match = await find_best_match(club_name, existing_clubs)

    if best_match:
        await message.answer(f"Вы имели в виду '{best_match}'?", reply_markup=kb.club_confirmation(best_match))
    else:
        await message.answer("Клуб не найден. Пожалуйста, введите название клуба снова.")


@router.callback_query(lambda c: c.data.startswith("club_"), Reg.club)
async def club_selection(callback: CallbackQuery, state: FSMContext):
    if callback.data == "club_again":
        await callback.message.answer("Введите название клуба снова:")
        await callback.answer()
    else:
        club_name = callback.data.split("_")[1]
        club = await rq.get_club_by_name(club_name)
        await state.update_data(club=club)
        await state.set_state(Reg.nationality)
        await callback.message.answer("Введите национальность игрока:")
        await callback.answer()

@router.message(Reg.nationality)
async def reg_nationality(message: Message, state: FSMContext):
    nationality_name = message.text.strip()
    existing_nationalities = await rq.get_all_nationalities()  # Получаем список национальностей из БД

    best_match = await find_best_match(nationality_name, existing_nationalities)

    if best_match:
        await message.answer(f"Вы имели в виду '{best_match}'?", reply_markup=kb.nationality_confirmation(best_match))
    else:
        await message.answer("Национальность не найдена. Пожалуйста, введите национальность снова.")


@router.callback_query(lambda c: c.data.startswith("nationality_"), Reg.nationality)
async def nationality_selection(callback: CallbackQuery, state: FSMContext):
    if callback.data == "nationality_again":
        await callback.message.answer("Введите национальность снова:")
        await callback.answer()
    else:
        nationality_name = callback.data.split("_")[1]
        nationality = await rq.get_nationality_by_name(nationality_name)
        await state.update_data(nationality=nationality)
        await state.set_state(Reg.photo)
        await callback.message.answer("Отправьте фото карты:")
        await callback.answer()


@router.message(Reg.photo, F.photo)
async def reg_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    await rq.add_new_card(data['name'], data['rating'], data['position'], file_id, data['club'], data['nationality'])
    await message.delete()

    await message.answer_photo(
        photo=file_id,
        caption=f'Карта добавлена✅\n\n'
                f'👤 Имя: {data["name"]}\n'
                f'🔝 Рейтинг: {data["rating"]}\n'
                f'🧩 Позиция: {dic.positions[data["position"]]}\n'
                f'⚽ Клуб: {data["club"].name} ({data["club"].id})\n'
                f'🌍 Национальность: {data["nationality"].name} ({data["nationality"].id})',
        reply_markup=kb.admin_menu
    )
    await state.clear()
