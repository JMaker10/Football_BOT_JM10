from typing import Any, Dict
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.handlers.admin.admin_items_giving import router as router_admin_items_giving
from app.handlers.admin.admin_serch import router as router_admin_serch
from app.handlers.admin.admin_card_adding import router as router_admin_card_adding
from app.handlers.admin.admin_card_editing_search import router as router_admin_card_editing_search
from app.handlers.admin.admin_card_editing_name_rating_position import router as router_admin_card_editing_name_rating_position
from app.handlers.admin.admin_card_editing_club_nationality import router as router_admin_card_editing_club_nationality

from config import ADMINS as ADMINS

import app.keyboards as kb

router = Router()
router.include_routers(
    router_admin_items_giving, 
    router_admin_serch, 
    router_admin_card_adding, 
    router_admin_card_editing_search, 
    router_admin_card_editing_name_rating_position, 
    router_admin_card_editing_club_nationality
)

@router.message(F.text == '/admin', F.from_user.id.in_(ADMINS))
async def admin_mode(message: Message, state: FSMContext):
    await message.answer('Приветствую адми!\nТы обрел силу которая даже не снилась твоему отцу 😎', reply_markup=kb.main_admin)
    await state.clear()

@router.message(F.text == 'Админ меню😎', F.from_user.id.in_(ADMINS))
async def admin_menu(message: Message):
    await message.delete()
    await message.answer("...", reply_markup=kb.admin_menu)

@router.message(F.text == 'Назад 🚪', F.from_user.id.in_(ADMINS))
async def back_to_main_menu(message: Message):
    await message.answer("С возвращением в мир смертных😎", reply_markup=kb.main_admin)