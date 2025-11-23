from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "ℹ️ <b>Помощь по боту</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/start - начать работу\n"
        "/profile - твой профиль и статистика\n"
        "/games - список доступных игр\n"
        "/help - эта справка\n\n"
        "<b>Игры:</b>\n"
        "/guess_number - Угадай число! \n"
        "/quiz - Викторина \n"
        "/cities - Города \n"
    )