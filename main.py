import logging
import asyncio
from aiogram import Bot, Dispatcher

# from app.handlers import router
from config import key
from app.database.models import async_main
from app.middlewares import ThrottlingMiddleware
from app.handlers.common.cmd_start import router as router_common
from app.handlers.admin.admin_main import router as routers_admin


async def main():
    await async_main()
    bot = Bot(token=key)
    dp = Dispatcher()
    dp.message.middleware(ThrottlingMiddleware())
    dp.include_routers(router_common, routers_admin)
    # logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot closed')