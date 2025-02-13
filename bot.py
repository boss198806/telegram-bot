import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
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

# Обработчики для курсов
async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    trainer = query.data.split("_")[-1]
    context.user_data["instructor"] = trainer
    await query.message.edit_text(f"Вы выбрали тренера: {trainer.title()}.\n\nТеперь выберите пол:")

    gender_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Мужчина", callback_data="gender_male"),
         InlineKeyboardButton("Женщина", callback_data="gender_female")]
    ])
    await query.message.reply_text("Выберите пол:", reply_markup=gender_keyboard)

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    gender = "male" if query.data == "gender_male" else "female"
    context.user_data["gender"] = gender

    # После выбора пола - выбор дома или в зале
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Дома", callback_data="program_home"),
         InlineKeyboardButton("В зале", callback_data="program_gym")]
    ])
    await query.message.edit_text("Выберите, где вы будете тренироваться:", reply_markup=keyboard)

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    program_type = query.data.split("_")[-1]  # "home" или "gym"
    context.user_data["program"] = program_type

    # Показ программы курса
    trainer = context.user_data["instructor"]
    day_buttons = day_menu(f"{trainer}_{program_type}")
    program_text = f"Программа для тренера {trainer.title()}, дня {context.user_data['current_day']}"
    await query.message.edit_text(program_text, reply_markup=day_buttons)

async def handle_send_free_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    course_type, day = user_waiting_for_video[user_id]
    
    if course_type == "free":
        # Отправка отчета в группу
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от пользователя {user_id} за бесплатный курс, День {day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        # Начисление баллов
        user_scores[user_id] = user_scores.get(user_id, 0) + 60
        reply_text = f"Отчет за День {day} принят! Вам начислено 60 баллов."
        del user_waiting_for_video[user_id]
        await update.message.reply_text(reply_text, reply_markup=main_menu())

# Запуск приложения
def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern=r"^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_gender, pattern=r"^gender_"))
    application.add_handler(CallbackQueryHandler(handle_program, pattern=r"^program_"))
    application.add_handler(CallbackQueryHandler(handle_send_free_report, pattern=r"^send_free_report_\d+"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
