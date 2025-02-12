import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from evgeniy import start_free_course as evgeniy_start_free_course, handle_send_report as evgeniy_handle_send_report
from anastasia import start_free_course as anastasia_start_free_course, handle_send_report as anastasia_handle_send_report
from common import main_menu

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токена из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ID вашего группового чата (это необходимо для отправки сообщений в группу)
GROUP_ID = "-1002451371911"

# Функция /start для приветствия пользователя
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start. Приветствие и выбор тренера."""
    user_id = update.effective_user.id
    ctx.user_data.setdefault(user_id, {"current_day": 1})
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_1")],
        [InlineKeyboardButton("💫 Анастасия", callback_data="instructor_2")],
        [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
        [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
        [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")],
    ])
    await update.message.reply_text("Привет! Я твой фитнес-ассистент! Выберите тренера:", reply_markup=kb)

# Обработчик выбора тренера
async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора тренера пользователем (Евгений или Анастасия)."""
    query = update.callback_query
    user_id = query.from_user.id

    # Сохраняем выбор тренера
    if query.data == "instructor_1":
        ctx.user_data[user_id]["instructor"] = "evgeniy"
    elif query.data == "instructor_2":
        ctx.user_data[user_id]["instructor"] = "anastasia"
    else:
        ctx.user_data[user_id]["instructor"] = query.data  # Для других тренеров

    # Отправляем меню для выбора курса и других опций
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Пройти бесплатный курс", callback_data="free_course")],
        [InlineKeyboardButton("💪 Челленджи", callback_data="challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс", callback_data="paid_course")],
        [InlineKeyboardButton("🍽 Меню питания", callback_data="nutrition_menu")],
        [InlineKeyboardButton("👤 Мой кабинет", callback_data="my_cabinet")],
        [InlineKeyboardButton("💡 Как заработать баллы", callback_data="earn_points")],
        [InlineKeyboardButton("💰 Как потратить баллы", callback_data="spend_points")],
        [InlineKeyboardButton("ℹ️ Обо мне", callback_data="about_me")],
        [InlineKeyboardButton("🔗 Реферальная ссылка", callback_data="referral")]
    ])
    
    await query.message.edit_text("Выберите опцию:", reply_markup=kb)

# Обработчик кнопок для курса
async def handle_course_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора курса (бесплатный, платный, челленджи)."""
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data

    if choice == "free_course":
        # Логика для бесплатного курса
        if ctx.user_data[user_id]["instructor"] == "evgeniy":
            await evgeniy_start_free_course(query.message, ctx, user_id)
        else:
            await anastasia_start_free_course(query.message, ctx, user_id)

    elif choice == "paid_course":
        # Логика для платного курса
        await query.message.reply_text("Вы выбрали платный курс. Ожидайте!")
    
    elif choice == "challenge_menu":
        # Логика для челленджей
        await query.message.reply_text("Вы выбрали челленджи. Ожидайте!")

    elif choice == "nutrition_menu":
        # Логика для меню питания
        await handle_nutrition_menu(update, ctx)
    
    elif choice == "referral":
        # Логика для реферальной ссылки
        await handle_referral(update, ctx)

# Обработчик меню питания
async def handle_nutrition_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Меню питания."""
    query = update.callback_query
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍴 Купить меню питания за 300 баллов", callback_data="buy_nutrition_menu")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки:", reply_markup=kb)

# Обработчик реферальной ссылки
async def handle_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Реферальная ссылка."""
    query = update.callback_query
    user_id = query.from_user.id
    me = await ctx.bot.get_me()
    link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(f"🔗 Ваша реферальная ссылка:\n{link}\n\nПоделитесь ею с друзьями, и вы получите 100 баллов! 🎉")

# Главный процесс бота
def main():
    """Запуск бота и подключение обработчиков."""
    app = Application.builder().token(TOKEN).build()

    # Обработчики команд и запросов
    app.add_handler(CommandHandler("start", start))  # Команда /start
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))  # Выбор тренера
    app.add_handler(CallbackQueryHandler(handle_course_selection, pattern="^(free_course|paid_course|challenge_menu|nutrition_menu|referral)$"))  # Выбор курса
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^buy_nutrition_menu$"))  # Покупка меню питания

    # Запуск бота на поллинге
    app.run_polling()

if __name__ == "__main__":
    main()
