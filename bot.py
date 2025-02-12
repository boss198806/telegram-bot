import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
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
    kb = main_menu()  # Отображение главного меню
    await update.message.reply_text("Привет! Я твой фитнес-ассистент! Выберите тренера:", reply_markup=kb)

# Обработчик выбора тренера
async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора тренера пользователем (Евгений или Анастасия)."""
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "instructor_1":
        ctx.user_data[user_id]["instructor"] = "evgeniy"
        await evgeniy_start_free_course(query.message, ctx, user_id)  # Запуск курса для Евгения
    elif query.data == "instructor_2":
        ctx.user_data[user_id]["instructor"] = "anastasia"
        await anastasia_start_free_course(query.message, ctx, user_id)  # Запуск курса для Анастасии
    else:
        await query.message.edit_text("Вы выбрали неизвестного тренера. Пожалуйста, выберите снова.")

# Обработчик отправки отчета (в зависимости от тренера)
async def handle_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка отправки отчета пользователем за день в зависимости от тренера."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = ctx.user_data.get(user_id, {}).get("instructor")
    
    if instructor == "evgeniy":
        await evgeniy_handle_send_report(update, ctx)
    elif instructor == "anastasia":
        await anastasia_handle_send_report(update, ctx)
    else:
        await query.message.reply_text("Ошибка: не выбран тренер. Пожалуйста, выберите тренера в главном меню.")

# Функции для обработки дополнительных кнопок (Меню питания, Челленджи, и т.п.)
async def handle_nutrition_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Меню питания."""
    query = update.callback_query
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍴 Купить меню питания за 300 баллов", callback_data="buy_nutrition_menu")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки:", reply_markup=kb)

async def handle_challenges(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Челленджи."""
    query = update.callback_query
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Купить доступ за 300 баллов", callback_data="buy_challenge")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Доступ к челленджам стоит 300 баллов. Хотите приобрести?", reply_markup=kb)

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
    app.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_\d+"))  # Отправка отчета
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))  # Меню питания
    app.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))  # Челленджи
    app.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))  # Реферальная ссылка
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^buy_nutrition_menu$"))  # Покупка меню питания

    # Запуск бота на поллинге
    app.run_polling()

if __name__ == "__main__":
    main()
