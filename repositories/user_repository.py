from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from database.models import User, GameSession, Rating
from repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""

    def get_or_create_user(self, telegram_id: int, username: str,
                          first_name: str, last_name: str = None) -> User:
        """Возвращает пользователя по telegram_id или создает нового"""
        user = self.get_user_by_telegram_id(telegram_id)

        if user:
            print(f"✅ Найден существующий пользователь: {user.first_name} (ID: {user.id})")
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )

        self.save(user)
        print(f"✅ Создан новый пользователь: {user.first_name} (ID: {user.id})")
        return user

        
    def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Находит пользователя по telegram_id"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        return self.db.execute(stmt).scalar_one_or_none()


    def get_user_by_id(self, user_id: int) -> User:
        """Находит пользователя по id"""
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_all_users(self) -> list[User]:
        """Возвращает всех пользователей"""
        stmt = select(User)
        return self.db.execute(stmt).scalars().all()

    def update_user(self, user: User) -> User:
        """Обновляет данные пользователя"""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def block_user(self, user_id: int, reason: str) -> bool:
        """Блокирует пользователя по user_id"""
        user = self.get_user_by_id(user_id)
        if user:
            user.is_blocked = True
            user.block_reason = reason
            self.db.commit()
            return True
        return False

    def unblock_user(self, user_id: int) -> bool:
        """Разблокирует пользователя по user_id"""
        user = self.get_user_by_id(user_id)
        if user:
            user.is_blocked = False
            user.block_reason = None
            self.db.commit()
            return True
        return False

    def get_user_stats(self, user_id: int) -> dict:
        """Возвращает статистику пользователя по играм"""
        # Общая статистика игр
        total_sessions = self.db.execute(
            select(func.count(GameSession.id))
            .where(GameSession.user_id == user_id)
        ).scalar() or 0
        
        completed_sessions = self.db.execute(
            select(func.count(GameSession.id))
            .where(GameSession.user_id == user_id, GameSession.completed == True)
        ).scalar() or 0
        
        # Рейтинги по играм
        ratings = self.db.execute(
            select(Rating).where(Rating.user_id == user_id)
        ).scalars().all()
        
        return {
            'total_games': total_sessions,
            'completed_games': completed_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'ratings': ratings
        }

    def get_total_users_count(self) -> int:
        """Возвращает общее количество пользователей"""
        return self.db.execute(select(func.count(User.id))).scalar()

    def get_blocked_users_count(self) -> int:
        """Возвращает количество заблокированных пользователей"""
        return self.db.execute(
            select(func.count(User.id)).where(User.is_blocked == True)
        ).scalar()

    def get_active_today_count(self) -> int:
        """Возвращает количество активных пользователей за сегодня"""
        today = datetime.now().date()
        return self.db.execute(
            select(func.count(func.distinct(GameSession.user_id)))
            .where(func.date(GameSession.started_at) == today)
        ).scalar() or 0
    
    def get_users_since_count(self, since_date) -> int:
        """Количество пользователей зарегистрированных с указанной даты"""
        return self.db.execute(
            select(func.count(User.id)).where(User.created_at >= since_date)
        ).scalar() or 0