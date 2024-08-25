from aiogram.fsm.state import State, StatesGroup




class NewBooking(StatesGroup):
    personal_link: State = State()
    date: State = State()
    time: State = State()
    name: State = State()
    email: State = State()
    phone_number: State = State()