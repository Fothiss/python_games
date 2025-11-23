from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Game, QuizQuestion, City
from database.engine import SessionLocal
import os
import csv

def create_initial_games(db: Session):
    """Создает начальный набор игр"""
    games_data = [
        {
            "name": "Угадай число",
            "code": "guess_number",
            "description": "Попробуй угадать число от 1 до 100 за минимальное количество попыток!"
        },
        {
            "name": "Викторина", 
            "code": "quiz",
            "description": "Проверь свои знания в увлекательной викторине!"
        },
        {
            "name": "Города",
            "code": "cities", 
            "description": "Вспомни географию - называй города на последнюю букву!"
        }
    ]
    
    for game_data in games_data:
        existing_game = db.query(Game).filter(Game.code == game_data["code"]).first()
        if not existing_game:
            game = Game(**game_data)
            db.add(game)
    
    db.commit()
    print("🎮 Начальные игры добавлены в базу данных")

def create_initial_quiz_questions(db: Session):
    """Создает начальные вопросы для викторины"""
    questions_data = [
        # ЛЕГКИЕ ВОПРОСЫ (8 штук)
        {
            "question": "Какая планета известна как 'Красная планета'?",
            "option1": "Венера",
            "option2": "Марс", 
            "option3": "Юпитер",
            "option4": "Сатурн",
            "correct_option": 2,
            "difficulty": "easy",
            "category": "science",
            "explanation": "Марс называют Красной планетой из-за оксида железа в почве."
        },
        {
            "question": "Сколько цветов у радуги?",
            "option1": "5",
            "option2": "6", 
            "option3": "7",
            "option4": "8",
            "correct_option": 3,
            "difficulty": "easy",
            "category": "science",
            "explanation": "Радуга имеет 7 цветов: красный, оранжевый, желтый, зеленый, голубой, синий, фиолетовый."
        },
        {
            "question": "Какое животное является символом России?",
            "option1": "Медведь",
            "option2": "Орел", 
            "option3": "Волк",
            "option4": "Тигр",
            "correct_option": 1,
            "difficulty": "easy",
            "category": "geography",
            "explanation": "Медведь - традиционный символ России, олицетворяющий силу и мощь."
        },
        {
            "question": "В каком году Москва принимала Олимпийские игры?",
            "option1": "1976",
            "option2": "1980", 
            "option3": "1984",
            "option4": "1988",
            "correct_option": 2,
            "difficulty": "easy",
            "category": "sport",
            "explanation": "XXII Летние Олимпийские игры прошли в Москве в 1980 году."
        },
        {
            "question": "Кто написал 'Евгения Онегина'?",
            "option1": "Лермонтов",
            "option2": "Пушкин", 
            "option3": "Толстой",
            "option4": "Достоевский",
            "correct_option": 2,
            "difficulty": "easy",
            "category": "art",
            "explanation": "Александр Сергеевич Пушкин - автор романа в стихах 'Евгений Онегин'."
        },
        {
            "question": "Какая столица у Франции?",
            "option1": "Лондон",
            "option2": "Берлин", 
            "option3": "Париж",
            "option4": "Мадрид",
            "correct_option": 3,
            "difficulty": "easy",
            "category": "geography",
            "explanation": "Париж - столица и крупнейший город Франции."
        },
        {
            "question": "Сколько дней в високосном году?",
            "option1": "365",
            "option2": "366", 
            "option3": "364",
            "option4": "367",
            "correct_option": 2,
            "difficulty": "easy",
            "category": "science",
            "explanation": "В високосном году 366 дней - добавляется 29 февраля."
        },
        {
            "question": "Кто был первым человеком в космосе?",
            "option1": "Нил Армстронг",
            "option2": "Юрий Гагарин", 
            "option3": "Валентина Терешкова",
            "option4": "Алексей Леонов",
            "correct_option": 2,
            "difficulty": "easy",
            "category": "history",
            "explanation": "Юрий Гагарин совершил первый полет в космос 12 апреля 1961 года."
        },
        
        # СРЕДНИЕ ВОПРОСЫ (8 штук)
        {
            "question": "Какая самая длинная река в России?",
            "option1": "Волга",
            "option2": "Енисей", 
            "option3": "Лена",
            "option4": "Обь",
            "correct_option": 3,
            "difficulty": "medium",
            "category": "geography",
            "explanation": "Лена - 4400 км, Енисей - 3487 км, Обь - 3650 км, Волга - 3530 км."
        },
        {
            "question": "В каком году началась Вторая мировая война?",
            "option1": "1937",
            "option2": "1939", 
            "option3": "1941",
            "option4": "1943",
            "correct_option": 2,
            "difficulty": "medium",
            "category": "history",
            "explanation": "1 сентября 1939 года Германия напала на Польшу."
        },
        {
            "question": "Кто написал картину 'Черный квадрат'?",
            "option1": "Кандинский",
            "option2": "Малевич", 
            "option3": "Пикассо",
            "option4": "Дали",
            "correct_option": 2,
            "difficulty": "medium",
            "category": "art",
            "explanation": "Казимир Малевич создал 'Черный квадрат' в 1915 году."
        },
        {
            "question": "Сколько костей в теле взрослого человека?",
            "option1": "186",
            "option2": "206", 
            "option3": "226",
            "option4": "246",
            "correct_option": 2,
            "difficulty": "medium",
            "category": "science",
            "explanation": "У взрослого человека 206 костей, у новорожденного - около 270."
        },
        {
            "question": "Какая самая большая планета Солнечной системы?",
            "option1": "Земля",
            "option2": "Сатурн", 
            "option3": "Юпитер",
            "option4": "Нептун",
            "correct_option": 3,
            "difficulty": "medium",
            "category": "science",
            "explanation": "Юпитер - газовый гигант, крупнейшая планета нашей системы."
        },
        {
            "question": "Столица Австралии?",
            "option1": "Сидней",
            "option2": "Мельбурн", 
            "option3": "Канберра",
            "option4": "Перт",
            "correct_option": 3,
            "difficulty": "medium",
            "category": "geography",
            "explanation": "Канберра стала компромиссом между Сиднеем и Мельбурном."
        },
        {
            "question": "Кто был первым президентом России?",
            "option1": "Михаил Горбачев",
            "option2": "Борис Ельцин", 
            "option3": "Владимир Путин",
            "option4": "Дмитрий Медведев",
            "correct_option": 2,
            "difficulty": "medium",
            "category": "history",
            "explanation": "Борис Ельцин стал первым президентом РФ в 1991 году."
        },
        {
            "question": "В каком виде спорта используется шайба?",
            "option1": "Футбол",
            "option2": "Баскетбол", 
            "option3": "Хоккей",
            "option4": "Теннис",
            "correct_option": 3,
            "difficulty": "medium",
            "category": "sport",
            "explanation": "Шайба используется в хоккее с шайбой."
        },
        
        # СЛОЖНЫЕ ВОПРОСЫ (4 штуки)
        {
            "question": "Какой химический элемент обозначается символом 'Au'?",
            "option1": "Серебро",
            "option2": "Алюминий", 
            "option3": "Золото",
            "option4": "Аргон",
            "correct_option": 3,
            "difficulty": "hard",
            "category": "science",
            "explanation": "Au - золото (от латинского Aurum)."
        },
        {
            "question": "Кто автор оперы 'Князь Игорь'?",
            "option1": "Чайковский",
            "option2": "Бородин", 
            "option3": "Мусоргский",
            "option4": "Римский-Корсаков",
            "correct_option": 2,
            "difficulty": "hard",
            "category": "art",
            "explanation": "Александр Порфирьевич Бородин - русский композитор, автор оперы 'Князь Игорь'."
        },
        {
            "question": "В каком году был основан Санкт-Петербург?",
            "option1": "1689",
            "option2": "1703", 
            "option3": "1721",
            "option4": "1740",
            "correct_option": 2,
            "difficulty": "hard",
            "category": "history",
            "explanation": "Санкт-Петербург был основан Петром I 27 мая 1703 года."
        },
        {
            "question": "Какое озеро является самым глубоким в мире?",
            "option1": "Виктория",
            "option2": "Байкал", 
            "option3": "Танганьика",
            "option4": "Верхнее",
            "correct_option": 2,
            "difficulty": "hard",
            "category": "geography",
            "explanation": "Озеро Байкал имеет глубину 1642 метра - это самое глубокое озеро в мире."
        }
    ]
    
    for question_data in questions_data:
        existing_question = db.query(QuizQuestion).filter(
            QuizQuestion.question == question_data["question"]
        ).first()
        if not existing_question:
            question = QuizQuestion(**question_data)
            db.add(question)
    
    db.commit()
    print("❓ Начальные вопросы викторины добавлены в БД")

def create_initial_cities(db: Session):
    """Создает начальный набор городов из CSV файла КЛАДР/ФИАС"""
    csv_file_path = './data/cities.csv'
    
    if not os.path.exists(csv_file_path):
        print(f"❌ Файл {csv_file_path} не найден!")
        return
    
    cities_added = 0
    cities_skipped = 0
    
    try:
        unique_city_names = set()
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            
            print("🏙️ Загрузка городов из CSV...")
            
            for row in reader:
                # Определяем название города в зависимости от типа записи
                city_name = ''
                region = row.get('Регион', '').strip()
                region_type = row.get('Тип региона', '').strip()
                city_type = row.get('Тип города', '').strip()
                
                # Логика определения города
                if city_type == 'г':  # Обычный город
                    city_name = row.get('Город', '').strip()
                elif region_type == 'г':  # Город федерального значения
                    city_name = region
                    region = ''  # У городов фед. значения нет региона
                
                if not city_name:
                    continue
                
                # Проверяем уникальность и существование в БД
                city_name_lower = city_name.lower()
                if city_name_lower not in unique_city_names:
                    unique_city_names.add(city_name_lower)
                    
                    existing_city = db.query(City)\
                        .filter(func.lower(City.name) == city_name_lower)\
                        .first()
                    
                    if not existing_city:
                        db.add(City(name=city_name, region=region))
                        cities_added += 1
                    else:
                        cities_skipped += 1
        
        db.commit()
        print(f"✅ Добавлено: {cities_added}, Пропущено: {cities_skipped}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")

def initialize_data():
    """Инициализирует БД с начальными данными"""
    db = SessionLocal()
    try:
        create_initial_games(db)
        create_initial_quiz_questions(db)
        create_initial_cities(db)
        print("✅ База данных инициализирована успешно!")
    finally:
        db.close()