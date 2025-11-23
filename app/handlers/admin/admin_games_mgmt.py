from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from database.engine import SessionLocal
from repositories import GameRepository

router = Router()

@router.message(Command("games_list"))
async def games_list(message: types.Message):
    """Список всех игр включая выключенные"""
    db = SessionLocal()
    try:
        game_repo = GameRepository(db)
        games = game_repo.get_all_games()
        
        if not games:
            await message.answer("🎮 Список игр пуст")
            return
        
        games_text = "🎮 <b>Список всех игр</b>\n\n"
        
        for game in games:
            status = "🟢 ВКЛ" if game.is_active else "🔴 ВЫКЛ"
            games_text += (
                f"{status} <b>{game.name}</b>\n"
                f"Код: <code>{game.code}</code>\n"
            )
            
            if game.description:
                games_text += f"Описание: {game.description}\n"
            
            games_text += f"Команда: <code>/game_toggle {game.code}</code>\n\n"
        
        games_text += (
            "💡 <b>Как использовать:</b>\n"
            "Чтобы включить/выключить игру, используйте:\n"
            "<code>/game_toggle код_игры</code>\n\n"
            "📝 <b>Пример:</b>\n"
            "<code>/game_toggle guess_number</code>"
        )
        
        await message.answer(games_text)
        
    except Exception as e:
        print(f"❌ Ошибка при получении списка игр: {e}")
        await message.answer("❌ Ошибка при получении списка игр")
    finally:
        db.close()

@router.message(Command("game_toggle"))
async def game_toggle(message: types.Message, command: CommandObject):
    """Включить/выключить игру"""
    if not command.args:
        await message.answer(
            "🔄 <b>Включение/выключение игры</b>\n\n"
            "Использование: <code>/game_toggle &lt;код_игры&gt;</code>\n\n"
            "💡 <b>Доступные коды игр:</b>\n"
            "Используйте <code>/games_list</code> чтобы увидеть все коды игр\n\n"
            "📝 <b>Пример:</b>\n"
            "<code>/game_toggle guess_number</code>"
        )
        return
    
    game_code = command.args.strip().lower()
    
    db = SessionLocal()
    try:
        game_repo = GameRepository(db)
        game = game_repo.get_game_by_code(game_code)
        
        if not game:
            await message.answer(
                f"❌ Игра с кодом <code>{game_code}</code> не найдена\n\n"
                f"💡 Используйте <code>/games_list</code> чтобы увидеть все доступные игры"
            )
            return
        
        # Переключаем статус игры
        success = game_repo.toggle_game(game_code)
        
        if success:
            new_status = "включена" if game.is_active else "выключена"
            status_emoji = "🟢" if game.is_active else "🔴"
            
            await message.answer(
                f"{status_emoji} <b>Игра {new_status}</b>\n\n"
                f"🎮 <b>{game.name}</b>\n"
                f"Код: <code>{game.code}</code>\n"
                f"Статус: <b>{'ВКЛЮЧЕНА' if game.is_active else 'ВЫКЛЮЧЕНА'}</b>\n\n"
                f"💡 Пользователи {'' if game.is_active else 'не'} смогут играть в эту игру"
            )
        else:
            await message.answer("❌ Ошибка при переключении игры")
            
    except Exception as e:
        print(f"❌ Ошибка при переключении игры: {e}")
        await message.answer("❌ Ошибка при переключении игры")
    finally:
        db.close()