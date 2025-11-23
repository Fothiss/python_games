from aiogram import types, Router
from aiogram.filters import Command, CommandObject

router = Router()

# Обработчик команды /echo
@router.message(Command("echo"))
async def cmd_echo(message: types.Message, command: CommandObject):
    if command.args:
        await message.answer(f"🔊 Эхо: {command.args}")
    else:
        await message.answer(
            "Напиши текст после команды /echo:\n"
            "Пример: <code>/echo Привет мир!</code>"
        )