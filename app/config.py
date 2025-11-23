import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config():
    BOT_TOKEN: str
    DB_URL: str = 'sqlite:///./data/bot.db'
    ADMIN_IDS: list = None

    def __post_init__(self):
        """Выполняется после автоматического __init__"""
        # Валидация обязательных полей
        if not self.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN не найден! Проверьте файл .env")
        
        # Обработка ADMIN_IDS
        if self.ADMIN_IDS is None:
            self.ADMIN_IDS = []
        elif isinstance(self.ADMIN_IDS, str):
            # Преобразование ADMIN_IDS из строки в список чисел
            try:
                self.ADMIN_IDS = [int(id.strip()) for id in self.ADMIN_IDS.split(',') if id.strip()]
            except ValueError:
                self.ADMIN_IDS = []
        
        # Проверка для SQLite
        if self.DB_URL.startswith('sqlite'):
            db_path = self.DB_URL.replace('sqlite:///', '')
            directory = os.path.dirname(db_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

        print("✅ Конфиг загружен успешно!")

config = Config(
    BOT_TOKEN=os.getenv('TG_TOKEN'),
    ADMIN_IDS=os.getenv('ADMIN_IDS'),
    DB_URL=os.getenv('DB_URL')
)