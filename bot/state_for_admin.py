from aiogram.fsm.state import State, StatesGroup




class CreateNotification(StatesGroup):
    description: State = State()
