from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Sinfni tanlash")],
        [KeyboardButton(text="➕ Dars qo'shish")],
        [KeyboardButton(text="✏️ Darsni o'zgartirish")],
        [KeyboardButton(text="❌ Darsni o'chirish")],
    ],
    resize_keyboard=True
)

student_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Sinfni tanlash")],
    ],
    resize_keyboard=True
)
