from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from common import main_menu, get_report_button_text

# Функция для начала бесплатного курса для Евгения
async def start_free_course(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Запуск бесплатного курса для тренера Евгения."""
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
