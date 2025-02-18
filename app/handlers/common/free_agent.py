import random
from datetime import datetime
from typing import Any, Dict, Awaitable, Callable
from aiogram import F, Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.scheduler as sc
import app.keyboards as kb
import app.database.requests as rq
import app.dictionary as dic

from app.middlewares import throttled

router = Router()

# Middleware для блокировки ввода
class ConfirmationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        state = data.get('state')
        
        if state:
            current_state = await state.get_state()
            # Блокируем только во время состояния free_agent
            if current_state == Reg.free_agent.state:
                if isinstance(event, CallbackQuery):
                    if event.data not in ["agreement_true", "agreement_false"]:
                        await event.answer("Сначала завершите текущее действие!", show_alert=True)
                        return
                else:
                    await event.answer("Погоди, давай сначала решим что-то с єтим игроком! Предложи контракт 📃 или ответь отказом ❌")
                    return
        return await handler(event, data)

# Регистрация middleware
router.message.middleware(ConfirmationMiddleware())
router.callback_query.middleware(ConfirmationMiddleware())

class Reg(StatesGroup):
    free_agent = State()  # Состояние для блокировки во время подтверждения



@throttled(rate=2)
@router.message(F.text == 'Свободный агент👤')
async def find_free_agent(message: Message, state: FSMContext):
    if await rq.spin_spending(message.from_user.id):
        await state.set_state(Reg.free_agent)  # Устанавливаем состояние блокировки
        result = None
        while result is None:
            print("+1")
            result = await rq.get_random_card()
        card, card_age, card_price, discount = result
        user = await rq.user(message.from_user.id)
        your_cash = user.cash
        await state.update_data(card_name=card.name, card_id=card.id, card_age=card_age, card_price=card_price)
        formatted_price = f"{card_price:,}".replace(",", " ")
        formatted_your_cash = f"{your_cash:,}".replace(",", " ")
        await message.answer_photo(
            photo=card.file_id,
            caption=f"Наши скауты нашли игрока у которого сейчас нет контракта❌📃\n\n"
                    f"👤 Имя: {card.name}\n"
                    f"⏳ Возраст: {card_age} \n"
                    f"🔝 Рейтинг: {card.rating}\n"
                    f"🧩 Позиция на поле: {dic.positions[card.position]}\n\n"
                    f"Агент требует подписной бонус: {formatted_price} 💵 (скидка {dic.discounts[discount]}%) \n\n"
                    f"На счетах нашего клуба сейчас: {formatted_your_cash} 💵\nЧто делаем?",
            reply_markup=kb.agreement
        )
    else:
        now = datetime.now()
        user = await rq.user(message.from_user.id)
        if not user.next_spin > now:
            await rq.spins_add(message.from_user.id)
            await find_free_agent(message, state)
            # await message.answer("А, что? Повтори пожалуйста...")
        else:
            formatted_time = user.next_spin.strftime('%H:%M')
            await message.delete()
            await message.answer(f"Встреча с представителями Свободного агента👤 запланирована на: {formatted_time} ⌛ Не опаздывай!", reply_markup=kb.main)

@router.callback_query(Reg.free_agent, F.data.in_(["agreement_true", "agreement_false"]))
async def handle_agreement(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    card_name = user_data.get('card_name', 'Неизвестно')
    
    if callback.data == 'agreement_true':
        card_id = user_data.get('card_id')
        card_age = user_data.get('card_age')
        card_price = user_data.get('card_price')
        tg_id = callback.from_user.id
        result = await rq.add_card_to_user(tg_id, card_id, card_age, card_price)
        if result == 1:
            response_text = f'Отлично ✅ \n\nТеперь 👤 {card_name} — игрок нашей команды 🥳'
        elif result == 0:
            response_text = f'''Проблемы с документами🤨 \n\nКажется 👤 {card_name} уже зарегестрирован в нашей команде... Что за бардак, как такое вообще могло произойти?! 😑'''
        else:
            response_text = f'''Для подписания 👤 {card_name} нам немного не хватает😥\n\nНужно где-то раздобыть еще {result * -1}💵'''
    else:
        response_text = f'''Согласен 😏 \n\nПусть 👤 {card_name} поищет себе другую команду! Мы кого попало не подписываем ❌'''
    
    await callback.message.edit_reply_markup()
    await callback.message.answer(response_text)
    await state.clear()  # Сбрасываем состояние
    three_spins_check = await rq.three_spins_check(callback.from_user.id)
    if three_spins_check is True:
        next_spin = await rq.next_spin(callback.from_user.id)
        await sc.scheduler(next_spin, callback.bot, callback.from_user.id)
    await callback.answer()