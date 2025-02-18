from typing import Any, Dict
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.middlewares import throttled
from app.handlers.common.free_agent import router as router_free_agent
from app.handlers.common.my_clube.my_clube_main import router as router_my_clube_main


import app.keyboards as kb
import app.database.requests as rq
import app.handlers.common.free_agent as fa

router = Router()
router.include_routers(router_free_agent, router_my_clube_main)
router.message.middleware(fa.ConfirmationMiddleware())
router.callback_query.middleware(fa.ConfirmationMiddleware())

@throttled(rate=2)
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await rq.set_user(message.from_user.id)
    await message.answer('Управляй своей командой!\nСобери самый сильный состав и стань чемпионом🥇', reply_markup=kb.main)
    await state.clear()