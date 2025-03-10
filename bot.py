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

# Конфигурация бота
TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# Данные тренеров
INSTRUCTORS = {
    "evgeniy": {
        "name": "Евгений Курочкин",
        "photo": "https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
        "video": "https://t.me/PRIVETSTVIEC/2",
        "courses": {
            "free": {
                1: {
                    "photo": "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
                    "exercises": [
                        "1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
                        "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
                        "3️⃣ Велосипед 3x15 [Видео](https://t.me/c/2241417709/278/279)"
                    ]
                },
                # Дни 2-5 аналогично
            },
            "paid": {
                1: {
                    "exercises": [
                        "Махи назад с утяжелителями 3х25+5 [Видео](https://t.me/c/2241417709/337/338)",
                        "Выпады 3х30 шагов х 2кг [Видео](https://t.me/c/2241417709/157/158)",
                        "Разведение ног 3х20 [Видео](https://t.me/c/2241417709/128/129)",
                        "Сведение ног 3х20 [Видео](https://t.me/c/2241417709/126/127)",
                        "Сгибание ног 3х15 [Видео](https://t.me/c/2241417709/130/131)"
                    ]
                },
                # Дни 2-5 аналогично
            }
        }
    },
    "anastasiya": {
        "name": "АНАСТАСИЯ",
        "photo": "https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
        "courses": {
            "free": {
                1: {
                    "photo": "https://example.com/anastasiya_day1.jpg",
                    "exercises": [
                        "1️⃣ Упражнение А1 [Видео](https://example.com)",
                        "2️⃣ Упражнение А2 [Видео](https://example.com)"
                    ]
                }
            }
        }
    }
}

# Статусы пользователей
STATUSES = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Универсальные клавиатуры
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=cb)] for text, cb in [
            ("🔥 Пройти бесплатный курс", "free_course"),
            ("💪 Челленджи", "challenge_menu"),
            ("📚 Платный курс", "paid_course"),
            ("🍽 Меню питания", "nutrition_menu"),
            ("👤 Мой кабинет", "my_cabinet"),
            ("💡 Как заработать баллы", "earn_points"),
            ("💰 Как потратить баллы", "spend_points"),
            ("ℹ️ Обо мне", "about_me"),
            ("🔗 Реферальная ссылка", "referral")
        ]
    ])

def instructor_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for i, (key, data) in enumerate(INSTRUCTORS.items()):
        if i % 2 == 0 and i != 0:
            buttons.append([])
        btn = InlineKeyboardButton(data["name"], callback_data=f"instructor_{key}")
        if len(buttons) == 0 or len(buttons[-1]) == 2:
            buttons.append([btn])
        else:
            buttons[-1].append(btn)
    return InlineKeyboardMarkup(buttons)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.send_message(
        chat_id=user.id,
        text="Выберите тренера:",
        reply_markup=instructor_keyboard()
    )

async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    instructor_key = query.data.split('_')[1]
    instructor = INSTRUCTORS[instructor_key]
    
    # Сохраняем выбор тренера
    context.user_data[query.from_user.id] = {
        "instructor": instructor_key,
        "scores": 0,
        "reports": {},
        "current_day": 1,
        "status": STATUSES[0],
        "paid_access": False
    }
    
    # Отправляем приветственное сообщение
    if "video" in instructor:
        await query.message.reply_video(
            video=instructor["video"],
            caption=f"🎥 Привет! Я {instructor['name']} - ваш фитнес-ассистент!",
            reply_markup=main_menu()
        )
    else:
        await query.message.reply_photo(
            photo=instructor["photo"],
            caption=f"📸 Привет! Я {instructor['name']} - ваш фитнес-ассистент!",
            reply_markup=main_menu()
        )

async def handle_free_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data.get(query.from_user.id)
    
    if not user_data or "instructor" not in user_data:
        await query.answer("Сначала выберите тренера!")
        return
    
    instructor = INSTRUCTORS[user_data["instructor"]]
    current_day = user_data["current_day"]
    
    if current_day > 5:
        await query.message.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
        return
    
    day_data = instructor["courses"]["free"].get(current_day, {})
    text = f"🔥 {instructor['name']} - День {current_day}\n\n" + "\n".join(day_data.get("exercises", []))
    
    await query.message.reply_photo(
        photo=day_data.get("photo"),
        caption=text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📹 Отправить отчет", callback_data=f"report_day_{current_day}")
        ]])
    )

async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data.get(query.from_user.id)
    
    if not user_data or "instructor" not in user_data:
        await query.answer("Сначала выберите тренера!")
        return
    
    if user_data["paid_access"]:
        await query.message.reply_text("Вы уже приобрели платный курс! 🎉", reply_markup=main_menu())
        return
    
    price = 2000 - min(user_data["scores"] * 2, 600)
    text = (
        f"📚 Платный курс\n\n"
        f"Стоимость: {price} руб.\n"
        f"Ваши баллы: {user_data['scores']} (1 балл = 2 руб. скидки)\n\n"
        f"После оплаты отправьте чек для подтверждения."
    )
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🧾 Отправить чек", callback_data="send_receipt")
        ]])
    )

async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data.get(query.from_user.id)
    
    if not user_data or "instructor" not in user_data:
        await query.answer("Сначала выберите тренера!")
        return
    
    text = (
        "🍽 Меню питания\n\n"
        "Ссылка на меню питания: https://t.me/MENUKURO4KIN/2\n\n"
        "Для покупки меню питания нажмите кнопку ниже."
    )
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("💰 Купить меню за 300 баллов", callback_data="buy_nutrition_menu")
        ]])
    )

async def handle_earn_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data.get(query.from_user.id)
    
    if not user_data or "instructor" not in user_data:
        await query.answer("Сначала выберите тренера!")
        return
    
    text = (
        "💡 Как заработать баллы:\n\n"
        "1. Проходите бесплатный курс и отправляйте видеоотчеты.\n"
        "2. Участвуйте в челленджах.\n"
        "3. Приглашайте друзей по реферальной ссылке.\n"
        "4. Покупайте платный курс и получайте дополнительные баллы."
    )
    
    await query.message.reply_text(text, reply_markup=main_menu())

async def handle_spend_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data.get(query.from_user.id)
    
    if not user_data or "instructor" not in user_data:
        await query.answer("Сначала выберите тренера!")
        return
    
    text = (
        "💰 Как потратить баллы:\n\n"
        "1. Скидка на платный курс (1 балл = 2 рубля).\n"
        "2. Покупка меню питания (300 баллов).\n"
        "3. Дополнительные материалы и консультации."
    )
    
    await query.message.reply_text(text, reply_markup=main_menu())

async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data.get(query.from_user.id)
    
    if not user_data or "instructor" not in user_data:
        await query.answer("Сначала выберите тренера!")
        return
    
    instructor = INSTRUCTORS[user_data["instructor"]]
    
    text = (
        f"ℹ️ О тренере: {instructor['name']}\n\n"
        "Общий тренировочный стаж - 20 лет\n"
        "Стаж работы - 15 лет\n"
        "МС - по становой тяге\n"
        "МС - по жиму штанги лежа\n"
        "Судья - федеральной категории\n"
        "Организатор соревнований\n"
        "КМС - по бодибилдингу\n\n"
        "20 лет в фитнесе! 💥"
    )
    
    await query.message.reply_photo(
        photo=instructor["photo"],
        caption=text,
        reply_markup=main_menu()
    )

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data.get(query.from_user.id)
    
    if not user_data or "instructor" not in user_data:
        await query.answer("Сначала выберите тренера!")
        return
    
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={query.from_user.id}"
    
    text = (
        "🔗 Реферальная ссылка\n\n"
        f"Ваша ссылка: {referral_link}\n\n"
        "Поделитесь этой ссылкой с друзьями. За каждого нового пользователя вы получите 100 баллов!"
    )
    
    await query.message.reply_text(text, reply_markup=main_menu())

# Основная функция
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern=r'^instructor_'))
    app.add_handler(CallbackQueryHandler(handle_free_course, pattern='^free_course$'))
    app.add_handler(CallbackQueryHandler(handle_paid_course, pattern='^paid_course$'))
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern='^nutrition_menu$'))
    app.add_handler(CallbackQueryHandler(handle_earn_points, pattern='^earn_points$'))
    app.add_handler(CallbackQueryHandler(handle_spend_points, pattern='^spend_points$'))
    app.add_handler(CallbackQueryHandler(handle_about_me, pattern='^about_me$'))
    app.add_handler(CallbackQueryHandler(handle_referral, pattern='^referral$'))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video_report))
    
    logger.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
