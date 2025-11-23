from aiogram import BaseMiddleware
from database.engine import SessionLocal
from repositories import AdminRepository, UserRepository
from app.config import config

class AdminMiddleware(BaseMiddleware):
    """
    Middleware для проверки прав доступа к админским командам
    """
    
    ADMIN_COMMANDS = [
        '/admin', '/admin_stats', '/stats_users', '/stats_games', '/stats_daily',
        '/user_info', '/user_stats', '/user_ban', '/user_unban', 
        '/games_list', '/game_toggle', '/admins_list', '/admin_add', '/admin_remove'
    ]

    async def __call__(self, handler, event, data):
        if hasattr(event, 'text') and event.text:
            command_parts = event.text.split()
            if command_parts:
                command = command_parts[0].lower()
                
                if any(command.startswith(cmd.lower()) for cmd in self.ADMIN_COMMANDS):
                    telegram_id = event.from_user.id
                    print(f"🔐 Проверка прав админа для telegram_id: {telegram_id}, команда: {command}")
                    
                    db = SessionLocal()
                    try:
                        user_repo = UserRepository(db)
                        admin_repo = AdminRepository(db)
                        
                        # Конвертируем telegram_id → user_id
                        user = user_repo.get_user_by_telegram_id(telegram_id)
                        if not user:
                            print(f"❌ User с telegram_id {telegram_id} не найден в БД")
                            await event.answer("❌ Нет прав доступа к админ-панели")
                            return
                        
                        user_id = user.id
                        print(f"🔁 Конвертация: telegram_id:{telegram_id} → user_id:{user_id}")
                        
                        # 1. Проверяем супер-админов из config (по user_id)
                        if user_id in config.ADMIN_IDS:
                            print(f"✅ Супер-админ user_id:{user_id} прошел проверку")
                            return await handler(event, data)
                        
                        # 2. Проверяем админов в БД (по user_id)
                        if not admin_repo.is_admin(user_id):
                            print(f"❌ User user_id:{user_id} не имеет прав админа")
                            await event.answer("❌ Нет прав доступа к админ-панели")
                            return
                        
                        print(f"✅ Админ из БД user_id:{user_id} прошел проверку")
                        data['admin_repo'] = admin_repo
                        
                    except Exception as e:
                        print(f"❌ Ошибка при проверке прав админа: {e}")
                        await event.answer("❌ Ошибка при проверке прав доступа")
                        return
                    finally:
                        db.close()
        
        return await handler(event, data)