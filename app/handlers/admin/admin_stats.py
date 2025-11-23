from aiogram import Router, types
from aiogram.filters import Command
from database.engine import SessionLocal
from repositories import UserRepository, GameSessionRepository, GameRepository, RatingRepository
from datetime import datetime, timedelta

router = Router()

# 2. Статистика
@router.message(Command("admin_stats"))
async def admin_stats(message: types.Message):
    """Общая статистика бота"""
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        session_repo = GameSessionRepository(db)
        
        # Собираем статистику
        total_users = user_repo.get_total_users_count()
        active_today = user_repo.get_active_today_count()
        blocked_users = user_repo.get_blocked_users_count()
        total_games = session_repo.get_total_sessions_count()
        completed_games = session_repo.get_completed_sessions_count()
        
        # Формируем ответ
        stats_text = (
            "📊 <b>Общая статистика бота</b>\n\n"
            
            "👥 <b>Пользователи:</b>\n"
            f"• Всего пользователей: <b>{total_users}</b>\n"
            f"• Активных сегодня: <b>{active_today}</b>\n"
            f"• Заблокированных: <b>{blocked_users}</b>\n\n"
            
            "🎮 <b>Игры:</b>\n"
            f"• Всего сыграно: <b>{total_games}</b>\n"
            f"• Завершено: <b>{completed_games}</b>\n"
        )
        
        if total_games > 0:
            completion_rate = (completed_games / total_games) * 100
            stats_text += f"• Процент завершения: <b>{completion_rate:.1f}%</b>\n\n"
        else:
            stats_text += "\n"
            
        stats_text += (
            "📈 <b>Детальная статистика:</b>\n"
            "/stats_users - по пользователям\n"
            "/stats_games - по играм\n"
            "/stats_daily - за сегодня/неделю"
        )
        
        await message.answer(stats_text)
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
        await message.answer("❌ Ошибка при получении статистики")
    finally:
        db.close()

@router.message(Command("stats_users"))
async def stats_users(message: types.Message):
    """Статистика по пользователям"""
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        session_repo = GameSessionRepository(db)
        
        # Статистика по пользователям
        total_users = user_repo.get_total_users_count()
        active_today = user_repo.get_active_today_count()
        blocked_users = user_repo.get_blocked_users_count()
        
        # Новые пользователи за неделю
        week_ago = datetime.now() - timedelta(days=7)
        new_users_week = user_repo.get_users_since_count(week_ago)
        
        # Самые активные пользователи (топ-5 по количеству игр)
        top_active_users = session_repo.get_most_active_users(limit=5)
        
        users_stats = (
            "👥 <b>Статистика по пользователям</b>\n\n"
            
            "📈 <b>Общее:</b>\n"
            f"• Всего пользователей: <b>{total_users}</b>\n"
            f"• Новых за неделю: <b>{new_users_week}</b>\n"
            f"• Активных сегодня: <b>{active_today}</b>\n"
            f"• Заблокированных: <b>{blocked_users}</b>\n\n"
        )
        
        if top_active_users:
            users_stats += "🏆 <b>Самые активные пользователи:</b>\n"
            for i, (user, game_count) in enumerate(top_active_users, 1):
                users_stats += f"{i}. {user.first_name} - <b>{game_count}</b> игр\n"
        
        await message.answer(users_stats)
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики пользователей: {e}")
        await message.answer("❌ Ошибка при получении статистики")
    finally:
        db.close()

@router.message(Command("stats_games"))
async def stats_games(message: types.Message):
    """Статистика по играм"""
    db = SessionLocal()
    try:
        game_repo = GameRepository(db)
        session_repo = GameSessionRepository(db)
        rating_repo = RatingRepository(db)
        
        games = game_repo.get_all_games()
        
        games_stats = "🎮 <b>Статистика по играм</b>\n\n"
        
        for game in games:
            # Статистика для каждой игры
            game_stat = session_repo.get_game_stats(game.id)
            top_players = rating_repo.get_top_players_by_game(game.id, limit=3)
            
            status = "🟢" if game.is_active else "🔴"
            games_stats += (
                f"{status} <b>{game.name}</b> (<code>{game.code}</code>)\n"
                f"• Сыграно раз: <b>{game_stat['total_sessions']}</b>\n"
                f"• Завершено: <b>{game_stat['completed_sessions']}</b>\n"
            )
            
            if game_stat['total_sessions'] > 0:
                completion_rate = (game_stat['completed_sessions'] / game_stat['total_sessions']) * 100
                games_stats += f"• Процент завершения: <b>{completion_rate:.1f}%</b>\n"
            
            if top_players:
                games_stats += "• Лучшие игроки: "
                top_names = [f"{user.first_name} ({rating.best_score})" for rating, user in top_players[:2]]
                games_stats += ", ".join(top_names) + "\n"
            
            games_stats += "\n"
        
        await message.answer(games_stats)
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики игр: {e}")
        await message.answer("❌ Ошибка при получении статистики")
    finally:
        db.close()

@router.message(Command("stats_daily"))
async def stats_daily(message: types.Message):
    """Статистика за сегодня/неделю"""
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        session_repo = GameSessionRepository(db)
        
        today = datetime.now().date()
        week_ago = datetime.now() - timedelta(days=7)
        
        # Статистика за сегодня
        new_users_today = user_repo.get_users_since_count(today)
        games_today = session_repo.get_sessions_since_count(today)
        active_users_today = user_repo.get_active_today_count()
        
        # Статистика за неделю
        new_users_week = user_repo.get_users_since_count(week_ago)
        games_week = session_repo.get_sessions_since_count(week_ago)
        
        daily_stats = (
            "📅 <b>Статистика за период</b>\n\n"
            
            "🟢 <b>За сегодня:</b>\n"
            f"• Новых пользователей: <b>{new_users_today}</b>\n"
            f"• Сыграно игр: <b>{games_today}</b>\n"
            f"• Активных пользователей: <b>{active_users_today}</b>\n\n"
            
            "📈 <b>За неделю:</b>\n"
            f"• Новых пользователей: <b>{new_users_week}</b>\n"
            f"• Сыграно игр: <b>{games_week}</b>\n"
        )
        
        # Средние значения за день
        if new_users_week > 0:
            avg_daily_users = new_users_week / 7
            avg_daily_games = games_week / 7
            daily_stats += (
                f"• В среднем в день:\n"
                f"  - Пользователей: <b>{avg_daily_users:.1f}</b>\n"
                f"  - Игр: <b>{avg_daily_games:.1f}</b>\n"
            )
        
        await message.answer(daily_stats)
        
    except Exception as e:
        print(f"❌ Ошибка при получении ежедневной статистики: {e}")
        await message.answer("❌ Ошибка при получении статистики")
    finally:
        db.close()