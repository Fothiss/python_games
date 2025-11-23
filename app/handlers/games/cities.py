import asyncio
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.engine import SessionLocal
from repositories import CityRepository, GameRepository, GameSessionRepository, UserRepository, RatingRepository
from utils.states import CitiesStates

# Создаем роутер
router = Router()

def normalize_city_name(city_name: str) -> str:
    """Нормализует название города для поиска"""
    return city_name.strip().title()

def get_game_letter(city_name: str) -> str:
    """Определяет игровую букву для следующего города (последняя буква с учетом правил)"""
    # Убираем пробелы и дефисы, переводим в верхний регистр
    clean_city = city_name.replace(' ', '').replace('-', '').upper()
    
    # Идем с конца и ищем первую подходящую букву (игнорируя Ь,Ъ,Ы,Й)
    index = len(clean_city) - 1
    bad_letters = ['Ь', 'Ъ', 'Ы', 'Й']
    
    while index >= 0:
        current_char = clean_city[index]
        if current_char not in bad_letters:
            return current_char
        index -= 1
    
    # Если все буквы "плохие", берем последнюю
    return clean_city[-1]

def get_first_letter(city_name: str) -> str:
    """Получает первую букву города"""
    return city_name.strip()[0].upper() if city_name.strip() else ''

class CitiesGame:
    """Класс для управления игровой сессией в города"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.used_cities = set()      # Использованные города
        self.current_city = None      # Текущий город
        self.user_score = 0           # Счет пользователя
        self.bot_score = 0            # Счет бота
        self.moves_count = 0          # Количество ходов
        self.start_time = datetime.now()
    
    def add_used_city(self, city_name: str):
        """Добавляет город в использованные"""
        normalized_name = normalize_city_name(city_name)
        self.used_cities.add(normalized_name)
    
    def is_city_used(self, city_name: str) -> bool:
        """Проверяет, использовался ли город"""
        normalized_name = normalize_city_name(city_name)
        return normalized_name in self.used_cities
    
    def increment_user_score(self):
        """Увеличивает счет пользователя"""
        self.user_score += 1
        self.moves_count += 1
    
    def increment_bot_score(self):
        """Увеличивает счет бота"""
        self.bot_score += 1
        self.moves_count += 1


async def save_game_results(session_id: int, user_id: int, game_id: int, user_score: int, moves_count: int):
    """Сохранение результатов игры в БД"""
    db = SessionLocal()
    try:
        session_repo = GameSessionRepository(db)
        rating_repo = RatingRepository(db)
        
        # Сохраняем сессию
        session_repo.complete_session(session_id, user_score, moves_count)
        
        # Обновляем рейтинг
        rating_repo.update_rating(user_id, game_id, user_score)
        
    except Exception as e:
        print(f"Ошибка при сохранении результатов: {e}")
    finally:
        db.close()


@router.message(Command("cities"))
async def start_cities(message: Message, state: FSMContext):
    """Начало игры в города"""
    db = SessionLocal()
    
    try:
        city_repo = CityRepository(db)
        game_repo = GameRepository(db)
        user_repo = UserRepository(db)

        user = user_repo.get_user_by_telegram_id(message.from_user.id)

        if not user:
            await message.answer("❌ Сначала используй /start для регистрации")
            return
        
        # Получаем игру "Города" из БД
        cities_game_db = game_repo.get_game_by_code("cities")
        if not cities_game_db:
            await message.answer("❌ Игра 'Города' временно недоступна")
            return
        
        # Создаем игровую сессию
        cities_game = CitiesGame(user.id)
        
        # Получаем случайный город для начала игры
        start_city = city_repo.get_random_start_city()
        if not start_city:
            await message.answer("❌ В базе данных нет городов для игры!")
            return
        
        cities_game.current_city = start_city.name
        cities_game.add_used_city(start_city.name)
        
        # Создаем сессию в БД
        session_repo = GameSessionRepository(db)
        session = session_repo.create_session(user.id, cities_game_db.id)
        
        # Сохраняем в state
        await state.update_data(
            cities_game=cities_game,
            session_id=session.id,
            user_id=user.id,
            game_id=cities_game_db.id
        )
        await state.set_state(CitiesStates.playing)
        
        # Определяем букву для первого хода пользователя
        first_letter = get_game_letter(start_city.name)
        
        # Показываем начало игры
        start_text = (
            f"🏙️ <b>Игра 'Города'</b>\n\n"
            f"📝 <b>Правила:</b>\n"
            f"• Называйте город на последнюю букву предыдущего\n"
            f"• Город должен существовать и не использоваться ранее\n"
            f"• Буквы Ь, Ъ, Ы, Й пропускаются\n"
            f"• Игра до первой ошибки\n\n"
            f"🎮 <b>Начинаю я:</b>\n"
            f"<code>{start_city.name}</code>\n\n"
            f"➡️ Теперь ваш ход! Назовите город на букву <b>«{first_letter}»</b>"
        )
        
        await message.answer(start_text)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при запуске игры: {e}")
    finally:
        db.close()


@router.message(CitiesStates.playing, F.text)
async def handle_city(message: Message, state: FSMContext):
    """Обработка хода пользователя"""
    db = SessionLocal()
    
    try:
        data = await state.get_data()
        cities_game = data.get("cities_game")
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        game_id = data.get("game_id")
        city_repo = CityRepository(db)
        
        if not cities_game:
            await message.answer("❌ Ошибка: данные игры не найдены")
            await state.clear()
            return
        
        user_city_input = message.text.strip()
        user_city = normalize_city_name(user_city_input)
        
        # Проверки города пользователя
        if not user_city:
            await message.answer("❌ Пожалуйста, введите название города!")
            return
        
        if len(user_city) < 3:
            await message.answer("❌ Название города должно содержать хотя бы 3 буквы!")
            return
        
        # 1. Проверяем существование города
        if not city_repo.city_exists(user_city):
            await save_game_results(session_id, user_id, game_id, cities_game.user_score, cities_game.moves_count)
            await message.answer(
                f"💔 <b>Город не найден!</b>\n\n"
                f"Город «{user_city}» не существует в нашей базе.\n\n"
                f"📊 <b>Результаты:</b>\n"
                f"• Правильных ходов: {cities_game.user_score}\n"
                f"• Всего ходов: {cities_game.moves_count}\n\n"
                f"🎮 Сыграть еще раз: /cities"
            )
            await state.clear()
            return
        
        # 2. Проверяем, не использовался ли город
        if cities_game.is_city_used(user_city):
            await save_game_results(session_id, user_id, game_id, cities_game.user_score, cities_game.moves_count)
            await message.answer(
                f"💔 <b>Город уже использовался!</b>\n\n"
                f"Город «{user_city}» уже называли в этой игре.\n\n"
                f"📊 <b>Результаты:</b>\n"
                f"• Правильных ходов: {cities_game.user_score}\n"
                f"• Всего ходов: {cities_game.moves_count}\n\n"
                f"🎮 Сыграть еще раз: /cities"
            )
            await state.clear()
            return
        
        # 3. Проверяем правильность буквы
        expected_letter = get_game_letter(cities_game.current_city)
        actual_letter = get_first_letter(user_city)
        
        if actual_letter != expected_letter:
            await save_game_results(session_id, user_id, game_id, cities_game.user_score, cities_game.moves_count)
            await message.answer(
                f"💔 <b>Неверная буква!</b>\n\n"
                f"Город должен начинаться на букву «{expected_letter}», а не «{actual_letter}».\n\n"
                f"📊 <b>Результаты:</b>\n"
                f"• Правильных ходов: {cities_game.user_score}\n"
                f"• Всего ходов: {cities_game.moves_count}\n\n"
                f"🎮 Сыграть еще раз: /cities"
            )
            await state.clear()
            return
        
        # Город прошел все проверки
        cities_game.add_used_city(user_city)
        cities_game.increment_user_score()
        
        # Ход бота
        game_letter = get_game_letter(user_city)
        bot_city = city_repo.get_city_for_bot(game_letter, cities_game.used_cities)
        
        if not bot_city:
            # Пользователь выиграл - города закончились
            await save_game_results(session_id, user_id, game_id, cities_game.user_score, cities_game.moves_count)
            await message.answer(
                f"🎉 <b>Поздравляю! Вы выиграли!</b>\n\n"
                f"Я не нашел города на букву «{game_letter}».\n\n"
                f"📊 <b>Результаты:</b>\n"
                f"• Правильных ходов: {cities_game.user_score}\n"
                f"• Всего ходов: {cities_game.moves_count}\n"
                f"• Очков заработано: {cities_game.user_score}\n\n"
                f"🎮 Сыграть еще раз: /cities\n"
                f"📈 Статистика: /profile"
            )
            await state.clear()
            return
        
        # ВАЖНО: Проверяем, что город бота не использовался (дополнительная защита)
        if cities_game.is_city_used(bot_city):
            # Если бот попытался использовать уже названный город - ищем другой
            available_cities = city_repo.get_cities_by_first_letter(game_letter, cities_game.used_cities)
            
            # Ищем первый неиспользованный город
            for city_obj in available_cities:
                if not cities_game.is_city_used(city_obj.name):
                    bot_city = city_obj.name
                    break
            else:
                # Если все города использованы - пользователь выиграл
                bot_city = None
        
        if not bot_city:
            # Пользователь выиграл - города закончились
            await save_game_results(session_id, user_id, game_id, cities_game.user_score, cities_game.moves_count)
            await message.answer(
                f"🎉 <b>Поздравляю! Вы выиграли!</b>\n\n"
                f"Я не нашел города на букву «{game_letter}».\n\n"
                f"📊 <b>Результаты:</b>\n"
                f"• Правильных ходов: {cities_game.user_score}\n"
                f"• Всего ходов: {cities_game.moves_count}\n"
                f"• Очков заработано: {cities_game.user_score}\n\n"
                f"🎮 Сыграть еще раз: /cities\n"
                f"📈 Статистика: /profile"
            )
            await state.clear()
            return
        
        # Бот делает успешный ход
        cities_game.add_used_city(bot_city)
        cities_game.increment_bot_score()
        cities_game.current_city = bot_city
        
        await state.update_data(cities_game=cities_game)
        
        next_letter = get_game_letter(bot_city)
        await message.answer(
            f"✅ <b>Принимаю!</b> Город «{user_city}»\n\n"
            f"🤖 <b>Мой ход:</b>\n"
            f"<code>{bot_city}</code>\n\n"
            f"➡️ Теперь ваш ход! Назовите город на букву <b>«{next_letter}»</b>"
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке хода: {e}")
    finally:
        db.close()


@router.message(Command("stop"))
async def stop_cities(message: Message, state: FSMContext):
    """Принудительное завершение игры"""
    
    data = await state.get_data()
    cities_game = data.get("cities_game")
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    game_id = data.get("game_id")
    
    if cities_game:
        # СОХРАНЯЕМ ТЕКУЩИЙ РЕЗУЛЬТАТ В БД
        await save_game_results(session_id, user_id, game_id, cities_game.user_score, cities_game.moves_count)
        
        await message.answer(
            f"⏹️ <b>Игра завершена</b>\n\n"
            f"📊 <b>Ваши результаты:</b>\n"
            f"• Правильных ходов: <code>{cities_game.user_score}</code>\n"
            f"• Всего ходов: <code>{cities_game.moves_count}</code>\n\n"
            f"🎮 Сыграть еще раз: /cities"
        )
        
        await state.clear()
    else:
        await message.answer("❌ Активная игра не найдена")
        await state.clear()