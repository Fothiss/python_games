from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from database.models import GameSession, User
from .base_repository import BaseRepository
from .rating_repository import RatingRepository


class GameSessionRepository(BaseRepository):
    """Репозиторий для работы с игровыми сессиями"""

    def create_session(self, user_id: int, game_id: int) -> GameSession:
        """Функция для создания новой игровой сессии"""

        session = GameSession(
            user_id=user_id,
            game_id=game_id,
            started_at=datetime.utcnow()
        )

        self.save(session)
        print(f"🎯 Создана игровая сессия: User {user_id}, Game {game_id}")
        return session


    def get_user_sessions(self, user_id: int, game_id: int = None) -> list[GameSession]:
        """Возвращает сессии пользователя"""
        if game_id:
            stmt = select(GameSession).where(
                GameSession.user_id == user_id,
                GameSession.game_id == game_id
            )
        else:
            stmt = select(GameSession).where(GameSession.user_id == user_id)
        
        result = self.db.execute(stmt)
        return result.scalars().all()


    def get_user_best_score(self, user_id: int, game_id: int) -> int:
        """Возвращает лучший результат пользователя в игре"""
        stmt = select(func.max(GameSession.score)).where(
            GameSession.user_id == user_id,
            GameSession.game_id == game_id,
            GameSession.completed == True
        )
        result = self.db.execute(stmt)
        best_score = result.scalar() or 0
        return best_score
    
    def complete_session(self, session_id: int, score: int, attempts: int):
        """Завершает игровую сессию с результатами и обновляет рейтинг"""
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session:
            session.score = score
            session.attempts = attempts
            session.completed = True
            session.finished_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(session)
            
            rating_repo = RatingRepository(self.db)
            rating_repo.update_rating(session.user_id, session.game_id, score)
            
            print(f"🎯 Завершена сессия {session_id} с результатом: {score} очков")

        return session
    
    def get_sessions_since_count(self, since_date) -> int:
        """Количество игровых сессий с указанной даты"""
        stmt = select(func.count(GameSession.id)).where(GameSession.started_at >= since_date)
        result = self.db.execute(stmt)
        return result.scalar() or 0

    def get_most_active_users(self, limit=5) -> list:
        """Самые активные пользователи по количеству игр"""
        stmt = (
            select(User, func.count(GameSession.id).label('game_count'))
            .join(GameSession, User.id == GameSession.user_id)
            .group_by(User.id)
            .order_by(func.count(GameSession.id).desc())
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.all()
    
    def get_total_sessions_count(self) -> int:
        """Общее количество игровых сессий"""
        stmt = select(func.count(GameSession.id))
        result = self.db.execute(stmt)
        return result.scalar() or 0

    def get_completed_sessions_count(self) -> int:
        """Количество завершенных игровых сессий"""
        stmt = select(func.count(GameSession.id)).where(GameSession.completed == True)
        result = self.db.execute(stmt)
        return result.scalar() or 0

    def get_game_stats(self, game_id: int) -> dict:
        """Статистика по конкретной игре"""
        total_sessions_stmt = select(func.count(GameSession.id)).where(
            GameSession.game_id == game_id
        )
        total_sessions = self.db.execute(total_sessions_stmt).scalar() or 0
        
        completed_sessions_stmt = select(func.count(GameSession.id)).where(
            GameSession.game_id == game_id,
            GameSession.completed == True
        )
        completed_sessions = self.db.execute(completed_sessions_stmt).scalar() or 0
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions
        }