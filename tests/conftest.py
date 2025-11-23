import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.engine import Base
from database.models import City, User, Game, GameSession, Rating


@pytest.fixture(scope='function')
def test_db():
    """Создает тестовую базу данных в памяти"""
    # Создаем движок для SQLite в памяти
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    
    # Создаем сессию
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()