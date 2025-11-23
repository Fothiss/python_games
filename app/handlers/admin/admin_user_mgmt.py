from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from database.engine import SessionLocal
from repositories import UserRepository, GameSessionRepository, RatingRepository
from app.config import config

router = Router()

@router.message(Command("user_info"))
async def user_info(message: types.Message, command: CommandObject):
    """Информация о пользователе по ID"""
    if not command.args:
        await message.answer(
            "👤 <b>Информация о пользователе</b>\n\n"
            "Использование: <code>/user_info &lt;user_id&gt;</code>\n"
            "Где <code>&lt;user_id&gt;</code> - ID пользователя в системе\n\n"
            "💡 <b>Пример:</b>\n"
            "<code>/user_info 1</code>\n\n"
            "🔍 <b>Как найти user_id?</b>\n"
            "Используйте <code>/admins_list</code> или <code>/user_info</code> с telegram_id"
        )
        return
    
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        
        # Пытаемся найти пользователя по ID
        try:
            user_id = int(command.args.strip())
        except ValueError:
            await message.answer("❌ user_id должен быть числом")
            return
        
        user = user_repo.get_user_by_id(user_id)
        
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Формируем информацию о пользователе
        status_emoji = "🔴" if user.is_blocked else "🟢"
        status_text = "Заблокирован" if user.is_blocked else "Активен"
        
        user_info_text = (
            f"👤 <b>Информация о пользователе</b>\n\n"
            f"{status_emoji} <b>Статус:</b> {status_text}\n"
            f"🆔 <b>ID в системе:</b> <code>{user.id}</code>\n"
            f"📱 <b>Telegram ID:</b> <code>{user.telegram_id}</code>\n"
            f"👤 <b>Имя:</b> {user.first_name}\n"
        )
        
        if user.last_name:
            user_info_text += f"📛 <b>Фамилия:</b> {user.last_name}\n"
        
        if user.username:
            user_info_text += f"🔗 <b>Username:</b> @{user.username}\n"
        
        user_info_text += (
            f"🌐 <b>Язык:</b> {user.language_code}\n"
            f"📅 <b>Регистрация:</b> {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        )
        
        if user.is_blocked and user.block_reason:
            user_info_text += f"🚫 <b>Причина блокировки:</b> {user.block_reason}\n"
        
        user_info_text += f"\n📊 <b>Подробная статистика:</b>\n<code>/user_stats {user.id}</code>"
        
        await message.answer(user_info_text)
        
    except Exception as e:
        print(f"❌ Ошибка при получении информации о пользователе: {e}")
        await message.answer("❌ Ошибка при получении информации о пользователе")
    finally:
        db.close()

@router.message(Command("user_stats"))
async def user_stats(message: types.Message, command: CommandObject):
    """Статистика пользователя по играм"""
    if not command.args:
        await message.answer(
            "📊 <b>Статистика пользователя</b>\n\n"
            "Использование: <code>/user_stats &lt;user_id&gt;</code>\n"
            "Где <code>&lt;user_id&gt;</code> - ID пользователя в системе\n\n"
            "💡 <b>Пример:</b>\n"
            "<code>/user_stats 1</code>"
        )
        return
    
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        rating_repo = RatingRepository(db)
        
        # Пытаемся найти пользователя по ID
        try:
            user_id = int(command.args.strip())
        except ValueError:
            await message.answer("❌ user_id должен быть числом")
            return
        
        user = user_repo.get_user_by_id(user_id)
        
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Получаем статистику пользователя
        user_stats_data = user_repo.get_user_stats(user_id)
        ratings = rating_repo.get_user_ratings(user_id)
        
        # Формируем статистику
        stats_text = (
            f"📊 <b>Статистика пользователя</b>\n"
            f"👤 <b>{user.first_name}</b> (ID: {user.id})\n\n"
            
            f"🎮 <b>Общая игровая статистика:</b>\n"
            f"• Всего игр: <b>{user_stats_data['total_games']}</b>\n"
            f"• Завершено: <b>{user_stats_data['completed_games']}</b>\n"
        )
        
        if user_stats_data['total_games'] > 0:
            completion_rate = user_stats_data['completion_rate']
            stats_text += f"• Процент завершения: <b>{completion_rate:.1f}%</b>\n\n"
        else:
            stats_text += "\n"
        
        # Рейтинги по играм
        if ratings:
            stats_text += "🏆 <b>Рейтинги по играм:</b>\n"
            for rating, game in ratings:  # ← РАСПАКОВЫВАЕМ КОРТЕЖ
                stats_text += (
                    f"• {game.name}: "  # ← используем game из кортежа
                    f"<b>{rating.best_score}</b> (лучший), "
                    f"<b>{rating.average_score:.1f}</b> (средний)\n"
                )
        else:
            stats_text += "📝 Пользователь еще не играл в игры\n"
        
        await message.answer(stats_text)
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики пользователя: {e}")
        await message.answer("❌ Ошибка при получении статистики пользователя")
    finally:
        db.close()

@router.message(Command("user_ban"))
async def user_ban(message: types.Message, command: CommandObject):
    """Блокировка пользователя"""
    if not command.args:
        await message.answer(
            "🚫 <b>Блокировка пользователя</b>\n\n"
            "Использование: <code>/user_ban &lt;user_id&gt; &lt;причина&gt;</code>\n\n"
            "💡 <b>Пример:</b>\n"
            "<code>/user_ban 1 Спам в чате</code>\n\n"
            "🔍 <b>Как найти user_id?</b>\n"
            "Используйте <code>/user_info &lt;user_id&gt;</code>"
        )
        return
    
    # Разделяем аргументы: первый - user_id, остальное - причина
    args = command.args.split(' ', 1)
    if len(args) < 2:
        await message.answer("❌ Укажите user_id и причину блокировки")
        return
    
    try:
        user_id = int(args[0])
        reason = args[1].strip()
    except ValueError:
        await message.answer("❌ user_id должен быть числом")
        return
    
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        
        # Проверяем существование пользователя
        user = user_repo.get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Проверяем, не заблокирован ли уже
        if user.is_blocked:
            await message.answer("❌ Пользователь уже заблокирован")
            return
        
        # Блокируем пользователя
        success = user_repo.block_user(user_id, reason)
        
        if success:
            await message.answer(
                f"✅ <b>Пользователь заблокирован</b>\n\n"
                f"👤 Пользователь: {user.first_name} (ID: {user.id})\n"
                f"🚫 Причина: {reason}\n\n"
                f"💡 Для разблокировки используйте:\n"
                f"<code>/user_unban {user.id}</code>"
            )
        else:
            await message.answer("❌ Ошибка при блокировке пользователя")
            
    except Exception as e:
        print(f"❌ Ошибка при блокировке пользователя: {e}")
        await message.answer("❌ Ошибка при блокировке пользователя")
    finally:
        db.close()

@router.message(Command("user_unban"))
async def user_unban(message: types.Message, command: CommandObject):
    """Разблокировать пользователя"""
    if not command.args:
        await message.answer(
            "🟢 <b>Разблокировка пользователя</b>\n\n"
            "Использование: <code>/user_unban &lt;user_id&gt;</code>\n"
            "Где <code>&lt;user_id&gt;</code> - ID пользователя в системе\n\n"
            "💡 <b>Пример:</b>\n"
            "<code>/user_unban 1</code>"
        )
        return
    
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        
        # Пытаемся найти пользователя по ID
        try:
            user_id = int(command.args.strip())
        except ValueError:
            await message.answer("❌ user_id должен быть числом")
            return
        
        user = user_repo.get_user_by_id(user_id)
        
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Проверяем, заблокирован ли пользователь
        if not user.is_blocked:
            await message.answer("✅ Пользователь не заблокирован")
            return
        
        # Разблокируем пользователя
        success = user_repo.unblock_user(user_id)
        
        if success:
            await message.answer(
                f"✅ <b>Пользователь разблокирован</b>\n\n"
                f"👤 Пользователь: {user.first_name} (ID: {user.id})\n"
                f"🟢 Статус: Активен\n\n"
                f"💡 Пользователь снова может использовать бота"
            )
        else:
            await message.answer("❌ Ошибка при разблокировке пользователя")
            
    except Exception as e:
        print(f"❌ Ошибка при разблокировке пользователя: {e}")
        await message.answer("❌ Ошибка при разблокировке пользователя")
    finally:
        db.close()