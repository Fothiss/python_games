import pytest
from database.models import Game, QuizQuestion, City
from database.initial_data import create_initial_games, create_initial_quiz_questions, create_initial_cities

class TestInitialData:
    """Тесты для инициализации начальных данных"""
    
    def test_create_initial_games(self, test_db):
        """Тест создания начальных игр"""
        create_initial_games(test_db)
        
        games = test_db.query(Game).all()
        assert len(games) == 3
        
        game_codes = [game.code for game in games]
        assert "guess_number" in game_codes
        assert "quiz" in game_codes
        assert "cities" in game_codes
        
        cities_game = test_db.query(Game).filter(Game.code == "cities").first()
        assert cities_game is not None
        assert cities_game.name == "Города"
        assert cities_game.is_active is True
    
    def test_create_initial_quiz_questions(self, test_db):
        """Тест создания вопросов викторины"""
        create_initial_quiz_questions(test_db)
        
        questions = test_db.query(QuizQuestion).all()
        assert len(questions) == 20
        
        easy_questions = test_db.query(QuizQuestion).filter(QuizQuestion.difficulty == "easy").all()
        medium_questions = test_db.query(QuizQuestion).filter(QuizQuestion.difficulty == "medium").all()
        hard_questions = test_db.query(QuizQuestion).filter(QuizQuestion.difficulty == "hard").all()
        
        assert len(easy_questions) == 8
        assert len(medium_questions) == 8
        assert len(hard_questions) == 4
        
        active_questions = test_db.query(QuizQuestion).filter(QuizQuestion.is_active == True).all()
        assert len(active_questions) == 20
        
        science_questions = test_db.query(QuizQuestion).filter(QuizQuestion.category == "science").all()
        assert len(science_questions) > 0
        
        first_question = questions[0]
        assert first_question.question is not None
        assert first_question.correct_option in [1, 2, 3, 4]
        assert first_question.explanation is not None
    
    def test_duplicate_games_not_created(self, test_db):
        """Тест что дубликаты игр не создаются"""
        create_initial_games(test_db)
        initial_count = test_db.query(Game).count()
        
        create_initial_games(test_db)
        final_count = test_db.query(Game).count()
        
        assert initial_count == final_count
    
    def test_duplicate_questions_not_created(self, test_db):
        """Тест что дубликаты вопросов не создаются"""
        create_initial_quiz_questions(test_db)
        initial_count = test_db.query(QuizQuestion).count()
        
        create_initial_quiz_questions(test_db)
        final_count = test_db.query(QuizQuestion).count()
        
        assert initial_count == final_count
    
    def test_cities_creation_with_mock_data(self, test_db):
        """Тест создания городов с мок-данными"""
        test_cities_data = [
            {"Тип региона": "обл", "Регион": "", "Тип города": "г", "Город": "Москва"},
            {"Тип региона": "г", "Регион": "Санкт-Петербург", "Тип города": "", "Город": ""},
            {"Тип региона": "обл", "Регион": "Ленинградская", "Тип города": "г", "Город": "Выборг"},
        ]
        
        import csv
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=["Тип региона", "Регион", "Тип города", "Город"])
            writer.writeheader()
            writer.writerows(test_cities_data)
            temp_file = f.name
        
        try:
            original_path = './data/cities.csv'
            if not os.path.exists('./data'):
                os.makedirs('./data')
            
            import shutil
            shutil.copy(temp_file, original_path)
            
            create_initial_cities(test_db)
            
            cities = test_db.query(City).all()
            assert len(cities) == 3
            
            city_names = [city.name for city in cities]
            assert "Москва" in city_names
            assert "Санкт-Петербург" in city_names
            assert "Выборг" in city_names
            
            moscow = test_db.query(City).filter(City.name == "Москва").first()
            assert moscow.region == ""
            
            spb = test_db.query(City).filter(City.name == "Санкт-Петербург").first()
            assert spb.region == ""
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            if os.path.exists(original_path):
                os.unlink(original_path)
    
    def test_games_have_descriptions(self, test_db):
        """Тест что все игры имеют описания"""
        create_initial_games(test_db)
        
        games = test_db.query(Game).all()
        for game in games:
            assert game.description is not None
            assert len(game.description) > 0
    
    def test_questions_have_valid_options(self, test_db):
        """Тест что все вопросы имеют валидные варианты ответов"""
        create_initial_quiz_questions(test_db)
        
        questions = test_db.query(QuizQuestion).all()
        for question in questions:
            assert question.option1 is not None
            assert question.option2 is not None
            assert question.option3 is not None
            assert question.option4 is not None
            assert question.correct_option in [1, 2, 3, 4]