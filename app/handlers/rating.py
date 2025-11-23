from aiogram import Router, types
from aiogram.filters import Command
from database.engine import SessionLocal
from repositories import RatingRepository, UserRepository, GameRepository

router = Router()

@router.message(Command("rating"))
async def cmd_rating(message: types.Message):
    """Показывает личный рейтинг пользователя"""
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        rating_repo = RatingRepository(db)
        
        # Находим пользователя
        user = user_repo.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("❌ Сначала используй /start")
            return
        
        # Получаем рейтинги пользователя
        user_ratings = rating_repo.get_user_ratings(user.id)
        
        if not user_ratings:
            await message.answer(
                "📊 <b>Твой рейтинг</b>\n\n"
                "У тебя еще нет сыгранных игр.\n"
                "🎮 Начни играть: /games"
            )
            return
        
        # Получаем общую статистику и глобальный ранг
        user_stats = rating_repo.get_user_stats(user.id)
        global_rank = rating_repo.get_user_global_rank(user.id)
        
        total_score = user_stats.total_score or 0
        total_games = user_stats.total_games or 0
        best_score = user_stats.best_score or 0
        
        # Формируем статистику
        rating_text = (
            f"👤 <b>Рейтинг {user.first_name}</b>\n\n"
            f"🏆 <b>Глобальный ранг:</b> #{global_rank}\n"
            f"📈 <b>Общая статистика:</b>\n"
            f"• Всего очков: {total_score}\n"
            f"• Всего игр: {total_games}\n"
            f"• Лучший результат: {best_score}\n\n"
        )
        
        # Добавляем статистику по играм
        rating_text += "<b>📊 По играм:</b>\n"
        for rating, game in user_ratings:
            medal = "🥇" if rating.best_score >= 90 else "🥈" if rating.best_score >= 70 else "🥉"
            rating_text += (
                f"{medal} <b>{game.name}</b>\n"
                f"   • Очков: {rating.total_score}\n"
                f"   • Игр: {rating.games_played}\n"
                f"   • Лучший: {rating.best_score}\n"
                f"   • Средний: {rating.average_score:.1f}\n\n"
            )
        
        rating_text += "🏅 <b>Топ игроков:</b> /leaderboard"
        
        await message.answer(rating_text)
        
    except Exception as e:
        print(f"❌ Ошибка при обработке /rating: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()

@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: types.Message):
    """Показывает топ игроков"""
    db = SessionLocal()
    try:
        rating_repo = RatingRepository(db)
        game_repo = GameRepository(db)
        
        # Получаем топ-10 игроков
        leaderboard = rating_repo.get_leaderboard(limit=10)
        
        if not leaderboard:
            await message.answer("🏆 <b>Топ игроков</b>\n\nПока никто не играл 😢\n🎮 Стань первым: /games")
            return
        
        leaderboard_text = "🏆 <b>Топ игроков</b>\n\n"
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, row in enumerate(leaderboard):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            
            if len(row) == 4:  # Общий топ (User, total_score, total_games, best_score)
                user, total_score, total_games, best_score = row
                username = f"@{user.username}" if user.username else user.first_name
                
                leaderboard_text += (
                    f"{medal} {username}\n"
                    f"   💎 {total_score} очков | 🎮 {total_games} игр\n"
                )
            else:  # Топ по конкретной игре (Rating, User, Game)
                rating, user, game = row
                username = f"@{user.username}" if user.username else user.first_name
                
                leaderboard_text += (
                    f"{medal} {username}\n"
                    f"   💎 {rating.total_score} очков | 🎮 {rating.games_played} игр\n"
                )
        
        leaderboard_text += "\n📊 <b>Мой рейтинг:</b> /rating\n🎯 <b>Сыграть:</b> /games"
        
        await message.answer(leaderboard_text)
        
    except Exception as e:
        print(f"❌ Ошибка при обработке /leaderboard: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()