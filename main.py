import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv


load_dotenv()

# Турнир требует postgres. Без него бот работает только на мьют.
ENABLE_TOURNAMENT = os.getenv("ENABLE_TOURNAMENT", "false").lower() in ("1", "true", "yes")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()

    if ENABLE_TOURNAMENT:
        # импорт внутри условия: модуль турнира тянет за собой подключение к базе
        from backend.tg.handlers import router as tournament_router
        dp.include_router(tournament_router)
        logging.info("Турнир включён")
    else:
        logging.info("Турнир выключен, работает только мьют")

    from backend.tg.mute import router as mute_router
    dp.include_router(mute_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
