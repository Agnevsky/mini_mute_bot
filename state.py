from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    waiting_name = State()
    waiting_team = State()

