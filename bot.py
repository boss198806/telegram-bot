import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (если он используется)
load_dotenv()

# Конфигурация
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")  # ID группы для администраторских уведомлений

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Константы
STATUSES = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Функция формирования главного меню
def get_main_menu():
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
    ])

# Утилита для отправки фото с подписью (с обработкой ошибок)
async def send_photo_with_caption(bot, chat_id, photo_url, caption, reply_markup=None):
    try:
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text="Ошибка: изображение не найдено. Продолжайте без фото.",
            reply_markup=reply_markup
        )

# Инициализация профиля пользователя в context.user_data
def init_user_profile(context: ContextTypes.DEFAULT_TYPE):
    profile = context.user_data.get("profile")
    if not profile:
        profile = {
            "scores": 0,
            "status": STATUSES[0],
            "free_course": {
                "current_day": 1,
                "reports_sent": {}
            },
            "paid_course": {
                "current_day": 1,
            },
            "challenges": {
                "current_day": 1,
            },
            "waiting_for_video": None,    # может быть числом (для бесплатного курса) или кортежем ("paid", day)
            "waiting_for_receipt": False,
            "instructor": None,
            "gender": None,
            "program": None,
            "paid_gender": None,
            "paid_program": None,
        }
        context.user_data["profile"] = profile
    return profile

def get_user_profile(context: ContextTypes.DEFAULT_TYPE):
    return init_user_profile(context)

# Формирование текста для кнопки «Отправить отчет» (учитывая пол и программу)
def get_report_button_text(profile: dict):
    gender = profile.get("gender", "male")
    prog = profile.get("program", "home")
    return (("👩" if gender=="female" else "👨") + ("🏠" if prog=="home" else "🏋️") + " Отправить отчет 📹")

# ===================== БЕСПЛАТНЫЙ КУРС =====================

async def start_free_course(message, context: ContextTypes.DEFAULT_TYPE):
    profile = get_user_profile(context)
    # Если не выбраны пол и программа, запросим сначала выбор
    if profile.get("gender") is None or profile.get("program") is None:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Мужчина", callback_data="gender_male"),
             InlineKeyboardButton("👩 Женщина", callback_data="gender_female")]
        ])
        await message.reply_text("Ваш пол:", reply_markup=kb)
        return

    day = profile["free_course"].get("current_day", 1)
    if day > 5:
        await message.reply_text("Вы завершили курс! 🎉", reply_markup=get_main_menu())
        return

    photos = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
    }
    course = {
        1: [
            "1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
            "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
            "3️⃣ Велосипед 3x15 [Видео](https://t.me/c/2241417709/278/279)"
        ],
        2: [
            "1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/c/2241417709/167/168)",
            "2️⃣ Лодочка прямые руки 3x30 [Видео](https://t.me/c/2241417709/395/396)",
            "3️⃣ Полные подъёмы корпуса 3x20 [Видео](https://t.me/c/2241417709/274/275)"
        ],
        3: [
            "1️⃣ Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Махи в бок с колен 3x20 [Видео](https://t.me/c/2241417709/385/386)",
            "3️⃣ Косые с касанием пяток 3x15 [Видео](https://t.me/c/2241417709/282/283)"
        ],
        4: [
            "1️⃣ Поочередные подъемы с гантелями 4x20 [Видео](https://t.me/c/2241417709/226/227)",
            "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
            "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)"
        ],
        5: [
            "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Махи под 45 с резинкой 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"
        ],
    }
    exercises = course.get(day, [])
    text = f"🔥 **Бесплатный курс: День {day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день! 🎥"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_report_button_text(profile), callback_data=f"send_report_day_{day}")]
    ])
    await send_photo_with_caption(context.bot, message.chat_id, photos.get(day), text, reply_markup=kb)

# Обработчик callback для бесплатного курса (а также для перехода к следующему дню)
async def handle_free_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    await query.answer()
    if query.data == "free_course" and (profile.get("gender") is None or profile.get("program") is None):
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Мужчина", callback_data="gender_male"),
             InlineKeyboardButton("👩 Женщина", callback_data="gender_female")]
        ])
        await query.message.reply_text("Ваш пол:", reply_markup=kb)
        return
    await start_free_course(query.message, context)

# Обработчики выбора пола и программы для бесплатного курса
async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    profile["gender"] = "male" if query.data == "gender_male" else "female"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    profile["program"] = "home" if query.data == "program_home" else "gym"
    profile["free_course"]["current_day"] = 1  # сброс дня курса
    await start_free_course(query.message, context)

# Обработка запроса на отправку видео-отчёта (бесплатный курс)
async def handle_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    try:
        day = int(query.data.split("_")[-1])
    except ValueError:
        await query.message.reply_text("Ошибка: неверный формат данных.")
        return
    if profile["free_course"]["reports_sent"].get(day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {day}.")
        return
    profile["waiting_for_video"] = day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день 🎥")

# ===================== ПЛАТНЫЙ КУРС =====================

async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    discount = min(profile["scores"] * 2, 600)
    price = 2000 - discount
    text = (
        f"📚 **Платный курс** 📚\n\n"
        f"Стоимость курса: 2000 руб. 💵\n"
        f"Ваша скидка: {discount} руб. 🔖\n"
        f"Итоговая сумма: {price} руб. 💳\n\n"
        "💳 Переведите сумму на карту: 89236950304 (Яндекс Банк) 🏦\n"
        "После оплаты отправьте чек для проверки."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧾 Отправить чек", callback_data="send_receipt")]
    ])
    await query.message.reply_text(text, reply_markup=kb)
    profile["waiting_for_receipt"] = True

async def handle_send_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    profile["waiting_for_receipt"] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате 📸.")

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = get_user_profile(context)
    user = update.message.from_user
    if not profile.get("waiting_for_receipt"):
        await update.message.reply_text("Я не жду чек от вас. Пожалуйста, выберите платный курс и отправьте чек. 🚧")
        return
    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фото чека 📸.")
        return
    photo_id = update.message.photo[-1].file_id
    await context.bot.send_message(chat_id=GROUP_ID, text=f"🧾 Чек от {user.first_name} (ID: {user.id}). Подтвердите оплату.")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_payment_{user.id}")]
    ])
    await context.bot.send_photo(chat_id=GROUP_ID, photo=photo_id, reply_markup=kb)
    await update.message.reply_text("Чек отправлен на проверку. Ожидайте подтверждения ⏳.")

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    try:
        user_id = int(query.data.split("_")[-1])
    except ValueError:
        await query.message.reply_text("Ошибка при подтверждении оплаты.")
        return
    profile["status"] = STATUSES[2]  # обновляем статус
    profile["waiting_for_receipt"] = False
    await context.bot.send_message(chat_id=user_id, text="✅ Оплата подтверждена! Вам открыт доступ к платному курсу. 🎉")
    if profile.get("instructor") == "evgeniy":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Мужчина", callback_data="paid_gender_male"),
             InlineKeyboardButton("👩 Женщина", callback_data="paid_gender_female")]
        ])
        await context.bot.send_message(chat_id=user_id, text="Пожалуйста, выберите ваш пол для платного курса:", reply_markup=kb)
    else:
        profile["paid_course"]["current_day"] = 1
        await start_paid_course_day(user_id, context)

async def handle_paid_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    if query.data == "paid_gender_male":
        profile["paid_gender"] = "male"
        await query.message.reply_text("В разработке 🚧")
    elif query.data == "paid_gender_female":
        profile["paid_gender"] = "female"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏋️ В зале", callback_data="paid_program_gym"),
             InlineKeyboardButton("🏠 Дома", callback_data="paid_program_home")]
        ])
        await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_paid_program_gym(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    profile["paid_program"] = "gym"
    profile["paid_course"]["current_day"] = 1
    await start_paid_course_day(query.from_user.id, context)

async def handle_paid_program_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке 🚧")

# Запуск платного курса (переход по дням)
async def start_paid_course_day(user_id, context: ContextTypes.DEFAULT_TYPE):
    profile = get_user_profile(context)
    day = profile["paid_course"].get("current_day", 1)
    paid_exercises = {
        1: [
            "Махи назад с утяжелителями 3х25+5 https://t.me/c/2241417709/337/338",
            "Выпады 3х30 шагов х 2кг https://t.me/c/2241417709/157/158",
            "Разведение ног 3х20 https://t.me/c/2241417709/128/129",
            "Сведение ног 3х20 https://t.me/c/2241417709/126/127",
            "Сгибание ног 3х15 https://t.me/c/2241417709/130/131",
        ],
        2: [
            "Косые скручивания 3х30+10 https://t.me/c/2241417709/284/285",
            "Отжимания от пола 3х15+5 https://t.me/c/2241417709/167/168",
            "Лодочка с локтями 3х20+5 https://t.me/c/2241417709/183/184",
            "Жим гантелей 3х15+5 (вес подбираешь) https://t.me/c/2241417709/175/176",
            "Гантели в развороте 3х15+5 https://t.me/c/2241417709/222/223",
            "Разгибание с веревкой 3х1+5 https://t.me/c/2241417709/260/261",
        ],
        3: [
            "Подъёмы ног 3х15+5 https://t.me/c/2241417709/270/271",
            "Разгибание ног 3х15+5 https://t.me/c/2241417709/134/135",
            "Выпады назад 3х15 https://t.me/c/2241417709/155/156",
            "Ягодичный мост 3х20+5 https://t.me/c/2241417709/381/382",
            "Двойные разведения ног 3х20+5 https://t.me/c/2241417709/123/125",
            "Мертвая тяга с гантелями 3х15+5 https://t.me/c/2241417709/136/137",
        ],
        4: [
            "Скручивания 3х20+10 https://t.me/c/2241417709/379/380",
            "Отжимания в ТРХ ремнях 3х15+5 https://t.me/c/2241417709/159/160",
            "Подтягивания в ТРХ ремнях 3х15 https://t.me/c/2241417709/188/189",
            "Разводка с гантелями 35 3х15+5 https://t.me/c/2241417709/169/170",
            "Тяга блока к груди широким хватом 3х12 https://t.me/c/2241417709/210/211",
            "Жим гантелей сидя 3х12 https://t.me/c/2241417709/115/117",
            "Скручивания на скамье 3х20 https://t.me/c/2241417709/272/273",
        ],
        5: [
            "Вместо дня 5 оставим пример или финальную программу 🏆",
        ],
    }
    exercises = paid_exercises.get(day, [])
    text = f"📚 **Платный курс: День {day}** 📚\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день! 🎥"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"paid_video_day_{day}")]
    ])
    await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown", reply_markup=kb)

async def handle_send_paid_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    try:
        paid_day = int(query.data.split("_")[-1])
    except ValueError:
        await query.message.reply_text("Ошибка: неверный формат данных.")
        return
    profile["waiting_for_video"] = ("paid", paid_day)
    await query.message.reply_text(f"Пожалуйста, отправьте видео-отчет за платный день {paid_day} 🎥")

async def handle_paid_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    current_day = profile["paid_course"].get("current_day", 1)
    if current_day < 5:
        profile["paid_course"]["current_day"] = current_day + 1
        await start_paid_course_day(query.from_user.id, context)
    else:
        await query.message.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=get_main_menu())
        profile["paid_course"]["current_day"] = 1  # сброс

# ===================== ЧЕЛЛЕНДЖИ =====================

async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    if profile["challenges"].get("current_day"):
        await send_challenge_task(query.message, context)
    elif profile["scores"] >= 300:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Купить доступ за 300 баллов", callback_data="buy_challenge"),
             InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ])
        await query.message.reply_text("Доступ к челленджам стоит 300 баллов. Хотите приобрести?", reply_markup=kb)
    else:
        await query.message.reply_text(f"⚠️ Для доступа к челленджам нужно 300 баллов.\nУ вас: {profile['scores']} баллов.\nПродолжайте тренировки!")

async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    if profile["scores"] >= 300:
        profile["scores"] -= 300
        profile["challenges"]["current_day"] = 1
        await query.message.reply_text("✅ Доступ к челленджам открыт!", reply_markup=get_main_menu())
        await send_challenge_task(query.message, context)
    else:
        await query.message.reply_text("⚠️ Недостаточно баллов для покупки доступа!")

async def send_challenge_task(message, context: ContextTypes.DEFAULT_TYPE):
    profile = get_user_profile(context)
    day = profile["challenges"].get("current_day", 1)
    challenge_exercises = {
        1: [
            "1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
            "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"
        ],
        2: [
            "1️⃣ Присед со штангой 30 раз [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Отжимания с отрывом рук 25 раз [Видео](https://t.me/c/2241417709/393/394)",
            "3️⃣ Полные подъёмы корпуса 30 раз [Видео](https://t.me/c/2241417709/274/275)"
        ],
        3: [
            "1️⃣ Планка 3 мин [Видео](https://t.me/c/2241417709/286/296)",
            "2️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"
        ],
        4: [
            "1️⃣ Выпады назад 60 раз [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
            "3️⃣ Велосипед 50 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"
        ],
        5: [
            "1️⃣ Присед со штангой 50 раз [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
            "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)"
        ],
    }
    exercises = challenge_exercises.get(day, [])
    text = f"💪 **Челлендж: День {day}** 💪\n\n" + "\n".join(exercises)
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("➡️ Следующий день", callback_data="challenge_next")]] 
        if day < 5 else [[InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="back")]]
    )
    await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_challenge_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    if not profile["challenges"].get("current_day"):
        await query.answer("Сначала купите челлендж! 🚧")
        return
    day = profile["challenges"]["current_day"]
    if day < 5:
        profile["challenges"]["current_day"] = day + 1
        await send_challenge_task(query.message, context)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж! 🎉", reply_markup=get_main_menu())
        profile["challenges"]["current_day"] = 0

# ===================== ОБЩИЙ ФУНКЦИОНАЛ =====================

async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍴 Купить меню питания за 300 баллов", callback_data="buy_nutrition_menu"),
         InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки:", reply_markup=kb)

async def handle_buy_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    if profile["scores"] >= 300:
        profile["scores"] -= 300
        await query.message.reply_text("✅ Покупка меню питания успешно завершена!\nВот ваше меню питания: https://t.me/MENUKURO4KIN/2", reply_markup=get_main_menu())
    else:
        await query.message.reply_text("⚠️ Недостаточно баллов для покупки меню питания!")

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    me = await context.bot.get_me()
    link = f"https://t.me/{me.username}?start={query.from_user.id}"
    await query.message.reply_text(f"🔗 Ваша реферальная ссылка:\n{link}\n\nПоделитесь ею с друзьями, и вы получите 100 баллов! 🎉")

async def handle_my_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    text = (
        f"👤 Ваш кабинет:\n\n"
        f"Статус: {profile['status']}\n"
        f"Баллы: {profile['scores']}\n"
        "Продолжайте тренироваться, чтобы улучшить статус и заработать больше баллов! 💪"
    )
    await send_photo_with_caption(context.bot, update.effective_chat.id,
                                  "https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
                                  text)

async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "👤 О тренере:\n\n"
        "Курочкин Евгений Витальевич\n"
        "Общий тренировочный стаж - 20 лет\n"
        "Стаж работы - 15 лет\n"
        "МС - по становой тяге\n"
        "МС - по жиму штанги лежа\n"
        "Судья - федеральной категории\n"
        "Организатор соревнований\n"
        "КМС - по бодибилдингу\n\n"
        "20 лет в фитнесе! 💥"
    )
    await send_photo_with_caption(context.bot, update.effective_chat.id,
                                  "https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
                                  text)

async def handle_earn_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "💡 Как заработать баллы:\n\n"
        "1️⃣ Проходите бесплатный курс и отправляйте видео-отчеты.\n"
        "2️⃣ Участвуйте в челленджах и отправляйте видео-отчеты.\n"
        "3️⃣ Приглашайте друзей и получайте баллы за их активность.\n"
        "4️⃣ Покупайте платный курс и получаете дополнительные баллы."
    )
    await send_photo_with_caption(context.bot, update.effective_chat.id,
                                  "https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
                                  text)

async def handle_spend_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    text = (
        f"💰 Как потратить баллы:\n\n"
        f"У вас есть {profile['scores']} баллов.\n"
        "Вы можете потратить баллы на:\n"
        "- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
        "- Максимальная скидка - 600 рублей.\n"
        "- Другие привилегии!"
    )
    await send_photo_with_caption(context.bot, update.effective_chat.id,
                                  "https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
                                  text)

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("🏠 Главное меню", reply_markup=get_main_menu())

# ===================== /START И ВЫБОР ИНСТРУКТОРА =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = get_user_profile(context)
    user_id = update.effective_user.id
    # Реферальная логика (пример; для полноценного решения потребуется хранить данные всех пользователей)
    if context.args:
        try:
            ref = int(context.args[0])
            if ref != user_id:
                try:
                    await context.bot.send_message(chat_id=ref, text="🎉 Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!")
                except Exception as e:
                    logger.error(f"Реферальный бонус: {e}")
        except ValueError:
            pass
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_1"),
            InlineKeyboardButton("💫 АНАСТАСИЯ", callback_data="instructor_2")
        ],
        [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
        [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
        [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")],
    ])
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выбери для себя фитнес инструктора:", reply_markup=kb)

async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = get_user_profile(context)
    data = query.data
    await query.answer()
    if data == "instructor_1":
        profile["instructor"] = "evgeniy"
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://t.me/PRIVETSTVIEC/2",
            supports_streaming=True,
            caption="🎥 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=get_main_menu()
        )
    elif data == "instructor_2":
        profile["instructor"] = "anastasiya"
        await query.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ 💫")
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="📸 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=get_main_menu()
        )
    else:
        sel = {
            "instructor_3": "Тренер 3 🏋️",
            "instructor_4": "Тренер 4 🤼",
            "instructor_5": "Тренер 5 🤸"
        }.get(data, "неизвестный тренер")
        await query.message.edit_text(f"Вы выбрали тренера: {sel}. Функционал пока не реализован 🚧\nВы будете перенаправлены в главное меню.", reply_markup=get_main_menu())

# ===================== РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ =====================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    app.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern="^(free_course|next_day)$"))
    app.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    app.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
    app.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    app.add_handler(CallbackQueryHandler(buy_challenge, pattern="^buy_challenge$"))
    app.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    app.add_handler(CallbackQueryHandler(handle_send_receipt, pattern="^send_receipt$"))
    app.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment_"))
    app.add_handler(CallbackQueryHandler(handle_send_paid_report, pattern=r"^paid_video_day_(\d+)$"))
    app.add_handler(CallbackQueryHandler(handle_paid_next_day, pattern="^paid_next_day$"))
    app.add_handler(CallbackQueryHandler(handle_paid_gender, pattern="^paid_gender_"))
    app.add_handler(CallbackQueryHandler(handle_paid_program_gym, pattern="^paid_program_gym$"))
    app.add_handler(CallbackQueryHandler(handle_paid_program_home, pattern="^paid_program_home$"))
    app.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="^my_cabinet$"))
    app.add_handler(CallbackQueryHandler(handle_about_me, pattern="^about_me$"))
    app.add_handler(CallbackQueryHandler(handle_earn_points, pattern="^earn_points$"))
    app.add_handler(CallbackQueryHandler(handle_spend_points, pattern="^spend_points$"))
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern="^buy_nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(handle_challenge_next_day, pattern="^challenge_next$"))
    app.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    
    logger.info("Бот запущен и готов к работе. 🚀")
    app.run_polling()

# Обработка видео (общая для бесплатного и платного курсов)
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = get_user_profile(context)
    user = update.message.from_user
    waiting = profile.get("waiting_for_video")
    if waiting:
        if isinstance(waiting, tuple) and waiting[0] == "paid":
            paid_day = waiting[1]
            await context.bot.send_message(chat_id=GROUP_ID, text=f"Платный видео-отчет от {user.first_name} (ID: {user.id}) за день {paid_day}.")
            await context.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
            profile["scores"] += 30
            profile["waiting_for_video"] = None
            if paid_day < 5:
                await update.message.reply_text(
                    f"Отчет за платный день {paid_day} принят! 🎉\nВаши баллы: {profile['scores']}.\nГотовы к следующему дню ({paid_day+1})? ➡️",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {paid_day+1}", callback_data="paid_next_day")]])
                )
            else:
                await update.message.reply_text(f"Поздравляем! Вы завершили платный курс! 🎉\nВаши баллы: {profile['scores']}.", reply_markup=get_main_menu())
                profile["paid_course"]["current_day"] = 1
        elif isinstance(waiting, int):
            day = waiting
            await context.bot.send_message(chat_id=GROUP_ID, text=f"Видео-отчет от {user.first_name} (ID: {user.id}) за день {day}.")
            profile["free_course"]["reports_sent"][day] = True
            profile["scores"] += 60
            profile["waiting_for_video"] = None
            if day < 5:
                profile["free_course"]["current_day"] = day + 1
                new_day = profile["free_course"]["current_day"]
                profile["waiting_for_video"] = new_day
                await update.message.reply_text(
                    f"Отчет за день {day} принят! 🎉\nВаши баллы: {profile['scores']}.\nГотовы к следующему дню ({new_day})? ➡️",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {new_day}", callback_data="free_course")]])
                )
            else:
                profile["status"] = STATUSES[1]
                await update.message.reply_text(f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: {profile['scores']}.", reply_markup=get_main_menu())
        else:
            await update.message.reply_text("Ошибка: неизвестный формат данных.")
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")

if __name__ == "__main__":
    main()
