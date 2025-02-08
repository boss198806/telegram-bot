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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
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
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Пройти бесплатный курс", callback_data="free_course")],
        [InlineKeyboardButton("💪 Челленджи", callback_data="challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс", callback_data="paid_course")],
        [InlineKeyboardButton("🍽 Меню питания", callback_data="nutrition_menu")],
        [InlineKeyboardButton("👤 Мой кабинет", callback_data="my_cabinet")],
        [InlineKeyboardButton("💡 Как заработать баллы", callback_data="earn_points")],
        [InlineKeyboardButton("💰 Как потратить баллы", callback_data="spend_points")],
        [InlineKeyboardButton("ℹ️ Обо мне", callback_data="about_me")],
        [InlineKeyboardButton("🔗 Реферальная ссылка", callback_data="referral")],
    ])

# Функция для формирования текста кнопки "Отправить отчет" с эмодзи (в зависимости от пола и программы)
def get_report_button_text(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    gender = context.user_data[user_id].get("gender", "male")
    program = context.user_data[user_id].get("program", "home")
    prefix = "👩" if gender == "female" else "👨"
    suffix = "🏠" if program == "home" else "🏋️"
    return f"{prefix}{suffix} Отправить отчет"

# Функция для отправки бесплатного курса (5-дневной тренировки)
async def start_free_course(message, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    if not (context.user_data[user_id].get("gender") == "female" and context.user_data[user_id].get("program") == "home"):
        await message.reply_text("Пока в разработке", reply_markup=main_menu())
        return

    current_day = context.user_data[user_id].get("current_day", 1)
    if current_day > 5:
        await message.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
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
            "2️⃣ Махи под 45 с резинкой (можно без нее) 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
        ],
    }

    exercises = course_program.get(current_day, [])
    caption = f"🔥 **Бесплатный курс: День {current_day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    report_button_text = get_report_button_text(context, user_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(report_button_text, callback_data=f"send_report_day_{current_day}")]
    ])
    try:
        await context.bot.send_photo(
            chat_id=message.chat_id,
            photo=photo_paths.get(current_day),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await message.reply_text(
            "Ошибка: изображение не найдено. Продолжайте без фото.",
            reply_markup=keyboard,
        )

# Функция старта – сначала предлагается выбрать инструктор
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if context.args:
            referrer_id_str = context.args[0]
            try:
                referrer_id = int(referrer_id_str)
                if referrer_id != user_id:
                    user_scores[referrer_id] = user_scores.get(referrer_id, 0) + 100
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text="Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!"
                        )
                    except Exception as e:
                        logger.error(f"Не удалось отправить сообщение о реферальном бонусе пользователю {referrer_id}: {e}")
            except ValueError:
                pass

        context.user_data.setdefault(user_id, {"current_day": 1})
        user_scores[user_id] = user_scores.get(user_id, 0)
        user_status[user_id] = user_status.get(user_id, statuses[0])
        
        instructor_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Евгений Курочкин", callback_data="instructor_1")],
            [InlineKeyboardButton("АНАСТАСИЯ", callback_data="instructor_2")],
            [InlineKeyboardButton("Тренер 3", callback_data="instructor_3")],
            [InlineKeyboardButton("Тренер 4", callback_data="instructor_4")],
            [InlineKeyboardButton("Тренер 5", callback_data="instructor_5")],
        ])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери для себя фитнес инструктора:",
            reply_markup=instructor_keyboard,
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора инструктора
async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()
    if data == "instructor_1":
        context.user_data[user_id]["instructor"] = "evgeniy"
        await query.message.edit_text("Вы выбрали тренера: Евгений Курочкин")
        # Отправляем видео с поддержкой потокового воспроизведения
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://github.com/boss198806/telegram-bot/raw/refs/heads/main/IMG_1484.MOV",
            supports_streaming=True,
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu()
        )
    elif data == "instructor_2":
        context.user_data[user_id]["instructor"] = "anastasiya"
        await query.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ")
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu()
        )
    else:
        if data == "instructor_3":
            selected_name = "Тренер 3"
        elif data == "instructor_4":
            selected_name = "Тренер 4"
        elif data == "instructor_5":
            selected_name = "Тренер 5"
        else:
            selected_name = "неизвестный тренер"
        await query.message.edit_text(
            f"Вы выбрали тренера: {selected_name}. Функционал пока не реализован.\nВы будете перенаправлены в главное меню.",
            reply_markup=main_menu()
        )

# --- Блок выбора пола и программы для бесплатного курса ---
async def handle_free_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "free_course":
        if "gender" not in context.user_data[user_id] or "program" not in context.user_data[user_id]:
            gender_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Мужчина", callback_data="gender_male"),
                 InlineKeyboardButton("Женщина", callback_data="gender_female")]
            ])
            await query.message.reply_text("Ваш пол:", reply_markup=gender_keyboard)
            return
    await start_free_course(query.message, context, user_id)

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data[user_id]["gender"] = "male" if query.data == "gender_male" else "female"
    program_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=program_keyboard)

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data[user_id]["program"] = "home" if query.data == "program_home" else "gym"
    context.user_data[user_id]["current_day"] = 1
    await start_free_course(query.message, context, user_id)
# --- Конец блока выбора пола и программы ---

# Остальной функционал (Меню питания, реферальная ссылка, отправка отчётов, челленджи, платный курс и т.д.) остается без изменений...
# [Далее идут функции handle_nutrition_menu, handle_buy_nutrition_menu, handle_referral, 
#  handle_send_report, handle_video, handle_challenges, buy_challenge, send_challenge_task, handle_challenge_next_day,
#  handle_paid_course, handle_receipt, confirm_payment, handle_my_cabinet, handle_about_me, handle_earn_points, 
#  handle_spend_points, handle_back]

def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_free_course, pattern="^(free_course|next_day)$"))
    application.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    application.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
    # Остальные обработчики: челленджи, платный курс, реферальная ссылка и т.д.
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    application.add_handler(CallbackQueryHandler(buy_challenge, pattern="^buy_challenge$"))
    application.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment_"))
    application.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="^my_cabinet$"))
    application.add_handler(CallbackQueryHandler(handle_about_me, pattern="^about_me$"))
    application.add_handler(CallbackQueryHandler(handle_earn_points, pattern="^earn_points$"))
    application.add_handler(CallbackQueryHandler(handle_spend_points, pattern="^spend_points$"))
    application.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern="^buy_nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))
    application.add_handler(CallbackQueryHandler(handle_challenge_next_day, pattern="^challenge_next$"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
