from sqlalchemy import func
from database.models import QuizQuestion
from repositories.base_repository import BaseRepository

class QuizRepository(BaseRepository):    
    def get_questions_by_difficulty(self, difficulty: str, limit: int = 10):
        return self.db.query(QuizQuestion)\
            .where(QuizQuestion.difficulty == difficulty)\
            .where(QuizQuestion.is_active == True)\
            .limit(limit)\
            .all()
    
    def get_random_questions(self, limit: int = 10):
        return self.db.query(QuizQuestion)\
            .where(QuizQuestion.is_active == True)\
            .order_by(func.random())\
            .limit(limit)\
            .all()
    
    def get_questions_by_category(self, category: str, limit: int = 10):
        return self.db.query(QuizQuestion)\
            .where(QuizQuestion.category == category)\
            .where(QuizQuestion.is_active == True)\
            .limit(limit)\
            .all()
    
    def get_balanced_questions(self, easy: int = 3, medium: int = 3, hard: int = 2):
        """Получает сбалансированный набор вопросов по сложности"""
        easy_questions = self.get_questions_by_difficulty("easy", easy)
        medium_questions = self.get_questions_by_difficulty("medium", medium) 
        hard_questions = self.get_questions_by_difficulty("hard", hard)
        
        # Объединяем вопросы
        all_questions = easy_questions + medium_questions + hard_questions
        return all_questions