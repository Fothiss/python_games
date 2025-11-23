import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import config
from database import setup_database

# Middleware
from app.middlewares.admin import AdminMiddleware

from app.handlers import all_routers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Инициализация бота и диспетчера
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Регистрируем middleware
dp.message.middleware(AdminMiddleware())

# Регистрируем роутеры
for router in all_routers:
    dp.include_router(router)

async def setup_bot_commands(bot: Bot):
    """Настраиваем меню команд бота"""
    commands = [
        BotCommand(command="/start", description="🚀 Начать работу"),
        BotCommand(command="/profile", description="👤 Мой профиль"),
        BotCommand(command="/games", description="🎮 Список игр"),
        BotCommand(command="/guess_number", description="🎯 Угадай число"),
        BotCommand(command="/quiz", description="🧠 Викторина"),
        BotCommand(command="/rating", description="📊 Мой рейтинг"),
        BotCommand(command="/leaderboard", description="🏆 Топ игроков"),
        BotCommand(command="/help", description="ℹ️ Помощь"),
    ]
    
    await bot.set_my_commands(commands)
    print("✅ Меню команд настроено!")


async def main():
    try:
        print("🤖 Запускаем бота...")
        
        # Инициализируем БД
        setup_database()
        
        # Проверяем подключение
        bot_info = await bot.get_me()
        print(f"✅ Бот @{bot_info.username} успешно подключен!")
        
        await setup_bot_commands(bot)

        # Запускаем
        print("🔄 Бот запущен и готов к работе!")
        print("👑 Админ-панель активирована")
        print("🎮 Доступные игры: Угадай число, Викторина")
        await dp.start_polling(bot)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())