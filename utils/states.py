from aiogram.fsm.state import State, StatesGroup

class GuessNumberState(StatesGroup):
    playing = State()  # Состояние активной игры "Угадай число"

class AdminStates(StatesGroup):
    waiting_user_id = State()          # Для добавления/удаления админа
    waiting_ban_user_id = State()      # Для блокировки пользователя (ID)
    waiting_ban_reason = State()       # Для блокировки пользователя (причина)
    waiting_broadcast = State()        # Для рассылки сообщения

class QuizStates(StatesGroup):
    playing = State()              # Основное состояние игры
    waiting_answer = State()       # Ожидание ответа пользователя

class CitiesStates(StatesGroup):
    playing = State()        # Основное состояние игры
    waiting_city = State()   # Ожидание города от пользователя