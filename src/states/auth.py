from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


class RegisterStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()
