import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Словарь для хранения текущего дня челленджа
user_challenges = {}

# Программа челленджей
challenge_program = {
    1: [
        "1️⃣ Выпады назад 40 раз",
        "2️⃣ Лодочка + сгибание в локтях 50 раз",
        "3️⃣ Велосипед 30 на каждую ногу",
    ],
    2: [
        "1️⃣ Присед со штангой (можно без) 30 раз",
        "2️⃣ Отжимания с отрывом рук 25 раз",
        "3️⃣ Полные подъёмы корпуса 30 раз",
    ],
    3: [
        "1️⃣ Планка 3 мин",
        "2️⃣ Подъёмы ног лёжа 3x15",
    ],
    4: [
        "1️⃣ Выпады назад 60 раз",
        "2️⃣ Лодочка + сгибание в локтях 50 раз",
        "3️⃣ Велосипед 50 на каждую ногу",
    ],
    5: [
        "1️⃣ Присед со штангой (можно без) 50 раз",
        "2️⃣ Отжимания с отрывом рук 40 раз",
        "3️⃣ Полные подъёмы корпуса 50 раз",
    ],
}

# Обработка кнопки "Челленджи"
async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_challenges:
        user_challenges[user_id] = {"current_day": 1}
    else:
        user_challenges[user_id]["current_day"] += 1

    current_day = user_challenges[user_id]["current_day"]

    if current_day > 5:
        await query.message.reply_text("Вы завершили челлендж! 🎉", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="main_menu")]]
        ))
        return

    exercises = challenge_program.get(current_day, [])
    caption = f"💪 **Челлендж: День {current_day}** 💪\n\n" + "\n".join(exercises)

    await query.message.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(f"➡️ Следующий день", callback_data="challenge_menu")],
                [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="main_menu")]
            ]
        ),
    )

# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", handle_challenges))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="challenge_menu"))

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
