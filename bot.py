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

# Токен бота
TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"  # Ваш токен

# Главное меню
def main_menu():
    """Возвращает главное меню бота."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍏 PRO DETOX", callback_data="pro_detox")]
    ])

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    user_id = update.effective_user.id
    context.user_data.setdefault(user_id, {})

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я твой помощник. Выбери действие ниже:",
        reply_markup=main_menu()
    )

# Обработчик для кнопки PRO DETOX
async def handle_pro_detox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор кнопки PRO DETOX и отправляет описание проекта."""
    query = update.callback_query
    description = (
        "Лето стройности ждет тебя! 🔥\n\n"
        "Мы запускаем летнее похудение — *PRO Detox* курс с Greenway Global! 🍏\n\n"
        "Три недели на пути к стройности и идеальному телу!\n\n"
        "**Что тебя ждет на курсе?**\n\n"
        "✅ Основы детокса от нутрициолога и программа питания на 21 день\n"
        "✅ Урок от эндокринолога — все о витаминах и БАД\n"
        "✅ Крутые мастер-классы с шеф-поваром — готовим вкусно и полезно\n"
        "✅ Прогулки + подкасты от психолога «Green Walk» — заряд для души и тела\n"
        "✅ Ежедневные тренировки и силовые комплексы, направленные на похудение — зарядки, йога, танцы и не только\n"
        "✅ Медитации и ароматерапия в бане, а также курс самомассажа и тейпирования\n\n"
        "Только для участников марафона доступна уникальная возможность в числе первых познакомиться с изумительной новинкой для очищения организма и тонуса — *Balancer Детокс-смузи* 💚\n\n"
        "❗️В ближайшее время отдельный запуск данного продукта не планируется!\n\n"
        "**КУРС НАПОЛНЕН ЭКСКЛЮЗИВАМИ:**\n\n"
        "💃 Участники смогут выиграть персональный онлайн-урок с хореографом.\n"
        "🧠 Узнают секреты сна, движения и питания от Члена Президентского совета Альберта Валиева.\n\n"
        "**Совершенствуй себя и помимо подтянутого тела забирай один из призов от Компании:**\n\n"
        "💆‍♀️ 5 массажеров для тела\n"
        "🧘‍♀️ 10 фитнес наборов для тренировки\n"
        "🥝 20 портативных блендеров\n\n"
        "**ГЛАВНЫЙ ПРИЗ — ФЕН DYSON 👩‍🦱**\n\n"
        "**Как участвовать?**\n\n"
        "1️⃣ С 12 по 19 мая (23:59 Мск) купи набор участника курса.\n"
        "2️⃣ Зарегистрируйся через мою ссылку (кнопка ниже)\n"
        "3️⃣ С 19 мая по 8 июня смотри все уроки и выполняй задания от экспертов.\n\n"
        "🎁 11 июня смотри розыгрыш призов курса в нашем Telegram-канале Greenway Global!\n\n"
        "Успей забрать свой кейс со скидкой -15%!\n\n"
        "*PRO Detox* — твой путь к здоровому и стройному телу 🧘‍♀️"
    )

    # Кнопка "Напиши мне"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Напиши мне", url="https://t.me/kuro4kin_sansay")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ])

    await query.message.edit_text(
        text=description,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await query.answer()

# Обработчик для возврата в главное меню
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает пользователя в главное меню."""
    query = update.callback_query
    await query.message.edit_text(
        "Привет! Я твой помощник. Выбери действие ниже:",
        reply_markup=main_menu()
    )
    await query.answer()

# Регистрация обработчиков
def main():
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_pro_detox, pattern="^pro_detox$"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))

    print("Бот запущен.")
    application.run_polling()

if __name__ == "__main__":
    main()
