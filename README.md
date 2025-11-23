# Telegram Games Bot

Телеграм бот с коллекцией мини-игр: "Города", "Угадай число" и "Викторина". Игроки могут соревноваться в рейтинге и отслеживать свою статистику.

## 🎮 Доступные игры

- **🏙️ Города** - классическая игра в города на последнюю букву
- **🔢 Угадай число** - попробуй угадать число за минимальное количество попыток  
- **❓ Викторина** - проверь свои знания в разных категориях

## 🛠 Технологический стек

- **Python 3.12.8**
- **aiogram 3.22** - фреймворк для Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **SQLite** - база данных
- **uv** - менеджер пакетов и окружений
- **pytest** - тестирование

## 📁 Структура проекта
```
(.venv) D:\pet projects\tg_games>python generate_tree.py
└── 
    ├── app
    │   ├── handlers # Обработчики событий
    │   │   ├── admin # Обработчики админских команд
    │   │   │   ├── __init__.py
    │   │   │   ├── admin_games_mgmt.py
    │   │   │   ├── admin_mgmt.py
    │   │   │   ├── admin_panel.py
    │   │   │   ├── admin_stats.py
    │   │   │   └── admin_user_mgmt.py
    │   │   ├── games # Обработчики игровых команд
    │   │   │   ├── __init__.py
    │   │   │   ├── cities.py
    │   │   │   ├── guess_number.py
    │   │   │   └── quiz.py
    │   │   ├── __init__.py
    │   │   ├── common.py
    │   │   ├── games_list.py
    │   │   ├── help.py
    │   │   ├── profile.py
    │   │   ├── rating.py
    │   │   └── start.py
    │   ├── middlewares # Middleware для идентификации админов
    │   │   └── admin.py
    │   ├── __init__.py
    │   ├── config.py # Файл с классом конфига
    │   └── main.py # Файл с запуском бота и общими конфигурациями
    ├── data # Папка для хранения БД и файла с городами
    ├── database # Папка с файлами для работы БД
    │   ├── __init__.py
    │   ├── engine.py
    │   ├── initial_data.py # Файл начальной инициализации данных
    │   └── models.py
    ├── repositories # Папка с файлами репозиториями для каждой таблицы БД
    │   ├── __init__.py
    │   ├── admin_repository.py
    │   ├── base_repository.py
    │   ├── city_repository.py
    │   ├── game_repository.py
    │   ├── game_session_repository.py
    │   ├── quiz_repository.py
    │   ├── rating_repository.py
    │   └── user_repository.py
    ├── tests # Папка с тестами
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_initial_data.py
    │   └── test_user_repository.py
    ├── utils # Вспомогаетльные утилиты
    │   └── states.py # Состояния FSM для игр
    ├── generate_tree.py # Файл для генерации структуры  проекта
    ├── README.md
    └── run.py # Файл запуска проекта
```
## Шаги для запуска

### 1. Клонирование репозитория
```bash
git clone <ссылка-на-репозиторий>
cd tg_games
```

### 2. Установка зависимостей
Установите uv если не установлен
```pip install uv```

Установите зависимости проекта
```uv sync```

### 3. Настройка переменных окружения
Переменные окружения находятся в файле `.env`. Если его нет, его необходимо создать и указать следующие данные.
```
TG_TOKEN=<yor_tg_token>
DB_URL=sqlite:///./data/bot.db
ADMIN_IDS=<your_admins_user_id>
```

### 4. Запуск проекта
Для запуска необходимо запустить файл `run.py`.
```
python run.py
```

### 5. Запуск тестов
Для запуска тестов можно воспользовться командой для каждого файла
```
pytest tests/test_user_repository.py
```
или для всех тестов
```
pytest tests/ -v
```
