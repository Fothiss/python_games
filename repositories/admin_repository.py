from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import Admin, User
from datetime import datetime

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def is_admin(self, user_id: int) -> bool:
        """Проверяет является ли пользователь админом по user_id"""
        stmt = select(Admin).where(
            Admin.user_id == user_id,
            Admin.is_active == True
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None
    
    def add_admin(self, user_id: int, added_by_user_id: int) -> Admin:
        """Добавляет пользователя в админы по user_id"""
        # Проверяем существование пользователя
        user_stmt = select(User).where(User.id == user_id)
        user = self.db.execute(user_stmt).scalar_one_or_none()
        
        if not user:
            raise ValueError(f"Пользователь с user_id {user_id} не найден")
        
        # Проверяем существование добавляющего
        added_by_stmt = select(User).where(User.id == added_by_user_id)
        added_by_user = self.db.execute(added_by_stmt).scalar_one_or_none()
        
        if not added_by_user:
            raise ValueError(f"Пользователь с user_id {added_by_user_id} не найден")
        
        # ПРОВЕРЯЕМ СУЩЕСТВУЮЩУЮ ЗАПИСЬ (даже неактивную)
        existing_admin_stmt = select(Admin).where(Admin.user_id == user_id)
        existing_admin = self.db.execute(existing_admin_stmt).scalar_one_or_none()
        
        if existing_admin:
            # Если запись существует, активируем ее
            if existing_admin.is_active:
                raise ValueError("Пользователь уже является администратором")
            else:
                # Активируем существующую запись
                existing_admin.is_active = True
                existing_admin.added_by = added_by_user_id
                existing_admin.added_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing_admin)
                return existing_admin
        else:
            # Создаем новую запись
            admin = Admin(
                user_id=user_id,
                added_by=added_by_user_id,
                is_active=True
            )
            self.db.add(admin)
            self.db.commit()
            self.db.refresh(admin)
            return admin
    
    def remove_admin(self, user_id: int) -> bool:
        """Удаляет пользователя из админов по user_id"""
        stmt = select(Admin).where(Admin.user_id == user_id)
        admin = self.db.execute(stmt).scalar_one_or_none()
        
        if admin:
            admin.is_active = False
            self.db.commit()
            return True
        return False
    
    def get_all_admins(self) -> list[tuple[Admin, User]]:
        """Возвращает всех активных админов с информацией о пользователе"""
        stmt = (
            select(Admin, User)
            .join(User, Admin.user_id == User.id)
            .where(Admin.is_active == True)
            .order_by(Admin.added_at.desc())
        )
        return self.db.execute(stmt).all()
    
    def get_admin_by_user_id(self, user_id: int) -> Admin:
        """Находит админа по user_id"""
        stmt = select(Admin).where(Admin.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()