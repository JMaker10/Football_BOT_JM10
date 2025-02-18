from typing import Any, Dict
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq
import app.dictionary as dic

from app.handlers.common.my_clube.card_search_categories import categories_update as categories_update


router = Router()

class Reg(StatesGroup):
    search_parameters = State()
    search_results = State()

@router.callback_query(F.data == 'user_cards_list')
async def user_cards_list(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await state.clear()
    await state.set_state(Reg.search_parameters)
    await categories_update(callback, state)


@router.callback_query(F.data.startswith("user_card_"), Reg.search_results)
async def user_card_menu(callback: CallbackQuery, state: FSMContext):
    card_id = callback.data.split("_")[2]
    if card_id == "back":
        m_id = callback.message.message_id
        await callback.bot.delete_messages(chat_id=callback.message.chat.id, message_ids=[m_id, m_id-1, m_id-2, m_id-3, m_id-4, m_id-5, m_id-6])        
        await state.update_data(Reg.search_parameters)
        await categories_update(callback, state)
    elif card_id == "empty":
        await callback.answer("Выберите карту")
    else:
        m_id = callback.message.message_id
        await callback.bot.delete_messages(chat_id=callback.message.chat.id, message_ids=[m_id, m_id-1, m_id-2, m_id-3, m_id-4, m_id-5, m_id-6])
        card = await rq.search_card_by_id(card_id)
        user = await rq.user(callback.from_user.id)
        user_card_association = await rq.user_card_association_by_user_card(callback.from_user.id, card_id)
        card_age = user_card_association.card_age
        card_created_at = user_card_association.created_at
        your_cash = user.cash
        penalty_amount = int(int(card.rating) * ((31 - int(card_age)) * 0.2 + 1) * 15)
        await state.update_data(penalty_amount=penalty_amount, card=card)
        formatted_your_cash = f"{your_cash:,}".replace(",", " ")
        formatted_penalty_amount = f"{penalty_amount:,}".replace(",", " ") 
        await callback.message.answer_photo(photo=card.file_id,
                                            caption=f"👤 Имя: {card.name}\n"
                                                    f"⏳ Возраст: {card_age} \n"
                                                    f"🔝 Рейтинг: {card.rating}\n"
                                                    f"🧩 Позиция на поле: {dic.positions[card.position]}\n"
                                                    f"🛬 В клубе: с {card_created_at.strftime('%d.%m.%Y')}\n\n\n"
                                                    f"Досрочное разорвание контракта обойдется в: \n{formatted_penalty_amount} 💵\n\n"
                                                    f"На счетах нашего клуба сейчас: \n{formatted_your_cash} 💵",
            reply_markup=kb.break_contract
        )   

@router.callback_query(F.data == "break_contract_true", Reg.search_results)
async def break_contract_true(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    data = await state.get_data()
    penalty_amount = data.get("penalty_amount")
    formatted_penalty_amount = f"{penalty_amount:,}".replace(",", " ")
    card = data.get("card")
    user = await rq.user(callback.from_user.id)
    await rq.remove_card_from_user(callback.from_user.id, card.id)
    await rq.remove_cash(callback.from_user.id, penalty_amount)
    await callback.message.answer(f"{card.name} покидает расположение клуба 🛫\n"
                                  f"ФК «{user.username}» навсегда останется в его сердце, как и ваши {formatted_penalty_amount} 💵 в его карманах.\n",
                                  reply_markup=kb.break_contract_ok
    )




    
