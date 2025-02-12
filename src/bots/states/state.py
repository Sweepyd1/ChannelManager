from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_url = State()


class NewGroupState(StatesGroup):
    waiting_for_name = State()
    waiting_for_channel = State()


class NewPostForGroup(StatesGroup):
    waiting_for_post = State()
    group_id = State()


class ScheduleNewPostForGroup(StatesGroup):
    waiting_for_post = State()
    group_id = State()
    waiting_for_date = State()
