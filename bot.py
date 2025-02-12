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
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from common import main_menu, get_report_button_text

# Функция для начала бесплатного курса для Анастасии
async def start_free_course(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Запуск бесплатного курса для тренера Анастасии."""
    if not (ctx.user_data[user_id].get("gender") == "female" and ctx.user_data[user_id].get("program") == "home"):
        return await msg.reply_text("Пока в разработке 🚧", reply_markup=main_menu())
    
    day = ctx.user_data[user_id].get("current_day", 1)
    if day > 5:
        return await msg.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
    
    photos = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
    }

    course = {
        1: ["1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)"],
        2: ["1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/c/2241417709/167/168)"],
        3: ["1️⃣ Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)"],
        4: ["1️⃣ Поочередные подъемы с гантелями 4x20 [Видео](https://t.me/c/2241417709/226/227)"],
        5: ["1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)"],
    }

    exercises = course.get(day, [])
    text = f"🔥 **Бесплатный курс: День {day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день! 🎥"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(get_report_button_text(ctx, user_id), callback_data=f"send_report_day_{day}")]])

    try:
        await ctx.bot.send_photo(chat_id=msg.chat_id, photo=photos.get(day), caption=text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await msg.reply_text("Ошибка: изображение не найдено. Продолжайте без фото.", reply_markup=kb)

# Функция для обработки отправки отчета
async def handle_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка отправки отчета пользователем за день в бесплатном курсе."""
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])
    if user_reports_sent.get(user_id, {}).get(day):
        return await query.message.reply_text(f"Вы уже отправили отчет за день {day}.")
    
    user_waiting_for_video[user_id] = day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день 🎥")
