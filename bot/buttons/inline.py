from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

GRADES = range(1, 12)  # 1-11 sinflar

DAYS = {
    "monday": "Dushanba",
    "tuesday": "Seshanba",
    "wednesday": "Chorshanba",
    "thursday": "Payshanba",
    "friday": "Juma",
    "saturday": "Shanba",
}


def grades_menu() -> InlineKeyboardMarkup:
    """1-11 sinflar ro'yxati (Student uchun ham, Admin uchun ham)."""
    buttons = [
        InlineKeyboardButton(text=f"{g}-sinf", callback_data=f"grade:{g}")
        for g in GRADES
    ]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def letters_menu(grade: int, letters: list[str], show_back: bool = True) -> InlineKeyboardMarkup:
    """Berilgan sinf uchun Admin qo'shgan harflar ro'yxati (masalan: 9-A, 9-B)."""
    rows = [
        [InlineKeyboardButton(text=f"{grade}-{letter}", callback_data=f"class:{grade}:{letter}")]
        for letter in letters
    ]
    if show_back:
        rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back:grades")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def week_menu(grade: int, letter: str, show_back: bool = True) -> InlineKeyboardMarkup:
    """Tanlangan sinf uchun hafta kunlari."""
    rows = [
        [InlineKeyboardButton(text=name, callback_data=f"day:{grade}:{letter}:{code}")]
        for code, name in DAYS.items()
    ]
    if show_back:
        rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"grade:{grade}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lessons_pick_menu(lessons) -> InlineKeyboardMarkup:
    """Admin uchun: o'zgartirish/o'chirish uchun aniq darsni tanlash ro'yxati."""
    rows = [
        [InlineKeyboardButton(text=f"{l.subject} ({l.room or '—'})", callback_data=f"pick:{l.id}")]
        for l in lessons
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def after_lessons_menu(grade: int, letter: str) -> InlineKeyboardMarkup:
    """Student darslarni ko'rgandan keyin: boshqa kun yoki boshqa sinfga o'tish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Kunni almashtirish", callback_data=f"class:{grade}:{letter}")],
        [InlineKeyboardButton(text="📚 Boshqa sinf", callback_data="back:grades")],
    ])


def add_more_menu() -> InlineKeyboardMarkup:
    """Admin bitta dars qo'shgandan keyin: shu kunga yana dars qo'shish yoki tugatish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yana dars qo'shish", callback_data="addmore:yes")],
        [InlineKeyboardButton(text="✅ Tugatish", callback_data="addmore:no")],
    ])
