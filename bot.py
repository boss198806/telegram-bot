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
user_scores = {}                # общий счет пользователя
user_status = {}                # статус пользователя
user_reports_sent = {}          # {user_id: {day: bool}} – отчеты по курсам
# Для ожидания видеоотчета: значение — кортеж (course_type, day)
user_waiting_for_video = {}

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

# Программа для платного курса (5 дней) – после подтверждения выдается 1-дневная программа
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
# Константы для опроса КБЖУ (ConversationHandler)
# ---------------------------
KBJU_SEX, KBJU_AGE, KBJU_HEIGHT, KBJU_ACTIVITY, KBJU_GOAL = range(5)

# ---------------------------
# Функция формирования меню выбора дня курса
# ---------------------------
def day_menu(course_type: str):
    buttons = []
    for i in range(1, 6):
        buttons.append(InlineKeyboardButton(f"День {i}", callback_data=f"{course_type}_day_{i}"))
    return InlineKeyboardMarkup([buttons])

# ---------------------------
# Функции для опроса КБЖУ
# ---------------------------
async def kbju_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    trainer = context.user_data[user_id].get("instructor")
    current_points = trainer_scores.get(trainer, {}).get(user_id, 0)
    if current_points < 300:
        await query.message.reply_text("Недостаточно баллов для покупки КБЖУ (требуется 300).", reply_markup=main_menu())
        return ConversationHandler.END
    trainer_scores[trainer][user_id] = current_points - 300
    await query.message.reply_text(
        "Для расчета КБЖУ ответьте на несколько вопросов.\n\nУкажите ваш пол:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Мужской", callback_data="kbju_sex_male"),
             InlineKeyboardButton("Женский", callback_data="kbju_sex_female")]
        ])
    )
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
    await update.message.reply_text(
        "Выберите уровень активности:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Низкая", callback_data="kbju_activity_low"),
             InlineKeyboardButton("Средняя", callback_data="kbju_activity_medium"),
             InlineKeyboardButton("Высокая", callback_data="kbju_activity_high")]
        ])
    )
    return KBJU_ACTIVITY

async def kbju_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    activity = query.data.split("_")[-1]
    context.user_data["kbju"]["activity"] = activity
    await query.message.reply_text(
        "Какова ваша цель?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Снижение веса", callback_data="kbju_goal_loss"),
             InlineKeyboardButton("Набор массы", callback_data="kbju_goal_gain"),
             InlineKeyboardButton("Поддержание веса", callback_data="kbju_goal_maintain")]
        ])
    )
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
    result_text = (
        f"Ваши параметры:\nПол: {context.user_data['kbju']['sex']}\nВозраст: {age}\nРост: {height} см\n"
        f"Активность: {activity.capitalize()}\nЦель: {goal}\n\n"
        f"Рекомендуемое количество калорий: {int(calories)} ккал/день"
    )
    await query.message.reply_text(result_text, reply_markup=main_menu())
    return ConversationHandler.END

async def kbju_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос КБЖУ отменен.", reply_markup=main_menu())
    return ConversationHandler.END

# ---------------------------
# Основное меню
# ---------------------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Пройти бесплатный курс", callback_data="free_course")],
        [InlineKeyboardButton("💪 Челленджи", callback_data="challenge_course")],
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
    context.user_data.setdefault(user_id, {})["current_day"] = 1  # сброс курса
    context.user_data[user_id]["instructor"] = trainer
    user_reports_sent[user_id] = {}  # очищаем историю отчетов
    await query.message.edit_text(f"Вы выбрали тренера: {trainer.title()}")
    await send_trainer_menu(context, query.message.chat_id, trainer)
    # После выбора тренера выводим меню выбора дня для бесплатного курса
    await query.message.reply_text("Выберите день бесплатного курса:", reply_markup=day_menu("free"))

# ---------------------------
# Функционал выбора пола и программы
# ---------------------------
async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    context.user_data.setdefault(user_id, {})["gender"] = "male" if query.data == "gender_male" else "female"
    await query.edit_message_text("Выберите программу:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ]))

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    context.user_data.setdefault(user_id, {})["program"] = "home" if query.data == "program_home" else "gym"
    context.user_data[user_id]["current_day"] = 1
    await query.edit_message_text("Программа установлена. Выберите день бесплатного курса:", reply_markup=day_menu("free"))

# ---------------------------
# Функционал бесплатного курса
# ---------------------------
async def handle_free_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        day = int(query.data.split("_")[-1])
    except Exception:
        day = 1
    program = free_course_program.get(day, [])
    text = f"🔥 **Бесплатный курс: День {day}** 🔥\n\n" + "\n".join(program)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data=f"send_free_report_{day}")]
    ])
    user_id = query.from_user.id
    user_waiting_for_video[user_id] = ("free", day)
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_free_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if "gender" not in context.user_data.get(user_id, {}) or "program" not in context.user_data.get(user_id, {}):
        gender_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Мужской", callback_data="gender_male"),
             InlineKeyboardButton("Женский", callback_data="gender_female")]
        ])
        await query.message.reply_text("Пожалуйста, выберите ваш пол:", reply_markup=gender_keyboard)
        return
    await query.message.reply_text("Выберите день бесплатного курса:", reply_markup=day_menu("free"))

async def handle_send_free_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Пожалуйста, отправьте видео-отчет за выбранный день.")

# ---------------------------
# Функционал платного курса
# ---------------------------
async def handle_paid_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        day = int(query.data.split("_")[-1])
    except Exception:
        day = 1
    program = paid_course_program.get(day, [])
    text = f"📚 **Платный курс: День {day}** 📚\n\n" + "\n".join(program)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data=f"send_paid_report_{day}")]
    ])
    user_id = query.from_user.id
    user_waiting_for_video[user_id] = ("paid", day)
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_send_paid_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Пожалуйста, отправьте видео-отчет за выбранный день.")

async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    trainer = context.user_data.get(user_id, {}).get("instructor")
    if not trainer:
        trainer = "evgeniy"
        context.user_data.setdefault(user_id, {})["instructor"] = trainer
    await query.message.reply_text("Выберите день платного курса:", reply_markup=day_menu("paid"))

# ---------------------------
# Функционал челленджей
# ---------------------------
async def handle_challenge_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        day = int(query.data.split("_")[-1])
    except Exception:
        day = 1
    program = challenge_program.get(day, [])
    text = f"💪 **Челлендж: День {day}** 💪\n\n" + "\n".join(program)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data=f"send_challenge_report_{day}")]
    ])
    user_id = query.from_user.id
    user_waiting_for_video[user_id] = ("challenge", day)
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_send_challenge_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Пожалуйста, отправьте видео-отчет за выбранный день.")

async def handle_complete_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_scores[user_id] = user_scores.get(user_id, 0) + 60
    trainer = context.user_data[user_id].get("instructor", "evgeniy")
    trainer_scores[trainer][user_id] = trainer_scores[trainer].get(user_id, 0) + 60
    await query.message.reply_text("Отчет челленджа принят! Вам начислено 60 баллов.", reply_markup=main_menu())

# ---------------------------
# Обработка видео-отчета
# ---------------------------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_waiting_for_video:
        course_type, day = user_waiting_for_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от пользователя {user_id} за {course_type} курс, День {day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        if course_type == "free":
            user_scores[user_id] = user_scores.get(user_id, 0) + 60
            reply_text = f"Отчет за День {day} принят! Вам начислено 60 баллов."
        elif course_type == "challenge":
            user_scores[user_id] = user_scores.get(user_id, 0) + 60
            reply_text = f"Отчет за День {day} принят! Вам начислено 60 баллов."
        elif course_type == "paid":
            user_scores[user_id] = user_scores.get(user_id, 0) + 30
            reply_text = f"Отчет за День {day} принят! Вам начислено 30 баллов."
        del user_waiting_for_video[user_id]
        await update.message.reply_text(reply_text, reply_markup=main_menu())
    else:
        pass

# ---------------------------
# Обработка чеков для платного курса (с подтверждением оплаты)
# ---------------------------
async def handle_send_receipt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Пожалуйста, отправьте фото чека.")

async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_waiting_for_video:
        # Если ожидается видео, пропускаем (это не чек)
        return
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
    try:
        prefix, uid_str, trainer = query.data.split("_", 2)
        user_id = int(uid_str)
    except Exception:
        await query.message.reply_text("Ошибка подтверждения оплаты.")
        return
    await query.message.reply_text("Оплата подтверждена!")
    program = paid_course_program.get(1, [])
    caption = (
        "📚 **Платный курс (1 день):**\n\n" +
        "\n".join(program) +
        "\n\nПосле выполнения видео-отчетов вам будут начисляться баллы."
    )
    await context.bot.send_message(chat_id=user_id, text=caption, reply_markup=main_menu())

async def handle_next_paid_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await handle_paid_course(update, context)

# ---------------------------
# Функционал рефералов, Личный кабинет, Меню питания и прочее
# ---------------------------
async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await context.bot.get_me()
    referral_link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(f"Ваша реферальная ссылка:\n{referral_link}", reply_markup=main_menu())

async def handle_my_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])
    caption = f"👤 Ваш кабинет:\nСтатус: {status}\nБаллы: {score}"
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Мой кабинет': {e}")
        await query.message.reply_text("Ошибка. Попробуйте позже.")

async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    caption = (
        "👤 О тренере:\nКурочкин Евгений Витальевич\nТренировочный стаж: 20 лет\n"
        "Стаж работы: 15 лет\nМС по становой тяге и жиму\nСудья федеральной категории"
    )
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Обо мне': {e}")
        await query.message.reply_text("Ошибка. Попробуйте позже.")

async def handle_earn_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    caption = (
        "💡 Как заработать баллы:\n1. Бесплатный курс\n2. Челленджи\n3. Реферальная система\n4. Платный курс"
    )
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Как заработать баллы': {e}")
        await query.message.reply_text("Ошибка. Попробуйте позже.")

async def handle_spend_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    caption = f"💰 Как потратить баллы:\nУ вас {score} баллов."
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке фото для 'Как потратить баллы': {e}")
        await query.message.reply_text("Ошибка. Попробуйте позже.")

async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Купить меню питания", callback_data="buy_nutrition")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания для покупки:", reply_markup=keyboard)

async def handle_buy_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    trainer = context.user_data[user_id].get("instructor")
    current = trainer_scores.get(trainer, {}).get(user_id, 0)
    if current >= 300:
        trainer_scores[trainer][user_id] = current - 300
        await query.message.reply_text("Меню питания куплено!\nВот ссылка: https://t.me/MENUKURO4KIN/2", reply_markup=main_menu())
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
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern=r"^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern=r"^(free_course|next_day)$"))
    application.add_handler(CallbackQueryHandler(handle_gender, pattern=r"^gender_"))
    application.add_handler(CallbackQueryHandler(handle_program, pattern=r"^program_"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"^send_report_day_\d+"))
    application.add_handler(CallbackQueryHandler(handle_paid_course, pattern=r"^paid_course$"))
    # Меню выбора дня для курсов:
    application.add_handler(CallbackQueryHandler(handle_free_day, pattern=r"^free_day_\d+"))
    application.add_handler(CallbackQueryHandler(handle_challenge_day, pattern=r"^challenge_day_\d+"))
    application.add_handler(CallbackQueryHandler(handle_paid_day, pattern=r"^paid_day_\d+"))
    # Кнопки "Отправить отчет":
    application.add_handler(CallbackQueryHandler(handle_send_free_report, pattern=r"^send_free_report_\d+"))
    application.add_handler(CallbackQueryHandler(handle_send_challenge_report, pattern=r"^send_challenge_report_\d+"))
    application.add_handler(CallbackQueryHandler(handle_send_paid_report, pattern=r"^send_paid_report_\d+"))
    application.add_handler(CallbackQueryHandler(handle_send_receipt_callback, pattern=r"^send_receipt_"))
    application.add_handler(CallbackQueryHandler(handle_confirm_payment, pattern=r"^confirm_payment_"))
    application.add_handler(CallbackQueryHandler(handle_next_paid_day, pattern=r"^next_paid_day$"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern=r"^challenge_course$"))
    application.add_handler(CallbackQueryHandler(handle_complete_challenge, pattern=r"^complete_challenge$"))
    application.add_handler(CallbackQueryHandler(handle_referral, pattern=r"^referral$"))
    application.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern=r"^my_cabinet$"))
    application.add_handler(CallbackQueryHandler(handle_about_me, pattern=r"^about_me$"))
    application.add_handler(CallbackQueryHandler(handle_earn_points, pattern=r"^earn_points$"))
    application.add_handler(CallbackQueryHandler(handle_spend_points, pattern=r"^spend_points$"))
    application.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern=r"^nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern=r"^buy_nutrition$"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern=r"^back$"))

    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(kbju_start, pattern=r"^kbju$")],
        states={
            KBJU_SEX: [CallbackQueryHandler(kbju_sex, pattern=r"^kbju_sex_")],
            KBJU_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kbju_age)],
            KBJU_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, kbju_height)],
            KBJU_ACTIVITY: [CallbackQueryHandler(kbju_activity, pattern=r"^kbju_activity_")],
            KBJU_GOAL: [CallbackQueryHandler(kbju_goal, pattern=r"^kbju_goal_")],
        },
        fallbacks=[CommandHandler("cancel", kbju_cancel)],
    )
    application.add_handler(conv_handler)

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
