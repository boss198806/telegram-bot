import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")

# ---------------------------
# Глобальные словари и константы
# ---------------------------
user_scores = {}                # общий счёт пользователя
user_status = {}                # статус пользователя
user_reports_sent = {}          # для бесплатного курса: {user_id: {day: bool}}
user_waiting_for_video = {}     # для бесплатного курса: {user_id: текущий день}

# Для платного курса – прогресс и ожидание видео (отдельно для каждого тренера)
user_paid_course_progress = {}   # {user_id: {trainer: day}} (0, если курс не куплен)
user_waiting_for_paid_video = {}   # {user_id: текущий день платного курса}

# Для покупки платного курса (ожидание чека)
user_waiting_for_receipt = {}    # {user_id: trainer}

# Для челленджей – прогресс (5 дней)
user_challenge_progress = {}    # {user_id: текущий день челленджа}

# Баллы для каждого тренера (отдельно)
trainer_scores = {
    "evgeniy": {},
    "anastasia": {},
    "trainer3": {},
    "trainer4": {},
    "trainer5": {},
}

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Программы для бесплатного курса (5 дней)
free_course_program = {
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
        "2️⃣ Махи под 45 с резинкой 3x20 [Видео](https://t.me/c/2241417709/339/340)",
        "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
    ],
}

# Программа для платного курса (5 дней) – после подтверждения выдаётся 1-дневная программа
paid_course_program = {
    1: [
        "1️⃣ Жим лежа 3x12 [Видео](https://t.me/c/2241417709/500/501)",
        "2️⃣ Тяга верхнего блока 3x15 [Видео](https://t.me/c/2241417709/502/503)",
        "3️⃣ Приседания 3x15 [Видео](https://t.me/c/2241417709/504/505)",
    ],
    2: [
        "1️⃣ Жим гантелей 3x12 [Видео](https://t.me/c/2241417709/506/507)",
        "2️⃣ Разводка рук 3x15 [Видео](https://t.me/c/2241417709/508/509)",
        "3️⃣ Подтягивания 3x10 [Видео](https://t.me/c/2241417709/510/511)",
    ],
    3: [
        "1️⃣ Становая тяга 3x10 [Видео](https://t.me/c/2241417709/512/513)",
        "2️⃣ Пресс 3x20 [Видео](https://t.me/c/2241417709/514/515)",
    ],
    4: [
        "1️⃣ Выпады 3x15 [Видео](https://t.me/c/2241417709/516/517)",
        "2️⃣ Пуловер 3x12 [Видео](https://t.me/c/2241417709/518/519)",
        "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/520/521)",
    ],
    5: [
        "1️⃣ Жим штанги 3x12 [Видео](https://t.me/c/2241417709/522/523)",
        "2️⃣ Тяга гантелей 3x15 [Видео](https://t.me/c/2241417709/524/525)",
        "3️⃣ Приседания с гантелями 3x15 [Видео](https://t.me/c/2241417709/526/527)",
    ],
}

# Программа для челленджей (5 дней, без видеоотчетов)
challenge_program = {
    1: [
        "1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
        "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
    ],
    2: [
        "1️⃣ Присед со штангой 30 раз [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Отжимания с отрывом рук 25 раз [Видео](https://t.me/c/2241417709/393/394)",
        "3️⃣ Полные подъёмы корпуса 30 раз [Видео](https://t.me/c/2241417709/274/275)",
    ],
    3: [
        "1️⃣ Планка 3 мин [Видео](https://t.me/c/2241417709/286/296)",
        "2️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
    ],
    4: [
        "1️⃣ Выпады назад 60 раз [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
        "3️⃣ Велосипед 50 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
    ],
    5: [
        "1️⃣ Присед со штангой 50 раз [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
        "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)",
    ],
}

# ---------------------------
# Константы для опроса КБЖУ
# ---------------------------
KBJU_SEX, KBJU_AGE, KBJU_HEIGHT, KBJU_ACTIVITY, KBJU_GOAL = range(5)

# ---------------------------
# Функции для опроса КБЖУ
# ---------------------------
async def kbju_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    trainer = context.user_data[user_id].get("instructor")
    current_trainer_points = trainer_scores.get(trainer, {}).get(user_id, 0)
    if current_trainer_points < 300:
        await query.message.reply_text("Недостаточно баллов для покупки КБЖУ (требуется 300).", reply_markup=main_menu())
        return ConversationHandler.END
    trainer_scores[trainer][user_id] = current_trainer_points - 300
    await query.message.reply_text("Для расчета КБЖУ ответьте на несколько вопросов.\n\nУкажите ваш пол:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Мужской", callback_data="kbju_sex_male"),
         InlineKeyboardButton("Женский", callback_data="kbju_sex_female")]
    ]))
    return KBJU_SEX

async def kbju_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["kbju"] = {}
    context.user_data["kbju"]["sex"] = "male" if query.data.endswith("male") else "female"
    await query.message.reply_text("Сколько вам лет?")
    return KBJU_AGE

async def kbju_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
        context.user_data["kbju"]["age"] = age
    except ValueError:
        await update.message.reply_text("Введите число (ваш возраст).")
        return KBJU_AGE
    await update.message.reply_text("Какой ваш рост (в см)?")
    return KBJU_HEIGHT

async def kbju_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = int(update.message.text)
        context.user_data["kbju"]["height"] = height
    except ValueError:
        await update.message.reply_text("Введите число (ваш рост в см).")
        return KBJU_HEIGHT
    await update.message.reply_text("Выберите уровень активности:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Низкая", callback_data="kbju_activity_low"),
         InlineKeyboardButton("Средняя", callback_data="kbju_activity_medium"),
         InlineKeyboardButton("Высокая", callback_data="kbju_activity_high")]
    ]))
    return KBJU_ACTIVITY

async def kbju_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    activity = query.data.split("_")[-1]
    context.user_data["kbju"]["activity"] = activity
    await query.message.reply_text("Какова ваша цель?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Снижение веса", callback_data="kbju_goal_loss"),
         InlineKeyboardButton("Набор массы", callback_data="kbju_goal_gain"),
         InlineKeyboardButton("Поддержание веса", callback_data="kbju_goal_maintain")]
    ]))
    return KBJU_GOAL

async def kbju_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    goal = query.data.split("_")[-1]
    context.user_data["kbju"]["goal"] = goal
    sex = context.user_data["kbju"]["sex"]
    age = context.user_data["kbju"]["age"]
    height = context.user_data["kbju"]["height"]
    weight = height - 100 if sex == "male" else height - 110
    bmr = 10 * weight + 6.25 * height - 5 * age + (5 if sex == "male" else -161)
    activity = context.user_data["kbju"]["activity"]
    factor = 1.2 if activity == "low" else 1.55 if activity == "medium" else 1.9
    calories = bmr * factor
    if goal == "loss":
        calories *= 0.8
    elif goal == "gain":
        calories *= 1.2
    result_text = (f"Ваши параметры:\nПол: {context.user_data['kbju']['sex']}\nВозраст: {age}\nРост: {height} см\n"
                   f"Активность: {activity.capitalize()}\nЦель: {goal}\n\n"
                   f"Рекомендуемое количество калорий: {int(calories)} ккал/день")
    await query.message.reply_text(result_text, reply_markup=main_menu())
    return ConversationHandler.END

async def kbju_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос КБЖУ отменен.", reply_markup=main_menu())
    return ConversationHandler.END

# ---------------------------
# Основное меню (с кнопками)
# ---------------------------
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
        [InlineKeyboardButton("🥗 КБЖУ", callback_data="kbju")]
    ])

# ---------------------------
# Функция отправки меню тренера
# ---------------------------
async def send_trainer_menu(context: ContextTypes.DEFAULT_TYPE, chat_id: int, trainer: str):
    caption = f"Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: {trainer.title()}"
    trainer_media = {
        "evgeniy": {"type": "video", "url": "https://github.com/boss198806/telegram-bot/raw/refs/heads/main/IMG_1484.MOV"},
        "anastasia": {"type": "photo", "url": "https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true"},
        "trainer3": {"type": "photo", "url": "https://via.placeholder.com/300.png?text=Trainer+3"},
        "trainer4": {"type": "photo", "url": "https://via.placeholder.com/300.png?text=Trainer+4"},
        "trainer5": {"type": "photo", "url": "https://via.placeholder.com/300.png?text=Trainer+5"},
    }
    media = trainer_media.get(trainer)
    if media:
        if media["type"] == "video":
            await context.bot.send_video(chat_id=chat_id, video=media["url"], supports_streaming=True, caption=caption, reply_markup=main_menu())
        else:
            await context.bot.send_photo(chat_id=chat_id, photo=media["url"], caption=caption, reply_markup=main_menu())
    else:
        await context.bot.send_message(chat_id=chat_id, text=caption, reply_markup=main_menu())

# ---------------------------
# Команда /start и выбор инструктора
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data.setdefault(user_id, {"current_day": 1})
    await update.message.reply_text(
        "Привет! Добро пожаловать в фитнес-бот. Выберите инструктора.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Евгений Курочкин", callback_data="instructor_evgeniy")],
            [InlineKeyboardButton("АНАСТАСИЯ", callback_data="instructor_anastasia")]
        ])
    )

async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    trainer = query.data.split("_", 1)[-1]
    user_id = query.from_user.id
    context.user_data.setdefault(user_id, {})["current_day"] = 1  # сброс бесплатного курса
    context.user_data[user_id]["instructor"] = trainer
    user_reports_sent[user_id] = {}  # очищаем историю отчетов
    await query.message.edit_text(f"Вы выбрали тренера: {trainer.title()}")
    await send_trainer_menu(context, query.message.chat_id, trainer)

# ---------------------------
# Функции выбора пола и программы
# ---------------------------
async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    context.user_data.setdefault(user_id, {})["gender"] = "male" if query.data == "gender_male" else "female"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=keyboard)

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    context.user_data.setdefault(user_id, {})["program"] = "home" if query.data == "program_home" else "gym"
    context.user_data[user_id]["current_day"] = 1
    await query.message.reply_text("Программа установлена. Бесплатный курс начинается с 1-го дня.", reply_markup=main_menu())

# ---------------------------
# Функционал бесплатного курса (5 дней, 60 баллов за день)
# ---------------------------
async def start_free_course(message_obj, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    if not (context.user_data[user_id].get("gender") == "female" and context.user_data[user_id].get("program") == "home"):
        await message_obj.reply_text("Пока в разработке", reply_markup=main_menu())
        return
    current_day = context.user_data[user_id].get("current_day", 1)
    if current_day > 5:
        await message_obj.reply_text("Вы завершили бесплатный курс! 🎉", reply_markup=main_menu())
        return
    program = free_course_program.get(current_day, [])
    caption = f"🔥 **Бесплатный курс: День {current_day}** 🔥\n\n" + "\n".join(program) + "\n\nОтправьте видео-отчет за день!"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Отправить отчет", callback_data=f"send_report_day_{current_day}")]
    ])
    try:
        await context.bot.send_photo(
            chat_id=message_obj.chat_id,
            photo=f"https://github.com/boss198806/telegram-bot/blob/main/IMG_96{46+current_day}.PNG?raw=true",
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке фото бесплатного курса: {e}")
        await message_obj.reply_text("Ошибка: изображение не найдено. Продолжайте без фото.", reply_markup=keyboard)

async def handle_free_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if "gender" not in context.user_data.get(user_id, {}) or "program" not in context.user_data.get(user_id, {}):
        gender_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Мужчина", callback_data="gender_male"),
             InlineKeyboardButton("Женщина", callback_data="gender_female")]
        ])
        await query.message.reply_text("Пожалуйста, выберите ваш пол:", reply_markup=gender_keyboard)
        return
    await start_free_course(query.message, context, user_id)

async def handle_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    try:
        current_day = int(query.data.split("_")[-1])
    except Exception:
        current_day = 1
    if user_reports_sent.get(user_id, {}).get(current_day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day}.")
        return
    user_waiting_for_video[user_id] = current_day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")

# ---------------------------
# Функционал платного курса: покупка (отдельно для каждого тренера)
# ---------------------------
async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    trainer = context.user_data[user_id].get("instructor")
    if not trainer:
        await query.message.reply_text("Сначала выберите тренера.", reply_markup=main_menu())
        return
    if user_id not in user_paid_course_progress:
        user_paid_course_progress[user_id] = {}
    user_paid_course_progress[user_id][trainer] = 0
    discount = min(user_scores.get(user_id, 0) * 2, 400)
    final_price = 2000 - discount
    text = (f"📚 **Платный курс** 📚\nСтоимость: 2000 руб.\nВаша скидка: {discount} руб.\nИтог: {final_price} руб.\n\n"
            "Переведите сумму на карту: 89236950304 (ЯНДЕКС БАНК).\nПосле оплаты нажмите кнопку и отправьте фото чека.")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить чек", callback_data=f"send_receipt_{trainer}")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
    user_waiting_for_receipt[user_id] = trainer
    await query.message.reply_text(text, reply_markup=keyboard)

async def handle_send_receipt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Пожалуйста, отправьте фото чека.")

async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_waiting_for_receipt:
        trainer = user_waiting_for_receipt[user_id]
        user_name = update.message.from_user.first_name
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Подтвердить", callback_data=f"confirm_payment_{user_id}_{trainer}")]
        ])
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Чек от {user_name} (ID: {user_id}) для платного курса тренера {trainer}. Подтвердите оплату."
        )
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[-1].file_id,
            reply_markup=keyboard
        )
        await update.message.reply_text("Чек отправлен на проверку. Ожидайте подтверждения.")
    else:
        await update.message.reply_text("Фото получено.")

async def handle_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    if len(data) >= 3:
        user_id = int(data[1])
        trainer = data[2]
        if user_id in user_waiting_for_receipt:
            del user_waiting_for_receipt[user_id]
        if user_id in user_paid_course_progress:
            user_paid_course_progress[user_id][trainer] = 1
        await query.message.reply_text("Оплата подтверждена!")
        program = paid_course_program.get(1, [])
        caption = "📚 **Платный курс (1 день):**\n\n" + "\n".join(program)
        await context.bot.send_message(chat_id=user_id, text=caption, reply_markup=main_menu())
    else:
        await query.message.reply_text("Ошибка подтверждения оплаты.")

async def handle_next_paid_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await handle_paid_course(update, context)

# ---------------------------
# Функционал челленджей (5 дней, без видео, 60 баллов за день)
# ---------------------------
async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in user_challenge_progress:
        user_challenge_progress[user_id] = 1
    current_day = user_challenge_progress[user_id]
    program = challenge_program.get(current_day, [])
    caption = (f"💪 **Челлендж: День {current_day}** 💪\n\n" +
               "\n".join(program) +
               "\n\nНажмите 'Завершить челлендж', чтобы получить 60 баллов!")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Завершить челлендж", callback_data="complete_challenge")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
    await query.message.reply_text(caption, parse_mode="Markdown", reply_markup=keyboard)

async def handle_complete_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_scores[user_id] = user_scores.get(user_id, 0) + 60
    trainer = context.user_data[user_id].get("instructor", "evgeniy")
    trainer_scores[trainer][user_id] = trainer_scores[trainer].get(user_id, 0) + 60
    current_day = user_challenge_progress.get(user_id, 1)
    response_text = f"Челлендж за день {current_day} выполнен! Вам начислено 60 баллов. Общий счет: {user_scores[user_id]}."
    if current_day < 5:
        user_challenge_progress[user_id] = current_day + 1
        response_text += f"\nПереходим к дню {current_day + 1}."
    else:
        response_text += "\nПоздравляем, вы завершили все челленджи!"
        del user_challenge_progress[user_id]
    await query.message.reply_text(response_text, reply_markup=main_menu())

# ---------------------------
# Функция обработки входящих видео (бесплатный и платный курсы)
# ---------------------------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    # Бесплатный курс
    if user_id in user_waiting_for_video:
        current_day = user_waiting_for_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Бесплатный курс. Видео-отчет от {user_name} (ID: {user_id}) за день {current_day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        user_reports_sent.setdefault(user_id, {})[current_day] = True
        user_scores[user_id] += 60
        trainer = context.user_data[user_id].get("instructor", "evgeniy")
        trainer_scores[trainer][user_id] = trainer_scores[trainer].get(user_id, 0) + 60
        del user_waiting_for_video[user_id]
        if current_day < 5:
            context.user_data[user_id]["current_day"] += 1
            new_day = context.user_data[user_id]["current_day"]
            user_waiting_for_video[user_id] = new_day
            await update.message.reply_text(
                f"Отчет за день {current_day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {new_day}", callback_data="next_day")]
                ])
            )
        else:
            user_status[user_id] = statuses[1]
            await update.message.reply_text(
                f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: {user_scores[user_id]}.",
                reply_markup=main_menu()
            )
        return

    # Платный курс
    if user_id in user_waiting_for_paid_video:
        current_day = user_waiting_for_paid_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Платный курс. Видео-отчет от {user_name} (ID: {user_id}) за день {current_day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        user_scores[user_id] += 30
        del user_waiting_for_paid_video[user_id]
        trainer = context.user_data[user_id].get("instructor", "evgeniy")
        if user_id in user_paid_course_progress and trainer in user_paid_course_progress[user_id]:
            user_paid_course_progress[user_id][trainer] = current_day + 1
        if current_day < 5:
            await update.message.reply_text(
                f"Отчет за день {current_day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {current_day + 1}", callback_data="next_paid_day")]
                ])
            )
        else:
            await update.message.reply_text(
                f"Поздравляем! Вы завершили платный курс! 🎉\nВаши баллы: {user_scores[user_id]}.",
                reply_markup=main_menu()
            )
        return

    await update.message.reply_text("Я не жду видео от вас.")

# ---------------------------
# Функционал рефералов, личного кабинета, информации и т.д.
# ---------------------------
async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await context.bot.get_me()
    referral_link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(f"Ваша реферальная ссылка:\n{referral_link}\n\nПоделитесь ею, чтобы получить бонус!", reply_markup=main_menu())

async def handle_my_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])
    caption = f"👤 Ваш кабинет:\n\nСтатус: {status}\nБаллы: {score}\nПродолжайте тренироваться!"
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                       photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
                                       caption=caption,
                                       parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Мой кабинет': {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    caption = ("👤 О тренере:\n\nКурочкин Евгений Витальевич\nТренировочный стаж: 20 лет\n"
               "Стаж работы: 15 лет\nМС по становой тяге и жиму\nСудья федеральной категории\n20 лет в фитнесе!")
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                       photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
                                       caption=caption,
                                       parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Обо мне': {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def handle_earn_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    caption = ("💡 Как заработать баллы:\n1. Бесплатный курс\n2. Челленджи\n3. Реферальная система\n4. Платный курс")
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                       photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
                                       caption=caption,
                                       parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Как заработать баллы': {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def handle_spend_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    caption = f"💰 Как потратить баллы:\nУ вас {score} баллов.\nМожно получить скидки на курсы и товары."
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                       photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
                                       caption=caption,
                                       parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Как потратить баллы': {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Купить меню питания", callback_data="buy_nutrition")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки.", reply_markup=keyboard)

async def handle_buy_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    trainer = context.user_data[user_id].get("instructor")
    current = trainer_scores.get(trainer, {}).get(user_id, 0)
    if current >= 300:
        trainer_scores[trainer][user_id] = current - 300
        await query.message.reply_text("Покупка меню питания успешно завершена!\nВот ваше меню: https://t.me/MENUKURO4KIN/2", reply_markup=main_menu())
    else:
        await query.message.reply_text("Недостаточно баллов для покупки меню питания!")

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню", reply_markup=main_menu())

# ---------------------------
# Основной обработчик и запуск бота
# ---------------------------
def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern="^(free_course|next_day)$"))
    application.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    application.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"^send_report_day_\d+"))
    application.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    application.add_handler(CallbackQueryHandler(handle_send_receipt_callback, pattern=r"^send_receipt_"))
    application.add_handler(CallbackQueryHandler(handle_confirm_payment, pattern=r"^confirm_payment_"))
    application.add_handler(CallbackQueryHandler(handle_next_paid_day, pattern="^next_paid_day$"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    application.add_handler(CallbackQueryHandler(handle_complete_challenge, pattern="^complete_challenge$"))
    application.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))
    application.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="^my_cabinet$"))
    application.add_handler(CallbackQueryHandler(handle_about_me, pattern="^about_me$"))
    application.add_handler(CallbackQueryHandler(handle_earn_points, pattern="^earn_points$"))
    application.add_handler(CallbackQueryHandler(handle_spend_points, pattern="^spend_points$"))
    application.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern="^buy_nutrition$"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))

    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(kbju_start, pattern="^kbju$")],
        states={
            KBJU_SEX: [CallbackQueryHandler(kbju_sex, pattern="^kbju_sex_")],
            KBJU_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kbju_age)],
            KBJU_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, kbju_height)],
            KBJU_ACTIVITY: [CallbackQueryHandler(kbju_activity, pattern="^kbju_activity_")],
            KBJU_GOAL: [CallbackQueryHandler(kbju_goal, pattern="^kbju_goal_")],
        },
        fallbacks=[CommandHandler("cancel", kbju_cancel)],
    )
    application.add_handler(conv_handler)

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
