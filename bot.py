import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# Словари для хранения данных
user_scores = {}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}
user_waiting_for_challenge_video = {}
user_waiting_for_receipt = {}
user_challenges = {}
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Главное меню
def main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔥 Пройти бесплатный курс", callback_data="free_course")],
            [InlineKeyboardButton("💪 Челленджи", callback_data="challenge_menu")],
            [InlineKeyboardButton("📚 Платный курс", callback_data="paid_course")],
            [InlineKeyboardButton("🍽 Меню питания", callback_data="nutrition_menu")],
            [InlineKeyboardButton("👤 Мой кабинет", callback_data="my_cabinet")],
            [InlineKeyboardButton("💡 Как заработать баллы", callback_data="earn_points")],
            [InlineKeyboardButton("💰 Как потратить баллы", callback_data="spend_points")],
            [InlineKeyboardButton("ℹ️ Обо мне", callback_data="about_me")],
        ]
    )

# Функция старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        context.user_data.setdefault(user_id, {"current_day": 1})
        user_scores[user_id] = user_scores.get(user_id, 0)
        user_status[user_id] = user_status.get(user_id, statuses[0])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/Photo.jpg?raw=true",
            caption="Привет! Я твой фитнес-ассистент!",
            reply_markup=main_menu(),
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Бесплатный курс
async def handle_free_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in context.user_data:
        context.user_data[user_id] = {"current_day": 1}

    if query.data == "next_day":
        context.user_data[user_id]["current_day"] += 1

    current_day = context.user_data[user_id].get("current_day", 1)
    if current_day > 5:
        await query.message.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
        return

    photo_paths = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
    }

    course_program = {
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
            "2️⃣ Махи в бок с колен 3x20 (можно без резинки) [Видео](https://t.me/c/2241417709/385/386)",
            "3️⃣ Косые с касанием пяток 3x15 на каждую [Видео](https://t.me/c/2241417709/282/283)",
        ],
        4: [
            "1️⃣ Поочередные подъемы с гантелями в развороте 4x20 [Видео](https://t.me/c/2241417709/226/227)",
            "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
            "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)",
        ],
        5: [
            "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Махи под 45 с резинкой (можно без нее) 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
        ],
    }

    exercises = course_program.get(current_day, [])
    caption = f"🔥 **Бесплатный курс: День {current_day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"

    photo_path = photo_paths.get(current_day)
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_path,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Отправить отчет", callback_data=f"send_report_day_{current_day}")]]
            ),
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await query.message.reply_text(
            "Ошибка: изображение не найдено. Продолжайте без фото.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Отправить отчет", callback_data=f"send_report_day_{current_day}")]]
            ),
        )

# Челленджи
async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_challenges.get(user_id):
        current_day = user_challenges[user_id]["current_day"]
        await send_challenge_task(query.message, user_id)
    elif user_scores.get(user_id, 0) >= 300:
        buttons = [
            [InlineKeyboardButton("Купить доступ за 300 баллов", callback_data="buy_challenge")],
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]
        await query.message.reply_text(
            "Доступ к челленджам стоит 300 баллов. Хотите приобрести?",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        await query.message.reply_text(
            f"Для доступа к челленджам нужно 300 баллов.\nУ вас: {user_scores.get(user_id, 0)} баллов.\nПродолжайте тренировки!"
        )

# Покупка челленджа
async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id] = {"current_day": 1}
        await query.message.reply_text("✅ Доступ к челленджам открыт!")
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("Недостаточно баллов для покупки доступа!")

# Отправка задания для челленджа
async def send_challenge_task(message: Update, user_id: int):
    current_day = user_challenges[user_id]["current_day"]
    exercises = course_program_challenges.get(current_day, [])
    caption = f"💪 **Челлендж: День {current_day}** 💪\n\n" + "\n".join(exercises)

    await message.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Отправить отчет", callback_data=f"send_challenge_report_{current_day}")]]
        ),
    )

# Программа для челленджей
course_program_challenges = {
    1: [
        "1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
        "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
    ],
    2: [
        "1️⃣ Присед со штангой (можно без) 30 раз [Видео](https://t.me/c/2241417709/140/141)",
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
        "1️⃣ Присед со штангой (можно без) 50 раз [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
        "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)",
    ],
}

# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_free_course, pattern="^free_course|next_day$"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="challenge_menu"))
    application.add_handler(CallbackQueryHandler(buy_challenge, pattern="buy_challenge"))  # Регистрация buy_challenge
    application.add_handler(CallbackQueryHandler(handle_paid_course, pattern="paid_course"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="confirm_payment_.*"))
    application.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="my_cabinet"))
    application.add_handler(CallbackQueryHandler(handle_about_me, pattern="about_me"))
    application.add_handler(CallbackQueryHandler(handle_earn_points, pattern="earn_points"))
    application.add_handler(CallbackQueryHandler(handle_spend_points, pattern="spend_points"))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))

    print("Бот запущен и готов к работе.")
    application.run_polling()


if __name__ == "__main__":
    main()
