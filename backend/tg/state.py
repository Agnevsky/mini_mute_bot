from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    waiting_name = State()
    waiting_team = State()

    waiting_result_game = State()

    waiting_edit_choice: str = State()
    waiting_edit_result: str = State()

