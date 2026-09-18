from aiogram.fsm.state import State, StatesGroup


class LessonState(StatesGroup):
    # Admin: dars qo'shish
    add_grade = State()
    add_letter = State()
    add_day = State()
    add_subject = State()
    add_room = State()
    add_more = State()

    # Admin: darsni o'zgartirish
    edit_grade = State()
    edit_letter = State()
    edit_day = State()
    edit_pick = State()
    edit_new_subject = State()
    edit_new_room = State()

    # Admin: darsni o'chirish
    delete_grade = State()
    delete_letter = State()
    delete_day = State()
    delete_pick = State()
