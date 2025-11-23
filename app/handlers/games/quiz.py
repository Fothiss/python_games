import asyncio
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.engine import SessionLocal
from repositories import QuizRepository, GameRepository, GameSessionRepository, RatingRepository, UserRepository
from utils.states import QuizStates

# Создаем роутер
router = Router()

# Система очков по сложности
SCORE_SYSTEM = {
    "easy": 5,
    "medium": 10, 
    "hard": 15
}

class QuizGame:
    """Класс для управления игровой сессией викторины"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.questions = []  # Будем хранить словари с данными вопросов
        self.current_question_index = 0
        self.user_answers = []  # Ответы пользователя [0, 2, 1, ...]
        self.scores = []  # Очки за каждый вопрос
        self.start_time = datetime.now()
        self.total_score = 0
        self.current_timer_task = None  # Для отмены таймера
    
    def add_question(self, question):
        """Добавляет вопрос в игру как словарь"""
        question_data = {
            "id": question.id,
            "question": question.question,
            "option1": question.option1,
            "option2": question.option2,
            "option3": question.option3,
            "option4": question.option4,
            "correct_option": question.correct_option,
            "difficulty": question.difficulty,
            "category": question.category,
            "explanation": question.explanation
        }
        self.questions.append(question_data)
    
    def get_current_question(self):
        """Возвращает текущий вопрос"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def answer_current_question(self, answer_index: int):
        """Обрабатывает ответ на текущий вопрос"""
        current_question = self.get_current_question()
        if not current_question:
            return None
            
        is_correct = (answer_index == current_question["correct_option"] - 1)  # -1 т.к. correct_option 1-4
        
        # Расчет очков
        base_score = SCORE_SYSTEM.get(current_question["difficulty"], 5) if is_correct else 0
        question_score = base_score
        
        self.user_answers.append(answer_index)
        self.scores.append(question_score)
        self.total_score += question_score
        self.current_question_index += 1
        
        return {
            "is_correct": is_correct,
            "correct_answer": current_question["correct_option"] - 1,
            "score": question_score,
            "explanation": current_question["explanation"]
        }
    
    def is_finished(self):
        """Проверяет, завершена ли игра"""
        return self.current_question_index >= len(self.questions)
    
    def get_progress(self):
        """Возвращает прогресс игры"""
        return f"{self.current_question_index + 1}/{len(self.questions)}"


async def cancel_question_timer(quiz_game: QuizGame):
    """Отменяет текущий таймер вопроса"""
    if quiz_game and quiz_game.current_timer_task:
        quiz_game.current_timer_task.cancel()
        quiz_game.current_timer_task = None


async def question_timer(bot: Bot, chat_id: int, message_id: int, state: FSMContext):
    """Таймер для вопроса (10 секунд)"""
    try:
        await asyncio.sleep(10)  # 10 секунд на ответ
        
        # Проверяем, не ответил ли уже пользователь
        current_state = await state.get_state()
        if current_state == QuizStates.waiting_answer:
            data = await state.get_data()
            quiz_game = data.get("quiz_game")
            
            if quiz_game and not quiz_game.is_finished():
                # Время вышло - обрабатываем как неправильный ответ
                quiz_game.answer_current_question(-1)  # -1 = время вышло
                
                # Показываем результат
                question = quiz_game.questions[quiz_game.current_question_index - 1]
                options = [question["option1"], question["option2"], question["option3"], question["option4"]]
                correct_answer = options[question["correct_option"] - 1]
                
                timeout_text = (
                    f"⏰ Время вышло!\n"
                    f"Правильный ответ: {correct_answer}\n"
                    f"💡 {question['explanation']}\n\n"
                    f"➡️ Следующий вопрос через 3 секунды..."
                )
                
                # Обновляем сообщение
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=timeout_text
                )
                
                # Ждем 3 секунды и показываем следующий вопрос
                await asyncio.sleep(3)
                await show_question(bot, chat_id, state)
                
    except asyncio.CancelledError:
        # Таймер был отменен - это нормально
        pass
    except Exception as e:
        print(f"❌ Ошибка в таймере: {e}")


async def show_question(bot: Bot, chat_id: int, state: FSMContext):
    """Показывает текущий вопрос"""
    data = await state.get_data()
    quiz_game = data.get("quiz_game")
    
    if not quiz_game or quiz_game.is_finished():
        await finish_quiz(bot, chat_id, state)
        return
    
    question = quiz_game.get_current_question()
    if not question:
        await finish_quiz(bot, chat_id, state)
        return
    
    # Создаем клавиатуру с вариантами ответов
    builder = InlineKeyboardBuilder()
    options = [question["option1"], question["option2"], question["option3"], question["option4"]]
    
    for i, option in enumerate(options):
        builder.button(text=f"{chr(65+i)}. {option}", callback_data=f"quiz_answer_{i}")
    
    builder.adjust(2)  # 2 кнопки в ряд
    
    progress = quiz_game.get_progress()
    difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(question["difficulty"], "⚪")
    
    question_text = (
        f"🎯 Вопрос {progress} | {difficulty_emoji} {question['difficulty'].upper()}\n\n"
        f"❓ {question['question']}\n\n"
        f"⏱ У вас 10 секунд!\n"
        f"Выберите ответ:"
    )
    
    # Отправляем вопрос
    sent_message = await bot.send_message(chat_id, question_text, reply_markup=builder.as_markup())
    await state.set_state(QuizStates.waiting_answer)
    
    # Запускаем таймер
    quiz_game.current_timer_task = asyncio.create_task(
        question_timer(bot, chat_id, sent_message.message_id, state)
    )


async def finish_quiz(bot: Bot, chat_id: int, state: FSMContext):
    """Завершение викторины и сохранение результатов"""
    data = await state.get_data()
    quiz_game = data.get("quiz_game")
    game_session_id = data.get("game_session_id")
    
    # Отменяем таймер если есть
    if quiz_game:
        await cancel_question_timer(quiz_game)
    
    if not quiz_game:
        await bot.send_message(chat_id, "❌ Ошибка: данные игры не найдены")
        await state.clear()
        return
    
    # Сохраняем результаты в БД
    db = SessionLocal()
    try:
        session_repo = GameSessionRepository(db)
        game_repo = GameRepository(db)
        
        # Получаем игру "Викторина"
        quiz_game_db = game_repo.get_game_by_code("quiz")
        
        # Считаем количество правильных ответов для attempts
        correct_answers = sum(1 for i, answer in enumerate(quiz_game.user_answers) 
                            if answer == quiz_game.questions[i]["correct_option"] - 1)
        
        # Обновляем игровую сессию
        # attempts = количество правильных ответов (успешные "попытки")
        session_repo.complete_session(
            game_session_id, 
            score=quiz_game.total_score,
            attempts=correct_answers
        )
        
        # Формируем текст результата
        result_text = (
            f"🎉 Викторина завершена!\n\n"
            f"📊 Результаты:\n"
            f"✅ Правильных ответов: {correct_answers}/{len(quiz_game.questions)}\n"
            f"🎯 Общий счет: {quiz_game.total_score} очков\n"
            f"🏆 Лучший вопрос: +{max(quiz_game.scores) if quiz_game.scores else 0} очков\n\n"
            f"Спасибо за игру! 🎮"
        )
        
        await bot.send_message(chat_id, result_text)
        
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Ошибка при сохранении результатов: {e}")
    finally:
        db.close()
        await state.clear()


@router.message(Command("quiz"))
async def start_quiz(message: Message, state: FSMContext, bot: Bot):
    """Начало викторины"""
    db = SessionLocal()
    
    # Получаем вопросы из БД
    try:
        quiz_repo = QuizRepository(db)
        game_repo = GameRepository(db)
        user_repo = UserRepository(db)

        user = user_repo.get_user_by_telegram_id(message.from_user.id)

        if not user:
                await message.answer("❌ Сначала используй /start для регистрации")
                return
        
        # Получаем 8 случайных вопросов
        questions = quiz_repo.get_balanced_questions()
        
        if not questions:
            await message.answer("❌ В базе данных нет вопросов для викторины!")
            return
        
        # Создаем игровую сессию
        quiz_game = QuizGame(user.id)
        for question in questions:
            quiz_game.add_question(question)
        
        # Сохраняем в state
        await state.update_data(quiz_game=quiz_game)
        await state.set_state(QuizStates.playing)
        
        # Получаем игру "Викторина" из БД
        quiz_game_db = game_repo.get_game_by_code("quiz")
        
        # Создаем сессию в БД
        session_repo = GameSessionRepository(db)
        game_session = session_repo.create_session(user.id, quiz_game_db.id)
        await state.update_data(game_session_id=game_session.id)
        
        # Показываем первый вопрос
        await show_question(bot, message.chat.id, state)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при запуске викторины: {e}")
    finally:
        db.close()


@router.callback_query(QuizStates.waiting_answer, F.data.startswith("quiz_answer_"))
async def handle_quiz_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка ответа пользователя"""
    answer_index = int(callback.data.split("_")[2])
    
    data = await state.get_data()
    quiz_game = data.get("quiz_game")
    
    # Отменяем таймер перед обработкой ответа
    await cancel_question_timer(quiz_game)
    
    if not quiz_game or quiz_game.is_finished():
        await callback.answer("Игра уже завершена!")
        return
    
    # Обрабатываем ответ
    result = quiz_game.answer_current_question(answer_index)
    
    if not result:
        await callback.answer("Ошибка обработки ответа!")
        return
    
    # Показываем результат
    question = quiz_game.questions[quiz_game.current_question_index - 1]
    options = [question["option1"], question["option2"], question["option3"], question["option4"]]
    
    result_emoji = "✅" if result["is_correct"] else "❌"
    correct_answer = options[result["correct_answer"]]
    
    result_text = (
        f"{result_emoji} {'Правильно!' if result['is_correct'] else 'Неправильно!'}\n"
        f"Правильный ответ: {correct_answer}\n"
        f"💡 {result['explanation']}\n"
        f"🎯 +{result['score']} очков\n\n"
        f"➡️ Следующий вопрос через 3 секунды..."
    )
    
    # Обновляем сообщение с вопросом
    await callback.message.edit_text(result_text)
    await callback.answer()
    
    # Ждем 3 секунды и показываем следующий вопрос
    await asyncio.sleep(3)
    await show_question(bot, callback.message.chat.id, state)