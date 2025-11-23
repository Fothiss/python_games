import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import config
from database.models import Base

# Создаем движок БД
engine = create_engine(
    config.DB_URL,  
    echo=False,            # Показывать SQL запросы в консоли (для разработки)
    future=True           # Использовать SQLAlchemy 2.0 style
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def init_db():
    """Создает все таблицы в БД"""
    print("🗃️ Создаем таблицы в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно!")

def get_db():
    """Генератор сессий для dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()