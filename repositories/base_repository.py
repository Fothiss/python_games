from sqlalchemy.orm import Session


class BaseRepository:
    """
    Базовый класс для всех репозиториев.
    Содержит общую логику работы с БД.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, obj):
        """Сохраняет объект в БД"""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def save_all(self, objects):
        """Сохраняет несколько объектов в БД"""
        self.db.add_all(objects)
        self.db.commit()
        for obj in objects:
            self.db.refresh(obj)
        return objects