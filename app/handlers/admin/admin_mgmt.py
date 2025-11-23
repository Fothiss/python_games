from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from database.engine import SessionLocal
from repositories import AdminRepository, UserRepository
from app.config import config

router = Router()

@router.message(Command("admins_list"))
async def admins_list(message: types.Message):
    """Список всех админов"""
    db = SessionLocal()
    try:
        admin_repo = AdminRepository(db)
        user_repo = UserRepository(db)
        
        admin_text = "👑 <b>Список администраторов</b>\n\n"
        
        # Супер-админы из config
        admin_text += "<b>🔐 Супер-админы (из config):</b>\n"
        for user_id in config.ADMIN_IDS:
            user = user_repo.get_user_by_id(user_id)
            if user:
                username = f"@{user.username}" if user.username else user.first_name
                admin_text += f"• {username} (ID: <code>{user.id}</code>) 👑\n"
            else:
                admin_text += f"• ID: <code>{user_id}</code> (пользователь не найден) 👑\n"
        
        # Админы из БД
        db_admins = admin_repo.get_all_admins()
        if db_admins:
            admin_text += "\n<b>👥 Админы из БД:</b>\n"
            for admin, user in db_admins:
                username = f"@{user.username}" if user.username else user.first_name
                admin_text += f"• {username} (ID: <code>{user.id}</code>)\n"
                admin_text += f"  Добавлен: {admin.added_at.strftime('%d.%m.%Y')}\n"
        else:
            admin_text += "\n📝 Админов в БД нет\n"
        
        admin_text += (
            "\n💡 <b>Примечание:</b>\n"
            "• Супер-админы не могут быть удалены\n"
            "• Админы из БД можно удалить командой /admin_remove"
        )
        
        await message.answer(admin_text)
        
    except Exception as e:
        print(f"❌ Ошибка при получении списка админов: {e}")
        await message.answer("❌ Ошибка при получении списка админов")
    finally:
        db.close()

@router.message(Command("admin_add"))
async def admin_add(message: types.Message, command: CommandObject):
    """Добавить админа"""
    if not command.args:
        await message.answer(
            "👥 <b>Добавление администратора</b>\n\n"
            "Использование: <code>/admin_add &lt;user_id&gt;</code>\n"
            "Где <code>&lt;user_id&gt;</code> - ID пользователя в системе\n\n"
            "💡 <b>Пример:</b>\n"
            "<code>/admin_add 1</code>\n\n"
            "🔍 <b>Как найти user_id?</b>\n"
            "Используйте <code>/user_info &lt;user_id&gt;</code>"
        )
        return
    
    db = SessionLocal()
    try:
        user_id = int(command.args.strip())
        
        admin_repo = AdminRepository(db)
        user_repo = UserRepository(db)
        
        # Проверяем существование пользователя
        user = user_repo.get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Проверяем, не супер-админ ли уже
        if user_id in config.ADMIN_IDS:
            await message.answer("❌ Этот пользователь уже супер-админ!")
            return
        
        # Проверяем, не админ ли уже в БД
        if admin_repo.is_admin(user_id):
            await message.answer("❌ Этот пользователь уже администратор!")
            return
        
        # Находим ID добавляющего (того, кто вызывает команду)
        added_by_user = user_repo.get_user_by_telegram_id(message.from_user.id)
        if not added_by_user:
            await message.answer("❌ Ошибка: ваш профиль не найден в системе")
            return
        
        # Добавляем в админы
        admin_repo.add_admin(user_id, added_by_user.id)
        
        await message.answer(
            f"✅ <b>Пользователь добавлен в админы</b>\n\n"
            f"👤 Пользователь: {user.first_name}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"👑 Статус: Администратор\n\n"
            f"💡 Теперь пользователь имеет доступ к админ-панели"
        )
        
    except ValueError:
        await message.answer("❌ user_id должен быть числом")
    except Exception as e:
        error_msg = str(e)
        if "уже является администратором" in error_msg:
            await message.answer("❌ Этот пользователь уже администратор!")
        elif "Пользователь с user_id" in error_msg:
            await message.answer("❌ Пользователь не найден")
        else:
            print(f"❌ Ошибка при добавлении админа: {e}")
            await message.answer("❌ Ошибка при добавлении админа")
    finally:
        db.close()

@router.message(Command("admin_remove"))
async def admin_remove(message: types.Message, command: CommandObject):
    """Удалить админа"""
    if not command.args:
        await message.answer(
            "🗑️ <b>Удаление администратора</b>\n\n"
            "Использование: <code>/admin_remove &lt;user_id&gt;</code>\n"
            "Где <code>&lt;user_id&gt;</code> - ID пользователя в системе\n\n"
            "💡 <b>Пример:</b>\n"
            "<code>/admin_remove 1</code>\n\n"
            "🔍 <b>Как найти user_id?</b>\n"
            "Используйте <code>/admins_list</code> чтобы увидеть всех админов"
        )
        return
    
    db = SessionLocal()
    try:
        admin_repo = AdminRepository(db)
        user_repo = UserRepository(db)
        
        # Пытаемся найти пользователя по ID
        try:
            user_id = int(command.args.strip())
        except ValueError:
            await message.answer("❌ user_id должен быть числом")
            return
        
        # Проверяем, не супер-админ ли это
        if user_id in config.ADMIN_IDS:
            await message.answer("❌ Нельзя удалить супер-админа из конфига!")
            return
        
        user = user_repo.get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Удаляем админа
        success = admin_repo.remove_admin(user_id)
        
        if success:
            await message.answer(
                f"✅ <b>Админ удален</b>\n\n"
                f"👤 Пользователь: {user.first_name}\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"📊 Статус: Обычный пользователь\n\n"
                f"💡 Пользователь больше не имеет доступа к админ-панели"
            )
        else:
            await message.answer("❌ Админ не найден в БД")
            
    except Exception as e:
        print(f"❌ Ошибка при удалении админа: {e}")
        await message.answer("❌ Ошибка при удалении админа")
    finally:
        db.close()