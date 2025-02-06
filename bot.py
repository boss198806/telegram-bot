import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "YOUR_BOT_TOKEN"
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
    ])

# Бесплатный курс
async def handle_free_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
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
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true"
    }
    
    course_program = {
        1: [
            "1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
            "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
            "3️⃣ Велосипед 3x15 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"
        ],
        2: [
            "1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/c/2241417709/167/168)",
            "2️⃣ Лодочка прямые руки 3x30 [Видео](https://t.me/c/2241417709/395/396)",
            "3️⃣ Полные подъёмы корпуса 3x20 [Видео](https://t.me/c/2241417709/274/275)"
        ],
        3: [
            "1️⃣ Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Махи в бок с колен 3x20 (можно без резинки) [Видео](https://t.me/c/2241417709/385/386)",
            "3️⃣ Косые с касанием пяток 3x15 на каждую [Видео](https://t.me/c/2241417709/282/283)"
        ],
        4: [
            "1️⃣ Поочередные подъемы с гантелями в развороте 4x20 [Видео](https://t.me/c/2241417709/226/227)",
            "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
            "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)"
        ],
        5: [
            "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Махи под 45 с резинкой (можно без нее) 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"
        ]
    }
    
    exercises = course_program.get(current_day, [])
    caption = f"🔥 **Бесплатный курс: День {current_day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_paths[current_day],
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отправить отчет", callback_data=f"send_report_day_{current_day}")]])
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отправить отчет", callback_data=f"send_report_day_{current_day}")]]))

# Отправка отчета
async def handle_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    current_day = int(query.data.split("_")[-1])
    
    if user_reports_sent.get(user_id, {}).get(current_day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day}.")
        return
    
    user_waiting_for_video[user_id] = current_day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")

# Обработка видео
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    if user_id in user_waiting_for_video:
        current_day = user_waiting_for_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {current_day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        user_reports_sent.setdefault(user_id, {})[current_day] = True
        user_scores[user_id] = user_scores.get(user_id, 0) + 60
        del user_waiting_for_video[user_id]
        
        if current_day < 5:
            context.user_data[user_id]["current_day"] += 1
            await update.message.reply_text(
                f"Отчет за день {current_day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.\nПереход к следующему дню.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Следующий день", callback_data="next_day")]])
            )
        else:
            user_status[user_id] = statuses[1]
            await update.message.reply_text(
                f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: {user_scores[user_id]}.",
                reply_markup=main_menu()
            )
    elif user_id in user_waiting_for_challenge_video:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от {user_name} (ID: {user_id}) за челлендж."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        user_scores[user_id] = user_scores.get(user_id, 0) + 60
        del user_waiting_for_challenge_video[user_id]
        await update.message.reply_text(f"Отчет за челлендж принят! 🎉\nВаши баллы: {user_scores[user_id]}.")
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")

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
            [InlineKeyboardButton("Назад", callback_data="back")]
        ]
        await query.message.reply_text(
            "Доступ к челленджам стоит 300 баллов. Хотите приобрести?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await query.message.reply_text(
            "Для доступа к челленджам нужно 300 баллов.\nУ вас: {user_scores.get(user_id, 0)} баллов.\nПродолжайте тренировки!"
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
async def send_challenge_task(message: Message, user_id: int):
    current_day = user_challenges[user_id]["current_day"]
    exercises = course_program_challenges.get(current_day, [])
    caption = f"💪 **Челлендж: День {current_day}** 💪\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    
    await message.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отправить отчет", callback_data=f"send_challenge_report_{current_day}")]])
    )

# Запуск бота
def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_free_course, pattern="^free_course|next_day$"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="challenge_menu"))
    application.add_handler(CallbackQueryHandler(buy_challenge, pattern="buy_challenge"))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
