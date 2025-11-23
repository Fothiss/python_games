from database.engine import init_db, get_db
from database.initial_data import initialize_data

def setup_database():
    """Настраивает базу данных (создает таблицы и начальные данные)"""
    print("🗃️ Инициализируем базу данных...")
    init_db()              # Создаем таблицы
    initialize_data()  # Добавляем начальные данные
    print("✅ База данных готова к работе!")

__all__ = ['setup_database', 'get_db', 'init_db', 'initialize_data']