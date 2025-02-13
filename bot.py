import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")

# Глобальные словари и константы
user_scores = {}  # общий счет пользователя
user_status = {}  # статус пользователя
user_reports_sent = {}  # {user_id: {day: bool}} – отчеты по курсам
user_waiting_for_video = {}  # для хранения данных о том, что ожидается видео

trainer_scores = {
    "evgeniy": {},
    "anastasia": {},
}

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Программы для бесплатного курса (5 дней)
free_course_program = {
    1: [
        "1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
        "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
        "3️⃣ Велосипед 3x15 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
    ],
    2: [
        "1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/c/2241417709/167/168)",
        "2️⃣ Лодочка прямые руки 3x30 [Видео](https://t.me/c/2241417709/395/396)",
        "3️⃣ Полные подъёмы корпуса 3x20 [Видео](https://t.me/c/2241417709/274/275)",
    ],
    3: [
        "1️⃣ Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Махи в бок с колен 3x20 [Видео](https://t.me/c/2241417709/385/386)",
        "3️⃣ Косые с касанием пяток 3x15 [Видео](https://t.me/c/2241417709/282/283)",
    ],
    4: [
        "1️⃣ Поочередные подъемы с гантелями в развороте 4x20 [Видео](https://t.me/c/2241417709/226/227)",
        "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
        "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)",
    ],
    5: [
        "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Махи под 45 с резинкой 3x20 [Видео](https://t.me/c/2241417709/339/340)",
        "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
    ],
}

# Программа для платного курса (5 дней)
paid_course_program = {
    1: [
        "1️⃣ Жим лежа 3x12 [Видео](https://t.me/c/2241417709/500/501)",
        "2️⃣ Тяга верхнего блока 3x15 [Видео](https://t.me/c/2241417709/502/503)",
        "3️⃣ Приседания 3x15 [Видео](https://t.me/c/2241417709/504/505)",
    ],
    2: [
        "1️⃣ Жим гантелей 3x12 [Видео](https://t.me/c/2241417709/506/507)",
        "2️⃣ Разводка рук 3x15 [Видео](https://t.me/c/2241417709/508/509)",
        "3️⃣ Подтягивания 3x10 [Видео](https://t.me/c/2241417709/510/511)",
    ],
    3: [
        "1️⃣ Становая тяга 3x10 [Видео](https://t.me/c/2241417709/512/513)",
        "2️⃣ Пресс 3x20 [Видео](https://t.me/c/2241417709/514/515)",
    ],
    4: [
        "1️⃣ Выпады 3x15 [Видео](https://t.me/c/2241417709/516/517)",
        "2️⃣ Пуловер 3x12 [Видео](https://t.me/c/2241417709/518/519)",
        "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/520/521)",
    ],
    5: [
        "1️⃣ Жим штанги 3x12 [Видео](https://t.me/c/2241417709/522/523)",
        "2️⃣ Тяга гантелей 3x15 [Видео](https://t.me/c/2241417709/524/525)",
        "3️⃣ Приседания с гантелями 3x15 [Видео](https://t.me/c/2241417709/526/527)",
    ],
}

# Программа для челленджей (5 дней)
challenge_program = {
    1: [
        "1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
        "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
    ],
    2: [
        "1️⃣ Присед со штангой 30 раз [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Отжимания с отрывом рук 25 раз [Видео](https://t.me/c/2241417709/393/394)",
        "3️⃣ Полные подъёмы корпуса 30 раз [Видео](https://t.me/c/2241417709/274/275)",
    ],
    3: [
        "1️⃣ Планка 3 мин [Видео](https://t.me/c/2241417709/286/296)",
        "2️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
    ],
    4: [
        "1️⃣ Выпады назад 60 раз [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
        "3️⃣ Велосипед 50 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
    ],
    5: [
        "1️⃣ Присед со штангой 50 раз [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
        "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)",
    ],
}

# Функции для создания меню выбора дня
def day_menu(course_type: str):
    buttons = []
    for i in range(1, 6):
        buttons.append(InlineKeyboardButton(f"День {i}", callback_data=f"{course_type}_day_{i}"))
    return InlineKeyboardMarkup([buttons])

# Команды для запуска и выбора тренера
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data.setdefault(user_id, {"current_day": 1})
    await update.message.reply_text(
        "Привет! Добро пожаловать в фитнес-бот. Выберите инструктора.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Евгений Курочкин", callback_data="instructor_evgeniy")],
            [InlineKeyboardButton("АНАСТАСИЯ", callback_data="instructor_anastasia")]
        ])
    )

async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    trainer = query.data.split("_", 1)[-1]
    user_id = query.from_user.id
    context.user_data.setdefault(user_id, {})["current_day"] = 1
    context.user_data[user_id]["instructor"] = trainer
    await query.message.edit_text(f"Вы выбрали тренера: {trainer.title()}")
    await send_trainer_menu(context, query.message.chat_id, trainer)
    await query.message.reply_text("Выберите день курса:", reply_markup=day_menu("free"))

async def send_trainer_menu(context: ContextTypes.DEFAULT_TYPE, chat_id: int, trainer: str):
    caption = f"Вы выбрали тренера: {trainer.title()}"
    trainer_media = {
        "evgeniy": {"type": "video", "url": "https://example.com/video"},
        "anastasia": {"type": "photo", "url": "https://example.com/photo.jpg"},
    }
    media = trainer_media.get(trainer)
    if media:
        if media["type"] == "video":
            await context.bot.send_video(chat_id=chat_id, video=media["url"], caption=caption, reply_markup=main_menu())
        else:
            await context.bot.send_photo(chat_id=chat_id, photo=media["url"], caption=caption, reply_markup=main_menu())

# Обработчики для курсов
async def handle_free_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    day = int(query.data.split("_")[-1])
    program = free_course_program.get(day, [])
    text = f"**Бесплатный курс: День {day}**\n\n" + "\n".join(program)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data=f"send_free_report_{day}")]
    ])
    user_id = query.from_user.id
    user_waiting_for_video[user_id] = ("free", day)
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_paid_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    day = int(query.data.split("_")[-1])
    program = paid_course_program.get(day, [])
    text = f"**Платный курс: День {day}**\n\n" + "\n".join(program)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data=f"send_paid_report_{day}")]
    ])
    user_id = query.from_user.id
    user_waiting_for_video[user_id] = ("paid", day)
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_challenge_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    day = int(query.data.split("_")[-1])
    program = challenge_program.get(day, [])
    text = f"**Челлендж: День {day}**\n\n" + "\n".join(program)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data=f"send_challenge_report_{day}")]
    ])
    user_id = query.from_user.id
    user_waiting_for_video[user_id] = ("challenge", day)
    await query.edit_message_text(text, reply_markup=keyboard)

# Обработка видео-отчета
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_waiting_for_video:
        course_type, day = user_waiting_for_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от пользователя {user_id} за {course_type} курс, День {day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        if course_type == "free":
            user_scores[user_id] = user_scores.get(user_id, 0) + 60
            reply_text = f"Отчет за День {day} принят! Вам начислено 60 баллов."
        elif course_type == "challenge":
            user_scores[user_id] = user_scores.get(user_id, 0) + 60
            reply_text = f"Отчет за День {day} принят! Вам начислено 60 баллов."
        elif course_type == "paid":
            user_scores[user_id] = user_scores.get(user_id, 0) + 30
            reply_text = f"Отчет за День {day} принят! Вам начислено 30 баллов."
        del user_waiting_for_video[user_id]
        await update.message.reply_text(reply_text, reply_markup=main_menu())

# Запуск приложения
def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern=r"^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_free_day, pattern=r"^free_day_\d+"))
    application.add_handler(CallbackQueryHandler(handle_paid_day, pattern=r"^paid_day_\d+"))
    application.add_handler(CallbackQueryHandler(handle_challenge_day, pattern=r"^challenge_day_\d+"))
    application.add_handler(CallbackQueryHandler(handle_send_free_report, pattern=r"^send_free_report_\d+"))
    application.add_handler(CallbackQueryHandler(handle_send_paid_report, pattern=r"^send_paid_report_\d+"))
    application.add_handler(CallbackQueryHandler(handle_send_challenge_report, pattern=r"^send_challenge_report_\d+"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
