from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio
import app.database.requests as rq

async def scheduler(next_spin, bot, tg_id):
    scheduler = AsyncIOScheduler()
    
    loop = asyncio.get_running_loop()  # Получаем активный event loop

    scheduler.add_job(
        lambda: asyncio.run_coroutine_threadsafe(add_spin_and_send_notification(tg_id, bot), loop),  # ✅ Запускаем в работающем event loop
        'date',
        run_date=next_spin
    )

    scheduler.start()  # Запускаем планировщик

async def add_spin_and_send_notification(tg_id, bot):
    three_spins_check_before = await rq.three_spins_check(tg_id)
    if three_spins_check_before == True:
        await rq.spins_add(tg_id)
        three_spins_check_after = await rq.three_spins_check(tg_id)
        if three_spins_check_after == True:
            next_spin = await rq.next_spin(tg_id)
            await scheduler(next_spin, bot, tg_id)
        else:
            await bot.send_message(tg_id, "⏰ Наши скауты нашли три Свободних агента👤\n\nНужно принять решения по этим игрокам!")


        