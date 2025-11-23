from sqlalchemy import func
from database.models import City
from repositories.base_repository import BaseRepository

class CityRepository(BaseRepository):
    """Репозиторий для работы с городами"""
    
    def get_city_by_name(self, city_name: str):
        """Находит город по названию"""
        clean_name = city_name.strip().title()
        
        result = self.db.query(City)\
            .filter(func.lower(City.name) == func.lower(clean_name))\
            .first()
        
        return result
    
    def get_cities_by_first_letter(self, letter: str, exclude_cities: set = None):
        """Находит города по первой букве, исключая использованные"""
        clean_letter = letter.strip().upper()
        
        query = self.db.query(City).filter(
            func.upper(func.substr(City.name, 1, 1)) == clean_letter
        )
        
        if exclude_cities:
            # ИСПРАВЛЕНИЕ: используем func.lower() для регистронезависимого сравнения
            exclude_lower = {city.lower() for city in exclude_cities}
            query = query.filter(~func.lower(City.name).in_(exclude_lower))
        
        return query.all()
    
    def get_city_for_bot(self, last_letter: str, used_cities: set) -> str:
        """Находит город для хода бота по первой букве"""
        available_cities = self.get_cities_by_first_letter(last_letter, used_cities)
        
        if available_cities:
            return available_cities[0].name
        return None
    
    def get_random_start_city(self):
        """Получает случайный город для начала игры"""
        return self.db.query(City).order_by(func.random()).first()
    
    def city_exists(self, city_name: str) -> bool:
        """Проверяет, существует ли город в БД"""
        return self.get_city_by_name(city_name) is not None