# app/database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Пользователи Telegram"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)  # ID из Telegram
    username = Column(String(100), nullable=True)      # @username
    first_name = Column(String(100), nullable=False)   # Имя
    last_name = Column(String(100), nullable=True)     # Фамилия
    language_code = Column(String(10), default='ru')   # Язык
    is_blocked = Column(Boolean, default=False)        # Заблокирован?
    block_reason = Column(Text, nullable=True)         # Причина блокировки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    game_sessions = relationship("GameSession", back_populates="user")
    ratings = relationship("Rating", back_populates="user")

class Game(Base):
    """Доступные игры"""
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)        # "Угадай число"
    code = Column(String(50), unique=True, nullable=False)         # "guess_number"
    description = Column(Text)                                     # Описание игры
    is_active = Column(Boolean, default=True)                      # Включена ли игра
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    game_sessions = relationship("GameSession", back_populates="game")
    ratings = relationship("Rating", back_populates="game")

class GameSession(Base):
    """Сессии игр (каждая игра пользователя)"""
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    score = Column(Integer, default=0)                             # Очки в этой сессии
    attempts = Column(Integer, default=0)                          # Количество попыток
    completed = Column(Boolean, default=False)                     # Завершена ли игра
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)                  # Когда завершилась
    
    # Связи
    user = relationship("User", back_populates="game_sessions")
    game = relationship("Game", back_populates="game_sessions")

class Rating(Base):
    """Рейтинги игроков по играм (агрегированные данные)"""
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    total_score = Column(Integer, default=0)                       # Сумма всех очков
    games_played = Column(Integer, default=0)                      # Количество сыгранных игр
    best_score = Column(Integer, default=0)                        # Лучший результат
    average_score = Column(Float, default=0.0)                     # Средний результат
    last_played = Column(DateTime, nullable=True)                  # Последняя игра
    
    # Связи
    user = relationship("User", back_populates="ratings")
    game = relationship("Game", back_populates="ratings")
    
    # Уникальность пары пользователь-игра
    __table_args__ = (UniqueConstraint('user_id', 'game_id', name='unique_user_game'),)

class Admin(Base):
    """Таблица администраторов"""
    __tablename__ = 'admins'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    added_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Связи
    user = relationship("User", foreign_keys=[user_id])
    added_by_user = relationship("User", foreign_keys=[added_by])


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    option1 = Column(String(200), nullable=False)
    option2 = Column(String(200), nullable=False)
    option3 = Column(String(200), nullable=False)
    option4 = Column(String(200), nullable=False)
    correct_option = Column(Integer, nullable=False)  # 1-4
    difficulty = Column(String(20), default='medium')  # easy/medium/hard
    category = Column(String(50), nullable=False)
    explanation = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class City(Base):
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # "Москва"
    region = Column(String(100), nullable=True)              # "Московская область"

    