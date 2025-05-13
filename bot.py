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

# Главное меню с видео
def main_menu():
    """Возвращает главное меню бота с кнопками PRO DETOX и ECO Market."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍏 PRO DETOX", callback_data="pro_detox"),
         InlineKeyboardButton("🛒 ECO Market", callback_data="eco_market")]
    ])

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start и отправляет видео с кнопками."""
    user_id = update.effective_user.id
    context.user_data.setdefault(user_id, {})

    try:
        # Отправляем видео из Telegram
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video="https://t.me/speekto/2",
            caption="",
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке видео: {e}")
        # Если видео не удалось отправить, отправляем сообщение с кнопками
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не удалось загрузить приветственное видео. Выберите действие ниже:",
            reply_markup=main_menu()
        )

# Обработчик для кнопки PRO DETOX
async def handle_pro_detox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор кнопки PRO DETOX и отправляет описание проекта."""
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки
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

    try:
        await query.message.edit_caption(
            caption=description,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        # Если редактирование не удалось, отправляем новое сообщение
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=description,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# Обработчик для кнопки ECO Market
async def handle_eco_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор кнопки ECO Market и отправляет видео, затем описание с кнопками."""
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    # Описание для ECO Market
    description = (
        "С 15 мая у нас стартует онлайн курс - *ЭКО МАРКЕТ*✅\n\n"
        "3 дня бесплатного обучения, по созданию такого чата, как у меня))) где тебя научат: создавать чат, рассказывать о продукте, делать обзоры🩷\n\n"
        "**Что ты получишь за 3 дня обучения? ⬇️**\n\n"
        "1️⃣ Начнешь зарабатывать на чате 5-30.000₽ в месяц, без рисков и вложений, уделяя 1 час в день\n"
        "2️⃣ У тебя будет наставник, я всегда помогу, расскажу и передам свой опыт\n"
        "3️⃣ Возможность бесплатно пользоваться продуктом\n"
        "4️⃣ Получишь подарки от компании в течении 6-ти месяцев на 10.000₽ даже швабру дарят\n\n"
        "✅ Можно совмещать с основной работой/учебой😻 Нужно только твое желание🩷\n\n"
        "А если хочешь масштаба 🚀 изменить свою жизнь, то я могу рассказать тебе, про другие виды заработка в компании и тогда мы будем работать по другому 🤩\n\n"
        "Напиши мне✍🏼 я отправлю тебе ссылку на бесплатный онлайн курс☺️🙌🏼 в тг канале)"
    )

    # Кнопки
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Написать мне", url="https://t.me/kuro4kin_sansay")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ])

    try:
        # Удаляем предыдущее сообщение
        await query.message.delete()
        # Отправляем видео без подписи
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://t.me/speekto/4",
            reply_markup=None  # Кнопки будут в следующем сообщении
        )
        # Отправляем описание как отдельное сообщение с кнопками
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=description,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке видео или сообщения для ECO Market: {e}")
        # Если что-то пошло не так, отправляем только текст с описанием и кнопками
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Не удалось загрузить видео для ECO Market.\n\n" + description,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )

# Обработчик для возврата в главное меню
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает пользователя в главное меню с видео."""
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки
    try:
        # Отправляем видео из Telegram
        await query.message.delete()  # Удаляем текущее сообщение
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://t.me/speekto/2",
            caption="",
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке видео: {e}")
        # Если видео не удалось отправить, отправляем сообщение с кнопками
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Не удалось загрузить приветственное видео. Выберите действие ниже:",
            reply_markup=main_menu()
        )

# Регистрация обработчиков
def main():
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_pro_detox, pattern="^pro_detox$"))
    application.add_handler(CallbackQueryHandler(handle_eco_market, pattern="^eco_market$"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))

    print("Бот запущен.")
    application.run_polling()

if __name__ == "__main__":
    main()
