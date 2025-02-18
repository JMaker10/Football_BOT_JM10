from typing import Any, Dict
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq
import app.dictionary as dic

from app.middlewares import throttled
from app.handlers.common.my_clube.user_cards_list import router as router_user_cards_list
from app.handlers.common.my_clube.card_search_categories import router as card_search_categories

router = Router()
router.include_routers(router_user_cards_list, card_search_categories)

class Reg(StatesGroup):
    clube_name = State()
    starting_lineup = State()

@throttled(rate=2)
@router.message(F.text == 'Клуб🏟️')
async def my_club(message: Message): 
    user = await rq.user(message.from_user.id)
    if not user:
        await message.answer("❌ Тут такоє дело... Тебя не существует🥲", parse_mode=None)
        return

    full_text = (
        f"🏟️ ФК «{user.username}»\n\n"
        f"💵 Бюджет: {user.cash}\n"
        f"🔄👤 Свободные агенты: {user.spins}\n\n"
    )
    
    await message.answer(full_text, reply_markup=kb.my_clube, parse_mode=None)
    

@router.callback_query(F.data == 'rename')
async def rename(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.clube_name)
    await callback.answer()
    bot_message =await callback.message.answer(f"Введите новое название клуба:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(prev_bot_message=bot_message.message_id)

@router.message(Reg.clube_name)
async def reg_name(message: Message, state: FSMContext):
    length = len(message.text)
    if length > 25:
        await message.delete()
        await message.answer(f"Давай еще раз, но покороче:")
    else:
        await state.update_data(new_name=message.text)
        data = await state.get_data()
        result = await rq.rename(message.from_user.id, data['new_name'])
        await message.delete()
        if result == "success":
            await message.answer(f"Ура...😑\nТеперь клуб назывется ФК «{data['new_name']}».\nНадеюсь вы довольны... А я пошел опять менять вывеску😤", reply_markup=kb.main)
            await state.clear()
        else:
            await message.answer(f"Упс... Что-то пощло не так🥲", reply_markup=kb.main)
            await state.clear()            


@throttled(rate=2)
@router.message(F.text == 'Сосать у шейхов🔞')
async def suck_cash(message: Message):
    await message.delete()
    sucked_cash = await rq.suck_cash(message.from_user.id)
    await message.answer(f"«{dic.suck_cash_message[sucked_cash]}» \n\nНа счет нашего клуба поступило: {sucked_cash} 💵")  

@router.callback_query(F.data == 'suck_cash')
async def suck_cash(callback: CallbackQuery):
    await callback.answer()
    sucked_cash = await rq.suck_cash(callback.from_user.id)
    await callback.message.answer(f"<<{dic.suck_cash_message[sucked_cash]}>> \n\nНа счет нашего клуба поступило: {sucked_cash} 💵")   