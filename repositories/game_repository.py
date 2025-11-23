from sqlalchemy.orm import Session
from sqlalchemy import select, func
from database.models import Game, GameSession
from repositories.base_repository import BaseRepository

class GameRepository(BaseRepository):
    """
    Репозиторий для работы с играми
    """

    def get_game_by_id(self, game_id: int) -> Game:
        """
        Находит игру по ID
        """
        stmt = select(Game).where(Game.id == game_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    
    def get_game_by_code(self, game_code: str) -> Game:
        """
        Находит игру по коду (например, 'guess_number')
        """
        stmt = select(Game).where(Game.code == game_code)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all_games(self) -> list[Game]:
        """
        Возвращает все игры
        """
        stmt = select(Game)
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def get_active_games(self) -> list[Game]:
        """
        Возвращает только активные игры
        """
        stmt = select(Game).where(Game.is_active == True)
        result = self.db.execute(stmt)
        return result.scalars().all()
    
    def toggle_game(self, game_code: str) -> bool:
        """Переключает статус игры (вкл/выкл)"""
        game = self.get_game_by_code(game_code)
        if game:
            game.is_active = not game.is_active
            self.db.commit()
            return True
        return False

    def get_game_stats(self, game_id: int) -> dict:
        """Возвращает статистику по игре"""
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
            'completed_sessions': completed_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        }