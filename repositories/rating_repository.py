from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from database.models import User, Rating, Game
from datetime import datetime
from repositories.base_repository import BaseRepository

class RatingRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def update_rating(self, user_id: int, game_id: int, score: int):
        """
        Обновляет рейтинг пользователя после завершения игры
        """
        # Находим существующий рейтинг или создаем новый
        stmt = select(Rating).where(
            Rating.user_id == user_id,
            Rating.game_id == game_id
        )
        result = self.db.execute(stmt)
        rating = result.scalar_one_or_none()
        
        if rating:
            # Обновляем существующий рейтинг
            rating.total_score += score
            rating.games_played += 1
            rating.best_score = max(rating.best_score, score)
            rating.average_score = rating.total_score / rating.games_played
            rating.last_played = datetime.utcnow()
            print(f"📈 Обновлен рейтинг: User {user_id}, Game {game_id}, +{score} очков")
        else:
            # Создаем новый рейтинг
            rating = Rating(
                user_id=user_id,
                game_id=game_id,
                total_score=score,
                games_played=1,
                best_score=score,
                average_score=score,
                last_played=datetime.utcnow()
            )
            self.db.add(rating)
            print(f"📈 Создан рейтинг: User {user_id}, Game {game_id}, {score} очков")
        
        self.db.commit()
        self.db.refresh(rating)
        return rating
    
    def get_user_ratings(self, user_id: int):
        """
        Возвращает все рейтинги пользователя с информацией об играх
        """
        stmt = (
            select(Rating, Game)
            .join(Game, Rating.game_id == Game.id)
            .where(Rating.user_id == user_id)
            .order_by(Rating.total_score.desc())
        )
        result = self.db.execute(stmt)
        return result.all()
    
    def get_leaderboard(self, game_id: int = None, limit: int = 10):
        """
        Возвращает топ игроков
        Если game_id is None - общий топ по всем играм
        """
        if game_id:
            # Топ для конкретной игры
            stmt = (
                select(Rating, User, Game)
                .join(User, Rating.user_id == User.id)
                .join(Game, Rating.game_id == Game.id)
                .where(Rating.game_id == game_id)
                .order_by(Rating.total_score.desc())
                .limit(limit)
            )
        else:
            # Общий топ (сумма очков по всем играм)
            stmt = (
                select(
                    User,
                    func.sum(Rating.total_score).label('total_score'),
                    func.sum(Rating.games_played).label('total_games'),
                    func.max(Rating.best_score).label('best_score')
                )
                .select_from(User)
                .join(Rating, User.id == Rating.user_id)
                .group_by(User.id)
                .order_by(desc('total_score'))
                .limit(limit)
            )
        
        result = self.db.execute(stmt)
        return result.all()
    
    def get_user_global_rank(self, user_id: int):
        """
        Возвращает глобальный ранг пользователя среди всех игроков
        """
        # Подзапрос для сумм очков всех пользователей
        user_scores = (
            select(
                User.id,
                func.sum(Rating.total_score).label('total_score')
            )
            .select_from(User)
            .join(Rating, User.id == Rating.user_id)
            .group_by(User.id)
            .subquery()
        )
        
        # Находим количество пользователей с большей суммой очков
        stmt = (
            select(func.count())
            .select_from(user_scores)
            .where(user_scores.c.total_score > (
                select(func.sum(Rating.total_score))
                .where(Rating.user_id == user_id)
            ))
        )
        
        result = self.db.execute(stmt)
        rank = result.scalar() or 0
        return rank + 1  # +1 потому что rank это количество людей выше
    
    def get_user_stats(self, user_id: int):
        """
        Возвращает общую статистику пользователя по всем играм
        """
        stmt = (
            select(
                func.sum(Rating.total_score).label('total_score'),
                func.sum(Rating.games_played).label('total_games'),
                func.max(Rating.best_score).label('best_score')
            )
            .where(Rating.user_id == user_id)
        )
        
        result = self.db.execute(stmt)
        return result.first()
    
    def get_top_players_by_game(self, game_id: int, limit: int = 3) -> list:
        """Топ игроков по конкретной игре"""
        stmt = (
            select(Rating, User)
            .join(User, Rating.user_id == User.id)
            .where(Rating.game_id == game_id)
            .order_by(Rating.best_score.desc())
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.all()