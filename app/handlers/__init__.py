# Основные хендлеры
from .start import router as start_router
from .profile import router as profile_router
from .games_list import router as games_router
from .help import router as help_router
from .common import router as common_router
from .rating import router as rating_router

# Игры
from .games.guess_number import router as guess_number_router
from .games.quiz import router as quiz_router
from .games.cities import router as cities_router

# Админ-панель
from .admin import admin_routers

# Все основные роутеры (игры + основные хендлеры)
all_routers = [
    start_router,
    profile_router,
    games_router,
    help_router,
    common_router,
    rating_router,
    guess_number_router,
    quiz_router,
    cities_router
] + admin_routers

__all__ = [
    'all_routers'
]