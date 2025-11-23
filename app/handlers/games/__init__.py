from .guess_number import router as guess_number_router
from .quiz import router as quiz_router
from .cities import router as cities_router

__all__ = [
    'guess_number_router',
    'quiz_router',
    'cities_router'
]