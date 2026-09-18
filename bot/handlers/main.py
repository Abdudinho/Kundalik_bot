from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.dp import dp
from bot.buttons.inline import (
    grades_menu,
    letters_menu,
    week_menu,
    lessons_pick_menu,
    after_lessons_menu,
    add_more_menu,
    DAYS,
)
from bot.buttons.reply import admin_menu, student_menu
from bot.db.database import SessionLocal
from bot.db.models import Lesson
from bot.states.lesson_state import LessonState
from bot.utils.roles import is_admin


# ── /start ──────────────────────────────────────────────────────
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    if is_admin(message.from_user.id):
        await message.answer(
            "Salom, Admin! 👋\nKundalik botga xush kelibsiz.",
            reply_markup=admin_menu
        )
    else:
        await message.answer(
            "Salom! Kundalik botga xush kelibsiz.",
            reply_markup=student_menu
        )
        await message.answer("Sinfingizni tanlang:", reply_markup=grades_menu())


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer("@zzxxddab     adminga murojat uchun")


@dp.message(Command("cancel"))
async def cancel_cmd(message: Message, state: FSMContext):
    await state.clear()
    menu = admin_menu if is_admin(message.from_user.id) else student_menu
    await message.answer("Bekor qilindi.", reply_markup=menu)


# ── Sinfni tanlash (Student va Admin uchun umumiy) ───────────────
@dp.message(F.text == "📚 Sinfni tanlash")
async def choose_grade(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Sinfni tanlang:", reply_markup=grades_menu())


# ── grade:{n} bosilganda ──────────────────────────────────────────
@dp.callback_query(F.data.startswith("grade:"))
async def show_letters(callback: CallbackQuery, state: FSMContext):
    grade = int(callback.data.split(":")[1])
    current_state = await state.get_state()

    session = SessionLocal()
    letters = [
        row[0] for row in
        session.query(Lesson.letter)
        .filter(Lesson.grade == grade)
        .distinct()
        .order_by(Lesson.letter)
        .all()
    ]
    session.close()

    # Admin: "Dars qo'shish" oqimi — harf erkin matn sifatida so'raladi
    if current_state == LessonState.add_grade:
        await state.update_data(grade=grade)
        await state.set_state(LessonState.add_letter)
        await callback.message.edit_text(f"{grade}-sinf tanlandi.\nHarfni kiriting (masalan: A):")
        await callback.answer()
        return

    # Admin: "O'zgartirish" / "O'chirish" oqimi — faqat mavjud harflar ko'rsatiladi
    if current_state in (LessonState.edit_grade, LessonState.delete_grade):
        if not letters:
            await callback.message.edit_text(
                f"{grade}-sinf uchun hali dars qo'shilmagan.",
                reply_markup=grades_menu()
            )
            await callback.answer()
            return
        await state.update_data(grade=grade)
        next_state = LessonState.edit_letter if current_state == LessonState.edit_grade else LessonState.delete_letter
        await state.set_state(next_state)
        await callback.message.edit_text(
            f"{grade}-sinf uchun harfni tanlang:",
            reply_markup=letters_menu(grade, letters, show_back=False)
        )
        await callback.answer()
        return

    # Student: sinflarni ko'rish
    if not letters:
        await callback.message.edit_text(
            f"{grade}-sinf uchun hali ma'lumot qo'shilmagan.",
            reply_markup=grades_menu()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{grade}-sinf. Harfni tanlang:",
        reply_markup=letters_menu(grade, letters)
    )
    await callback.answer()


@dp.callback_query(F.data == "back:grades")
async def back_to_grades(callback: CallbackQuery):
    await callback.message.edit_text("Sinfni tanlang:", reply_markup=grades_menu())
    await callback.answer()


# ── class:{grade}:{letter} bosilganda ─────────────────────────────
@dp.callback_query(F.data.startswith("class:"))
async def show_days(callback: CallbackQuery, state: FSMContext):
    _, grade, letter = callback.data.split(":")
    grade = int(grade)
    current_state = await state.get_state()

    if current_state in (LessonState.edit_letter, LessonState.delete_letter):
        await state.update_data(grade=grade, letter=letter)
        next_state = LessonState.edit_day if current_state == LessonState.edit_letter else LessonState.delete_day
        await state.set_state(next_state)
        await callback.message.edit_text(
            f"{grade}-{letter}. Kunni tanlang:",
            reply_markup=week_menu(grade, letter, show_back=False)
        )
        await callback.answer()
        return

    # Student: kunni tanlash
    await callback.message.edit_text(
        f"{grade}-{letter}. Kunni tanlang:",
        reply_markup=week_menu(grade, letter)
    )
    await callback.answer()


# ── day:{grade}:{letter}:{day} bosilganda ─────────────────────────
@dp.callback_query(F.data.startswith("day:"))
async def show_lessons(callback: CallbackQuery, state: FSMContext):
    _, grade, letter, day = callback.data.split(":")
    grade = int(grade)
    current_state = await state.get_state()
    day_name = DAYS.get(day, day)

    # Admin: "Dars qo'shish" oqimi — kundan keyin fan nomi so'raladi
    if current_state == LessonState.add_day:
        await state.update_data(day=day)
        await state.set_state(LessonState.add_subject)
        await callback.message.edit_text(
            f"{day_name} kuni uchun fan nomini kiriting.\n"
            f"Bir nechta fan bo'lsa, har birini alohida qatorga (yoki vergul bilan) yozing:"
        )
        await callback.answer()
        return

    session = SessionLocal()
    lessons = (
        session.query(Lesson)
        .filter(Lesson.grade == grade, Lesson.letter == letter, Lesson.day == day)
        .all()
    )
    session.close()

    # Admin: "O'zgartirish" oqimi — mos darslardan birini tanlash
    if current_state == LessonState.edit_day:
        if not lessons:
            await callback.message.edit_text(f"{grade}-{letter}, {day_name} kuniga dars topilmadi.")
            await state.clear()
            await callback.answer()
            return
        await state.update_data(day=day)
        await state.set_state(LessonState.edit_pick)
        await callback.message.edit_text(
            "O'zgartirish uchun darsni tanlang:",
            reply_markup=lessons_pick_menu(lessons)
        )
        await callback.answer()
        return

    # Admin: "O'chirish" oqimi — mos darslardan birini tanlash
    if current_state == LessonState.delete_day:
        if not lessons:
            await callback.message.edit_text(f"{grade}-{letter}, {day_name} kuniga dars topilmadi.")
            await state.clear()
            await callback.answer()
            return
        await state.update_data(day=day)
        await state.set_state(LessonState.delete_pick)
        await callback.message.edit_text(
            "O'chirish uchun darsni tanlang:",
            reply_markup=lessons_pick_menu(lessons)
        )
        await callback.answer()
        return

    # Student: darslarni va xonalarini ko'rsatish
    if not lessons:
        text = f"📅 {day_name}\n🏫 {grade}-{letter}\n\nBu kunga dars qo'shilmagan."
    else:
        lines = [f"📅 {day_name} — {grade}-{letter} sinf darslari:\n"]
        for l in lessons:
            room = l.room if l.room else "belgilanmagan"
            lines.append(f"📖 {l.subject} — {room}-xona")
        text = "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=after_lessons_menu(grade, letter))
    await callback.answer()


# ── Admin: Dars qo'shish ───────────────────────────────────────────
@dp.message(F.text == "➕ Dars qo'shish")
async def add_lesson_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⚠️ Bu buyruq faqat Admin uchun.")
        return
    await state.set_state(LessonState.add_grade)
    await message.answer("Qaysi sinf uchun dars qo'shmoqchisiz?", reply_markup=grades_menu())


@dp.message(LessonState.add_letter)
async def add_lesson_letter(message: Message, state: FSMContext):
    letter = message.text.strip().upper()
    if not letter or ":" in letter or len(letter) > 5:
        await message.answer("Harfni to'g'ri kiriting (masalan: A). Qaytadan urinib ko'ring:")
        return
    data = await state.get_data()
    await state.update_data(letter=letter)
    await state.set_state(LessonState.add_day)
    await message.answer(
        f"{data['grade']}-{letter}. Qaysi kun?",
        reply_markup=week_menu(data["grade"], letter, show_back=False)
    )


def _parse_multi(text: str) -> list[str]:
    """Ko'p qiymatni ajratib olish: avval qator bo'yicha, bitta qator bo'lsa vergul bo'yicha."""
    items = [line.strip() for line in text.split("\n") if line.strip()]
    if len(items) == 1 and "," in items[0]:
        items = [part.strip() for part in items[0].split(",") if part.strip()]
    return items


@dp.message(LessonState.add_subject)
async def add_lesson_subject(message: Message, state: FSMContext):
    subjects = _parse_multi(message.text)
    if not subjects:
        await message.answer("Fan nomini kiriting:")
        return
    await state.update_data(subjects=subjects)
    await state.set_state(LessonState.add_room)
    if len(subjects) == 1:
        await message.answer("Xona raqamini kiriting (masalan: 205):")
    else:
        numbered = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(subjects))
        await message.answer(
            f"{len(subjects)} ta fan qabul qilindi:\n{numbered}\n\n"
            f"Endi shu tartibda xonalarni kiriting — har birini alohida qatorga "
            f"(yoki vergul bilan) yozing:"
        )


@dp.message(LessonState.add_room)
async def add_lesson_room(message: Message, state: FSMContext):
    data = await state.get_data()
    subjects = data["subjects"]
    rooms = _parse_multi(message.text)

    if len(rooms) != len(subjects):
        await message.answer(
            f"⚠️ Fanlar soni ({len(subjects)}) bilan xonalar soni ({len(rooms)}) mos kelmadi.\n"
            f"Xonalarni qaytadan, {len(subjects)} ta fan bilan bir xil tartibda kiriting:"
        )
        return

    session = SessionLocal()
    for subject, room in zip(subjects, rooms):
        session.add(Lesson(
            grade=data["grade"],
            letter=data["letter"],
            day=data["day"],
            subject=subject,
            room=room,
        ))
    session.commit()
    session.close()

    day_name = DAYS.get(data["day"], data["day"])
    summary = "\n".join(f"📖 {s} — {r}-xona" for s, r in zip(subjects, rooms))
    await state.set_state(LessonState.add_more)
    await message.answer(
        f"✅ Qo'shildi:\n{summary}\n\n"
        f"{data['grade']}-{data['letter']}, {day_name} kuniga yana dars qo'shasizmi?",
        reply_markup=add_more_menu()
    )


@dp.callback_query(LessonState.add_more, F.data.startswith("addmore:"))
async def add_more_lesson(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    data = await state.get_data()
    if choice == "yes":
        await state.set_state(LessonState.add_subject)
        await callback.message.edit_text(
            "Yana fan nomini kiriting.\n"
            "Bir nechta bo'lsa, har birini alohida qatorga (yoki vergul bilan) yozing:"
        )
    else:
        day_name = DAYS.get(data["day"], data["day"])
        await callback.message.edit_text(
            f"✅ {data['grade']}-{data['letter']}, {day_name} kuni uchun darslar kiritish yakunlandi."
        )
        await state.clear()
        await callback.message.answer("Bosh menyu:", reply_markup=admin_menu)
    await callback.answer()


# ── Admin: Darsni o'zgartirish ─────────────────────────────────────
@dp.message(F.text == "✏️ Darsni o'zgartirish")
async def edit_lesson_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⚠️ Bu buyruq faqat Admin uchun.")
        return
    await state.set_state(LessonState.edit_grade)
    await message.answer("Qaysi sinf darsini o'zgartirmoqchisiz?", reply_markup=grades_menu())


@dp.callback_query(LessonState.edit_pick, F.data.startswith("pick:"))
async def edit_pick_lesson(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])
    await state.update_data(lesson_id=lesson_id)
    await state.set_state(LessonState.edit_new_subject)
    await callback.message.edit_text("Yangi fan nomini kiriting:")
    await callback.answer()


@dp.message(LessonState.edit_new_subject)
async def edit_new_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text.strip())
    await state.set_state(LessonState.edit_new_room)
    await message.answer("Yangi xona raqamini kiriting:")


@dp.message(LessonState.edit_new_room)
async def edit_new_room(message: Message, state: FSMContext):
    data = await state.get_data()
    session = SessionLocal()
    lesson = session.query(Lesson).filter(Lesson.id == data["lesson_id"]).first()
    if lesson:
        lesson.subject = data["subject"]
        lesson.room = message.text.strip()
        session.commit()
        await message.answer("✅ Dars o'zgartirildi.", reply_markup=admin_menu)
    else:
        await message.answer("❌ Dars topilmadi.", reply_markup=admin_menu)
    session.close()
    await state.clear()


# ── Admin: Darsni o'chirish ─────────────────────────────────────────
@dp.message(F.text == "❌ Darsni o'chirish")
async def delete_lesson_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⚠️ Bu buyruq faqat Admin uchun.")
        return
    await state.set_state(LessonState.delete_grade)
    await message.answer("Qaysi sinf darsini o'chirmoqchisiz?", reply_markup=grades_menu())


@dp.callback_query(LessonState.delete_pick, F.data.startswith("pick:"))
async def delete_pick_lesson(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])
    session = SessionLocal()
    lesson = session.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson:
        session.delete(lesson)
        session.commit()
        await callback.message.edit_text("✅ Dars muvaffaqiyatli o'chirildi.")
    else:
        await callback.message.edit_text("❌ Dars topilmadi.")
    session.close()
    await state.clear()
    await callback.answer()
