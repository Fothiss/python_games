from aiogram import Router, types
from aiogram.filters import Command
from database.engine import SessionLocal
from repositories import UserRepository, GameRepository, GameSessionRepository

router = Router()

#Обработчик команды /profile
@router.message(Command("profile"))
async def cmd_profile(message: types.Message):
    """Показывает профиль пользователя с игровой статистикой"""
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        game_repo = GameRepository(db)
        session_repo = GameSessionRepository(db)
        
        user = user_repo.get_user_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используй /start")
            return
        
        # ПОЛУЧАЕМ ВСЕ ДАННЫЕ ДЛЯ СТАТИСТИКИ
        all_games = game_repo.get_all_games()
        user_sessions = session_repo.get_user_sessions(user.id)
        completed_sessions = [s for s in user_sessions if s.completed]
        
        # ОБЩАЯ СТАТИСТИКА
        total_games_played = len(completed_sessions)
        total_score = sum(session.score for session in completed_sessions)
        best_score_overall = max((session.score for session in completed_sessions), default=0)
        
        # СТАТИСТИКА ПО КАЖДОЙ ИГРЕ
        game_stats = []
        
        for game in all_games:
            # Находим сессии для этой игры
            game_sessions = [s for s in completed_sessions if s.game_id == game.id]
            
            if game_sessions:
                total_game_score = sum(session.score for session in game_sessions)
                best_game_score = max(session.score for session in game_sessions)
                total_attempts = sum(session.attempts for session in game_sessions)
                games_played = len(game_sessions)
                avg_attempts = total_attempts // games_played if games_played > 0 else 0
                
                game_stats.append({
                    'name': game.name,
                    'games_played': games_played,
                    'total_score': total_game_score,
                    'best_score': best_game_score,
                    'avg_attempts': avg_attempts
                })
        
        # ФОРМИРУЕМ ТЕКСТ СТАТИСТИКИ
        general_stats = (
            f"👤 <b>Твой профиль</b>\n\n"
            f"<b>Основная информация:</b>\n"
            f"• Имя: {user.first_name}\n"
            f"• Username: @{user.username if user.username else 'не указан'}\n"
            f"• ID: <code>{user.id}</code>\n"
            f"• В системе с: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"<b>Общая статистика:</b>\n"
            f"• Всего сыграно игр: {total_games_played}\n"
            f"• Всего очков: {total_score}\n"
            f"• Лучший результат: {best_score_overall}\n"
            f"• Всего сессий: {len(user_sessions)}\n"
        )
        
        # ДОБАВЛЯЕМ СТАТИСТИКУ ПО ИГРАМ
        games_stats_text = ""
        if game_stats:
            games_stats_text = "\n<b>📊 Статистика по играм:</b>\n"
            for stat in game_stats:
                games_stats_text += (
                    f"🎯 <b>{stat['name']}:</b>\n"
                    f"   • Сыграно: {stat['games_played']}\n"
                    f"   • Всего очков: {stat['total_score']}\n"
                    f"   • Лучший результат: {stat['best_score']}\n"
                )
                if stat['avg_attempts'] > 0:
                    games_stats_text += f"   • Средние попытки: {stat['avg_attempts']}\n"
                games_stats_text += "\n"
        else:
            games_stats_text = "\n📝 Ты еще не играл в игры. Начни: /games\n"
        
        # ДОБАВЛЯЕМ ПРОГРЕСС ИЛИ ДОСТИЖЕНИЯ
        achievements_text = ""
        if total_games_played >= 10:
            achievements_text = "🏆 <b>Достижение:</b> Заядлый игрок (10+ игр)\n"
        elif total_games_played >= 5:
            achievements_text = "⭐ <b>Достижение:</b> Активный игрок (5+ игр)\n"
        elif total_games_played > 0:
            achievements_text = "👶 <b>Статус:</b> Начинающий игрок\n"
        
        final_message = (
            f"{general_stats}"
            f"{achievements_text}"
            f"{games_stats_text}"
            f"🎮 <b>Играть:</b> /games"
        )
        
        await message.answer(final_message)
        
    except Exception as e:
        print(f"❌ Ошибка при обработке /profile: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()