import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from database.models import User, Game, GameSession, Rating
from repositories import UserRepository


class TestUserRepository:
    """Тесты для UserRepository"""
    
    def test_create_user(self, test_db):
        """Тест создания пользователя"""
        user_repo = UserRepository(test_db)
        
        # Создаем пользователя
        user = user_repo.get_or_create_user(
            telegram_id=12345,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        assert user is not None
        assert user.telegram_id == 12345
        assert user.username == "test_user"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_blocked is False
    
    def test_get_existing_user(self, test_db):
        """Тест получения существующего пользователя"""
        user_repo = UserRepository(test_db)
        
        # Сначала создаем пользователя
        created_user = user_repo.get_or_create_user(
            telegram_id=12345,
            username="test_user",
            first_name="Test"
        )
        
        # Пытаемся получить того же пользователя
        found_user = user_repo.get_or_create_user(
            telegram_id=12345,
            username="test_user",
            first_name="Test"
        )
        
        assert found_user is not None
        assert found_user.id == created_user.id  # Должен быть тот же ID
        assert found_user.telegram_id == 12345
    
    def test_get_user_by_telegram_id(self, test_db):
        """Тест поиска пользователя по telegram_id"""
        user_repo = UserRepository(test_db)
        
        # Создаем пользователя
        user_repo.get_or_create_user(
            telegram_id=12345,
            username="test_user",
            first_name="Test"
        )
        
        # Ищем по telegram_id
        user = user_repo.get_user_by_telegram_id(12345)
        
        assert user is not None
        assert user.telegram_id == 12345
        assert user.first_name == "Test"
        
        # Пытаемся найти несуществующего пользователя
        non_existent = user_repo.get_user_by_telegram_id(99999)
        assert non_existent is None
    
    def test_get_user_by_id(self, test_db):
        """Тест поиска пользователя по ID"""
        user_repo = UserRepository(test_db)
        
        # Создаем пользователя
        created_user = user_repo.get_or_create_user(
            telegram_id=12345,
            username="test_user",
            first_name="Test"
        )
        
        # Ищем по ID
        user = user_repo.get_user_by_id(created_user.id)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.first_name == "Test"
        
        # Пытаемся найти несуществующего пользователя
        non_existent = user_repo.get_user_by_id(99999)
        assert non_existent is None
    
    def test_get_all_users(self, test_db):
        """Тест получения всех пользователей"""
        user_repo = UserRepository(test_db)
        
        # Создаем несколько пользователей
        user_repo.get_or_create_user(11111, "user1", "User1")
        user_repo.get_or_create_user(22222, "user2", "User2")
        user_repo.get_or_create_user(33333, "user3", "User3")
        
        users = user_repo.get_all_users()
        
        assert len(users) == 3
        assert any(user.telegram_id == 11111 for user in users)
        assert any(user.telegram_id == 22222 for user in users)
        assert any(user.telegram_id == 33333 for user in users)
    
    def test_block_and_unblock_user(self, test_db):
        """Тест блокировки и разблокировки пользователя"""
        user_repo = UserRepository(test_db)
        
        # Создаем пользователя
        user = user_repo.get_or_create_user(12345, "test_user", "Test")
        
        # Блокируем пользователя
        block_result = user_repo.block_user(user.id, "Test block")
        assert block_result is True
        
        # Проверяем, что пользователь заблокирован
        blocked_user = user_repo.get_user_by_id(user.id)
        assert blocked_user.is_blocked is True
        assert blocked_user.block_reason == "Test block"
        
        # Разблокируем пользователя
        unblock_result = user_repo.unblock_user(user.id)
        assert unblock_result is True
        
        # Проверяем, что пользователь разблокирован
        unblocked_user = user_repo.get_user_by_id(user.id)
        assert unblocked_user.is_blocked is False
        assert unblocked_user.block_reason is None
    
    def test_block_nonexistent_user(self, test_db):
        """Тест блокировки несуществующего пользователя"""
        user_repo = UserRepository(test_db)
        
        result = user_repo.block_user(99999, "Reason")
        assert result is False
    
    def test_get_total_users_count(self, test_db):
        """Тест получения общего количества пользователей"""
        user_repo = UserRepository(test_db)
        
        # Изначально должен быть 0 пользователей
        count = user_repo.get_total_users_count()
        assert count == 0
        
        # Создаем пользователей
        user_repo.get_or_create_user(11111, "user1", "User1")
        user_repo.get_or_create_user(22222, "user2", "User2")
        
        count = user_repo.get_total_users_count()
        assert count == 2
    
    def test_get_blocked_users_count(self, test_db):
        """Тест получения количества заблокированных пользователей"""
        user_repo = UserRepository(test_db)
        
        # Создаем пользователей
        user1 = user_repo.get_or_create_user(11111, "user1", "User1")
        user2 = user_repo.get_or_create_user(22222, "user2", "User2")
        
        # Блокируем одного пользователя
        user_repo.block_user(user1.id, "Test")
        
        blocked_count = user_repo.get_blocked_users_count()
        assert blocked_count == 1
    
    def test_get_users_since_count(self, test_db):
        """Тест получения количества пользователей с определенной даты"""
        user_repo = UserRepository(test_db)
        
        # Создаем пользователей
        user_repo.get_or_create_user(11111, "user1", "User1")
        user_repo.get_or_create_user(22222, "user2", "User2")
        
        # Получаем количество пользователей с сегодняшней даты
        today = datetime.now().date()
        count = user_repo.get_users_since_count(today)
        assert count == 2
        
        # Получаем количество пользователей с завтрашней даты (должно быть 0)
        tomorrow = today + timedelta(days=1)
        count = user_repo.get_users_since_count(tomorrow)
        assert count == 0
    
    def test_get_user_stats(self, test_db):
        """Тест получения статистики пользователя"""
        user_repo = UserRepository(test_db)
        
        # Создаем пользователя
        user = user_repo.get_or_create_user(12345, "test_user", "Test")
        
        # Создаем тестовую игру
        game = Game(name="Test Game", code="test", description="Test game")
        test_db.add(game)
        test_db.commit()
        
        # Создаем игровые сессии
        session1 = GameSession(user_id=user.id, game_id=game.id, score=10)
        session2 = GameSession(user_id=user.id, game_id=game.id, score=20, completed=True)
        test_db.add_all([session1, session2])
        test_db.commit()
        
        # Создаем рейтинг
        rating = Rating(
            user_id=user.id, 
            game_id=game.id, 
            total_score=30,
            games_played=2,
            best_score=20,
            average_score=15.0,
            last_played=datetime.utcnow()
        )
        test_db.add(rating)
        test_db.commit()
        
        # Получаем статистику
        stats = user_repo.get_user_stats(user.id)
        
        assert stats['total_games'] == 2
        assert stats['completed_games'] == 1
        assert stats['completion_rate'] == 50.0
        assert len(stats['ratings']) == 1
        assert stats['ratings'][0].total_score == 30