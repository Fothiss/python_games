from aiogram import Router, types
from aiogram.filters import Command
from database.engine import SessionLocal
from repositories import UserRepository

router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start с сохранением пользователя в БД"""
    # Создаем сессию БД
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        
        # Сохраняем/находим пользователя
        user = user_repo.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        await message.answer(
            f"👋 Привет, <b>{user.first_name}</b>!\n\n"
            f"🎮 Добро пожаловать в мир мини-игр!\n\n"
            f"<b>Твоя статистика:</b>\n"
            f"• ID в системе: <code>{user.id}</code>\n"
            f"• Зарегистрирован: {user.created_at.strftime('%d.%m.%Y')}\n\n"
            f"<b>Доступные команды:</b>\n"
            f"/start - начать работу\n"
            f"/profile - твой профиль\n" 
            f"/rating - твой рейтинг\n"
            f"/leaderboard - топ игроков\n"
            f"/games - список игр\n"
            f"/help - помощь"
        )
        
    except Exception as e:
        print(f"❌ Ошибка при обработке /start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()