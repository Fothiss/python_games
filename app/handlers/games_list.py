from aiogram import Router, types
from aiogram.filters import Command
from database.engine import SessionLocal
from repositories import GameRepository

router = Router()

# Обработчик команды /games
@router.message(Command("games"))
async def cmd_games(message: types.Message):
    """Показывает список доступных игр"""
    db = SessionLocal()
    try:
        game_repo = GameRepository(db)
        games = game_repo.get_active_games()
        
        if not games:
            await message.answer("🎮 Игры пока в разработке... Скоро появятся!")
            return
        
        # ФОРМИРУЕМ КРАСИВЫЙ СПИСОК ИГР
        games_list = []
        for game in games:
            status = "🟢 Доступна" if game.is_active else "🔴 Недоступна"
            games_list.append(
                f"{status} <b>{game.name}</b>\n"
                f"   📝 {game.description}\n"
                f"   🎮 Команда: /{game.code}\n"
            )
        
        games_text = "\n".join(games_list)
        
        await message.answer(
            f"🎮 <b>Доступные игры</b>\n\n"
            f"{games_text}\n"
            f"📈 <b>Посмотреть статистику:</b> /profile\n"
            f"⚡ <b>Скоро:</b> Викторина, Города и другие игры!"
        )
        
    except Exception as e:
        print(f"❌ Ошибка при обработке /games: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()