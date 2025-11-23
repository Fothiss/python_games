import random
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import GuessNumberState
from database.engine import SessionLocal
from repositories import UserRepository, GameRepository, GameSessionRepository

router = Router()

@router.message(Command("guess_number"))
async def start_guess_number(message: types.Message, state: FSMContext):
    """Начало игры - команда /guess_number"""
    
    db = SessionLocal()
    try:
        # 1. НАХОДИМ ПОЛЬЗОВАТЕЛЯ В БД
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.answer("❌ Сначала используй /start для регистрации")
            return
        
        # 2. НАХОДИМ ИГРУ В БД
        game_repo = GameRepository(db)
        game = game_repo.get_game_by_code("guess_number")
        
        if not game:
            await message.answer("❌ Игра временно недоступна")
            return
        
        # 3. СОЗДАЕМ ИГРОВУЮ СЕССИЮ
        session_repo = GameSessionRepository(db)
        session = session_repo.create_session(user.id, game.id)
        
        # 4. ГЕНЕРИРУЕМ СЛУЧАЙНОЕ ЧИСЛО
        secret_number = random.randint(1, 100)
        
        # 5. СОХРАНЯЕМ ДАННЫЕ В СОСТОЯНИИ
        await state.update_data(
            secret_number=secret_number,
            attempts=0,
            max_attempts=10,
            session_id=session.id,  # Сохраняем ID сессии
            user_id=user.id,
            game_id=game.id
        )
        
        await state.set_state(GuessNumberState.playing)
        
        await message.answer(
            "🎯 <b>Игра 'Угадай число'</b>\n\n"
            "Я загадал число от 1 до 100.\n"
            "Попробуй угадать его за минимальное количество попыток!\n"
            "У тебя есть 10 попыток.\n\n"
            "Просто напиши число:"
        )
        
    except Exception as e:
        print(f"❌ Ошибка при старте игры: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()

@router.message(GuessNumberState.playing, F.text)
async def process_guess(message: types.Message, state: FSMContext):
    """Обработка попытки угадать число"""
    
    db = SessionLocal()
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        secret_number = data['secret_number']
        attempts = data['attempts'] + 1
        max_attempts = data['max_attempts']
        session_id = data['session_id']
        
        # Проверяем что введено число
        try:
            user_guess = int(message.text)
        except ValueError:
            await message.answer("🔢 Пожалуйста, введите число от 1 до 100!")
            return
        
        # Проверяем диапазон числа
        if user_guess < 1 or user_guess > 100:
            await message.answer("📏 Число должно быть от 1 до 100!")
            return
        
        # Обновляем счетчик попыток
        await state.update_data(attempts=attempts)
        
        # Проверяем угадал ли пользователь
        if user_guess < secret_number:
            await message.answer(f"⬆️ Загаданное число <b>больше</b> чем {user_guess}")
        elif user_guess > secret_number:
            await message.answer(f"⬇️ Загаданное число <b>меньше</b> чем {user_guess}")
        else:
            # ПОБЕДА! Пользователь угадал число
            score = max(10, 100 - attempts * 5)  # Расчет очков
            
            # СОХРАНЯЕМ РЕЗУЛЬТАТЫ В БД
            session_repo = GameSessionRepository(db)
            session_repo.complete_session(session_id, score, attempts)
            
            await message.answer(
                f"🎉 <b>Поздравляю! Ты угадал число {secret_number}!</b>\n\n"
                f"📊 <b>Твои результаты:</b>\n"
                f"• Загаданное число: <code>{secret_number}</code>\n"
                f"• Количество попыток: <code>{attempts}</code>\n"
                f"• Заработано очков: <code>{score}</code>\n\n"
                f"🎯 Сыграть еще раз: /guess_number\n"
                f"📈 Посмотреть статистику: /profile"
            )
            
            # Очищаем состояние игры
            await state.clear()
            return
        
        # Проверяем не закончились ли попытки
        if attempts >= max_attempts:
            # СОХРАНЯЕМ РЕЗУЛЬТАТ ПРОИГРЫША В БД
            session_repo = GameSessionRepository(db)
            session_repo.complete_session(session_id, 0, attempts)  # 0 очков за проигрыш
            
            await message.answer(
                f"💔 К сожалению, попытки закончились!\n"
                f"Загаданное число было: <code>{secret_number}</code>\n\n"
                f"🎯 Попробовать еще раз: /guess_number"
            )
            await state.clear()
            return
        
        # Показываем сколько попыток осталось
        remaining_attempts = max_attempts - attempts
        await message.answer(
            f"🔄 Попытка {attempts}/{max_attempts}\n"
            f"📋 Осталось попыток: {remaining_attempts}\n\n"
            f"Продолжаем угадывать!"
        )
        
    except Exception as e:
        print(f"❌ Ошибка при обработке попытки: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()