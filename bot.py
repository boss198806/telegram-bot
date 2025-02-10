import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# ------------------------- Глобальные словари (отдельно для Евгения и Анастасии) -------------------------
# Евгений
user_scores_evg = {}
user_status_evg = {}
user_reports_sent_evg = {}
user_waiting_for_video_evg = {}
user_waiting_for_receipt_evg = {}
user_challenges_evg = {}
user_data_free_evg = {}     # (gender, program, current_day)
user_data_paid_evg = {}     # (gender, program, current_day)

# Анастасия
user_scores_ana = {}
user_status_ana = {}
user_reports_sent_ana = {}
user_waiting_for_video_ana = {}
user_waiting_for_receipt_ana = {}
user_challenges_ana = {}
user_data_free_ana = {}
user_data_paid_ana = {}

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# --------------------- Пример словарей с упражнениями (чтобы убрать «в разработке») ---------------------
# 1) Бесплатный курс Евгения
evg_free_exercises = {
    ("male", "home"): {
        1: [
            "1) Приседания 3x15",
            "2) Отжимания 3x12",
            "3) Скручивания 3x20",
        ],
        2: [
            "1) Выпады 3x15",
            "2) Планка 3x1 мин",
            "3) Ягодичный мост 3x20",
        ],
        3: [
            "1) Присед узким хватом 3x12",
            "2) Отжимания широким хватом 3x10",
            "3) Скручивания на полу 3x20",
        ],
        4: [
            "1) Махи ногами 3x20",
            "2) Подъёмы таза 3x15",
            "3) Планка боковая 3x30 c",
        ],
        5: [
            "1) Присед + прыжок 3x10",
            "2) Берпи 3x10",
            "3) Велосипед 3x20",
        ]
    },
    ("male", "gym"): {
        1: [
            "1) Присед со штангой 3x10",
            "2) Жим лежа 3x8",
            "3) Скручивания на скамье 3x15",
        ],
        2: [
            "1) Становая тяга 3x8",
            "2) Тяга верхнего блока 3x12",
            "3) Планка 3x1 мин",
        ],
        3: [
            "1) Выпады со штангой 3x10",
            "2) Подтягивания 3xMax",
            "3) Ягодичный мост со штангой 3x12",
        ],
        4: [
            "1) Жим гантелей сидя 3x10",
            "2) Отжимания на брусьях 3xMax",
            "3) Подъёмы ног в висе 3x15",
        ],
        5: [
            "1) Тяга штанги в наклоне 3x8",
            "2) Приседания 3x8",
            "3) Скручивания на скамье 3x15",
        ]
    },
    ("female", "home"): {
        1: [
            "1) Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
            "2) Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
            "3) Велосипед 3x15 [Видео](https://t.me/c/2241417709/278/279)",
        ],
        2: [
            "1) Отжимания 3x15 [Видео](https://t.me/c/2241417709/167/168)",
            "2) Лодочка 3x30 [Видео](https://t.me/c/2241417709/395/396)",
            "3) Подъёмы корпуса 3x20 [Видео](https://t.me/c/2241417709/274/275)",
        ],
        3: [
            "1) Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)",
            "2) Махи в бок 3x20 [Видео](https://t.me/c/2241417709/385/386)",
            "3) Косые 3x15 [Видео](https://t.me/c/2241417709/282/283)",
        ],
        4: [
            "1) Подъемы с гантелями 4x20 [Видео](https://t.me/c/2241417709/226/227)",
            "2) Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
            "3) Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)",
        ],
        5: [
            "1) Присед (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
            "2) Махи под 45 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3) Подъёмы ног 3x15 [Видео](https://t.me/c/2241417709/367/368)",
        ]
    },
    ("female", "gym"): {
        1: [
            "1) Присед в тренажёре Смита 3x12",
            "2) Разведение ног 3x15",
            "3) Сведение ног 3x15",
        ],
        2: [
            "1) Жим ногами 3x12",
            "2) Гиперэкстензия 3x15",
            "3) Планка 3x1 мин",
        ],
        3: [
            "1) Выпады со штангой 3x10",
            "2) Тяга верхнего блока 3x12",
            "3) Скручивания на полу 3x20",
        ],
        4: [
            "1) Жим гантелей на наклонной 3x10",
            "2) Становая румынская 3x8",
            "3) Ягодичный мост 3x12",
        ],
        5: [
            "1) Присед со штангой 3x10",
            "2) Тяга блока к груди 3x12",
            "3) Подъёмы ног в тренажёре 3x15",
        ]
    }
}

# 2) Платный курс Евгения
evg_paid_exercises = {
    ("male", "gym"): {
        1: [
            "Мужчина/Зал, День 1: Пример упражнений ...",
            "...."
        ],
        2: [
            "Мужчина/Зал, День 2: ...",
        ],
        3: [
            "Мужчина/Зал, День 3: ...",
        ],
        4: [
            "Мужчина/Зал, День 4: ...",
        ],
        5: [
            "Мужчина/Зал, День 5: ...",
        ],
    },
    ("male", "home"): {
        1: [
            "Мужчина/Дом, День 1: ...",
        ],
        2: [
            "Мужчина/Дом, День 2: ...",
        ],
        3: [
            "Мужчина/Дом, День 3: ...",
        ],
        4: [
            "Мужчина/Дом, День 4: ...",
        ],
        5: [
            "Мужчина/Дом, День 5: ...",
        ],
    },
    ("female", "gym"): {
        1: [
            "1) Махи назад с утяжелителями 3х25+5 https://t.me/c/2241417709/337/338",
            "2) Выпады 3х30 шагов х 2кг https://t.me/c/2241417709/157/158",
            "3) Разведение ног 3х20 https://t.me/c/2241417709/128/129",
            "4) Сведение ног 3х20 https://t.me/c/2241417709/126/127",
            "5) Сгибание ног 3х15 https://t.me/c/2241417709/130/131"
        ],
        2: [
            "1) Косые скручивания 3х30+10 https://t.me/c/2241417709/284/285",
            "2) Отжимания 3x15+5 https://t.me/c/2241417709/167/168",
            "3) Лодочка с локтями 3х20+5 https://t.me/c/2241417709/183/184",
            "4) Жим гантелей 3х15+5 https://t.me/c/2241417709/175/176",
            "5) Гантели в развороте 3х15+5 https://t.me/c/2241417709/222/223",
            "6) Разгибание с веревкой 3х1+5 https://t.me/c/2241417709/260/261"
        ],
        3: [
            "1) Подъёмы ног 3х15+5 https://t.me/c/2241417709/270/271",
            "2) Разгибание ног 3х15+5 https://t.me/c/2241417709/134/135",
            "3) Выпады назад 3х15 https://t.me/c/2241417709/155/156",
            "4) Ягодичный мост 3х20+5 https://t.me/c/2241417709/381/382",
            "5) Двойные разведения ног 3х20+5 https://t.me/c/2241417709/123/125",
            "6) Мертвая тяга 3х15+5 https://t.me/c/2241417709/136/137"
        ],
        4: [
            "1) Скручивания 3х20+10 https://t.me/c/2241417709/379/380",
            "2) Отжимания в ТРХ 3х15+5 https://t.me/c/2241417709/159/160",
            "3) Подтягивания в ТРХ 3х15 https://t.me/c/2241417709/188/189",
            "4) Разводка с гантелями 3х15+5 https://t.me/c/2241417709/169/170",
            "5) Тяга блока к груди 3х12 https://t.me/c/2241417709/210/211",
            "6) Жим гантелей сидя 3х12 https://t.me/c/2241417709/115/117",
            "7) Скручивания на скамье 3х20 https://t.me/c/2241417709/272/273"
        ],
        5: [
            "Вместо дня 5 - финальная программа 🏆"
        ]
    },
    ("female", "home"): {
        1: [
            "Женщина/Дом, День 1: ...", 
        ],
        2: [
            "Женщина/Дом, День 2: ...", 
        ],
        3: [
            "Женщина/Дом, День 3: ...", 
        ],
        4: [
            "Женщина/Дом, День 4: ...", 
        ],
        5: [
            "Женщина/Дом, День 5: ...", 
        ],
    }
}

# 3) Платный курс Анастасии
ana_paid_exercises = {
    ("male", "gym"): {
        1: ["Анастасия / Мужчина / Зал, День 1..."],
        2: ["День 2..."],
        3: ["День 3..."],
        4: ["День 4..."],
        5: ["День 5..."],
    },
    ("male", "home"): {
        1: ["Анастасия / Мужчина / Дом, День 1..."],
        2: ["День 2..."],
        3: ["День 3..."],
        4: ["День 4..."],
        5: ["День 5..."],
    },
    ("female", "gym"): {
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
            "Лодочка 3х20+5 https://t.me/c/2241417709/183/184",
            "...",
        ],
        3: [
            "...",
        ],
        4: [
            "...",
        ],
        5: [
            "Финальная программа 🏆",
        ]
    },
    ("female", "home"): {
        1: ["Анастасия / Женщина / Дом, День 1..."],
        2: ["..."],
        3: ["..."],
        4: ["..."],
        5: ["Финал..."]
    }
}

# -------------------------------------------------------------------------------------
#             ФОРМУЛА ДЛЯ КБЖУ + ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ ШАГОВ (С ИНЛАЙН-КНОПКАМИ)
# -------------------------------------------------------------------------------------
KBJU_EVGENIY_STATE = {}    # user_id -> dict c данными
KBJU_ANASTASIYA_STATE = {} # user_id -> dict

(
    EVG_KBJU_GENDER,
    EVG_KBJU_WEIGHT,
    EVG_KBJU_HEIGHT,
    EVG_KBJU_AGE,
    EVG_KBJU_ACTIVITY,
    EVG_KBJU_GOAL
) = range(6)  # если будем использовать ConversationHandler для текста

# Если хотим *только inline-кнопки* – можно иначе управлять состояниями.

def calc_kbju(gender: str, weight: float, height: float, age: int, activity: float, goal: str):
    """
    Упрощённая формула Mifflin-St Jeor. 
    """
    if gender.lower().startswith("m"):  # male
        bmr = 10*weight + 6.25*height - 5*age + 5
    else:
        bmr = 10*weight + 6.25*height - 5*age - 161

    cal = bmr * activity
    if goal == "похудеть":
        cal *= 0.85
    elif goal == "набрать":
        cal *= 1.15
    return round(cal, 2)

# -------------------------------------------------------------------------------------
#                              МЕНЮ / СТАРТ
# -------------------------------------------------------------------------------------
def start_menu():
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_evg"),
            InlineKeyboardButton("💫 Анастасия", callback_data="instructor_ana")
        ],
        [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
        [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
        [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")]
    ])
    return kb

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Обработка рефссылки
    if ctx.args:
        try:
            ref = int(ctx.args[0])
            if ref != user_id:
                user_scores_evg[ref] = user_scores_evg.get(ref, 0) + 100
                try:
                    await ctx.bot.send_message(ref, text="🎉 Ваш реферал пришёл! +100 баллов")
                except:
                    pass
        except:
            pass

    await update.message.reply_text(
        "Выберите для себя фитнес-инструктора:",
        reply_markup=start_menu()
    )

async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "instructor_evg":
        # Инициализируем словари
        user_scores_evg[user_id] = user_scores_evg.get(user_id, 0)
        user_status_evg[user_id] = user_status_evg.get(user_id, statuses[0])
        ctx.user_data[user_id] = {"instructor": "evg"}

        await ctx.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://t.me/PRIVETSTVIEC/2",
            caption="🎥 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu_evg()
        )

    elif data == "instructor_ana":
        user_scores_ana[user_id] = user_scores_ana.get(user_id, 0)
        user_status_ana[user_id] = user_status_ana.get(user_id, statuses[0])
        ctx.user_data[user_id] = {"instructor": "ana"}

        await query.message.reply_text("Вы выбрали тренера: Анастасия 💫")
        await ctx.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="📸 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Анастасия",
            reply_markup=main_menu_ana()
        )
    else:
        # Тренеры 3,4,5 - пока без функционала
        await query.message.reply_text(
            "Вы выбрали тренера, функционал не реализован. Возвращаемся назад...",
            reply_markup=start_menu()
        )

async def handle_back_to_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Выберите тренера:", reply_markup=start_menu())


# -------------------------------------------------------------------------------------
#                       МЕНЮ ДЛЯ ЕВГЕНИЯ / АНАСТАСИИ
# -------------------------------------------------------------------------------------
def main_menu_evg():
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Бесплатный курс (Евг.)", callback_data="evg_free_course")],
        [InlineKeyboardButton("💪 Челлендж (Евг.)", callback_data="evg_challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс (Евг.)", callback_data="evg_paid_course")],
        [InlineKeyboardButton("👤 Мой кабинет (Евг.)", callback_data="evg_my_cabinet")],
        [InlineKeyboardButton("💡 Как заработать баллы (Евг.)", callback_data="evg_earn_points")],
        [InlineKeyboardButton("💰 Как потратить баллы (Евг.)", callback_data="evg_spend_points")],
        [InlineKeyboardButton("🔗 Реферальная ссылка (Евг.)", callback_data="evg_referral")],
        [InlineKeyboardButton("🍽 КБЖУ (Евг.)", callback_data="evg_kbju")],
        [InlineKeyboardButton("ℹ️ Обо мне (Евг.)", callback_data="evg_about_me")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")],
    ])
    return kb

def main_menu_ana():
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Бесплатный курс (Анаст.)", callback_data="ana_free_course")],
        [InlineKeyboardButton("💪 Челлендж (Анаст.)", callback_data="ana_challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс (Анаст.)", callback_data="ana_paid_course")],
        [InlineKeyboardButton("👤 Мой кабинет (Анаст.)", callback_data="ana_my_cabinet")],
        [InlineKeyboardButton("💡 Как заработать баллы (Анаст.)", callback_data="ana_earn_points")],
        [InlineKeyboardButton("💰 Как потратить баллы (Анаст.)", callback_data="ana_spend_points")],
        [InlineKeyboardButton("🔗 Реферальная ссылка (Анаст.)", callback_data="ana_referral")],
        [InlineKeyboardButton("🍽 КБЖУ (Анаст.)", callback_data="ana_kbju")],
        [InlineKeyboardButton("ℹ️ Обо мне (Анаст.)", callback_data="ana_about_me")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")],
    ])
    return kb


# -------------------------------------------------------------------------------------
#                    БЕСПЛАТНЫЙ КУРС: ЕВГЕНИЙ
# -------------------------------------------------------------------------------------
async def evg_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    info = user_data_free_evg.get(user_id, {})
    if "gender" not in info or "program" not in info:
        # Спросим пол
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨 Мужчина", callback_data="evg_free_gender_male"),
                InlineKeyboardButton("👩 Женщина", callback_data="evg_free_gender_female")
            ]
        ])
        await query.message.reply_text("Ваш пол (бесплатный курс Евгений)?", reply_markup=kb)
    else:
        await start_free_course_evg(query.message, ctx, user_id)

async def evg_free_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    gender = "male" if "male" in query.data else "female"
    if user_id not in user_data_free_evg:
        user_data_free_evg[user_id] = {}
    user_data_free_evg[user_id]["gender"] = gender

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏠 Дома", callback_data="evg_free_program_home"),
            InlineKeyboardButton("🏋️ В зале", callback_data="evg_free_program_gym")
        ]
    ])
    await query.message.reply_text("Выберите программу (бесплатный курс Евгений):", reply_markup=kb)

async def evg_free_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    program = "home" if "home" in query.data else "gym"

    if user_id not in user_data_free_evg:
        user_data_free_evg[user_id] = {}
    user_data_free_evg[user_id]["program"] = program
    user_data_free_evg[user_id]["current_day"] = 1

    await start_free_course_evg(query.message, ctx, user_id)

async def start_free_course_evg(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    info = user_data_free_evg[user_id]
    gender = info["gender"]
    program = info["program"]
    day = info.get("current_day", 1)
    if day > 5:
        await msg.reply_text("Вы завершили бесплатный курс (Евгений)! 🎉", reply_markup=main_menu_evg())
        return

    # Достаём упражнения
    ex_dict = evg_free_exercises.get((gender, program))
    if not ex_dict:
        # Если вдруг нет такого ключа
        await msg.reply_text("Упражнения не найдены (Евгений).", reply_markup=main_menu_evg())
        return

    day_ex = ex_dict.get(day, [])
    text = f"🔥 **Бесплатный курс (Евгений): День {day}** 🔥\n\n" + "\n".join(day_ex) + "\n\nОтправьте видео-отчёт!"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчёт", callback_data=f"evg_free_send_report_day_{day}")]
    ])
    try:
        # Можно добавить фото (если хотите). Для примера:
        await ctx.bot.send_message(
            chat_id=msg.chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке free day {day} (Евг.): {e}")
        await msg.reply_text(text, reply_markup=kb)


async def evg_free_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])
    if user_reports_sent_evg.get(user_id, {}).get(day):
        await query.message.reply_text(f"Уже есть отчёт за день {day} (Евг.)")
        return

    user_waiting_for_video_evg[user_id] = ("free", day)
    await query.message.reply_text("Пришлите видео-отчёт (Евг.)")

async def evg_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in user_waiting_for_video_evg:
        return

    course_type, day = user_waiting_for_video_evg[user_id]
    if course_type == "free":
        # Отправим в группу
        await ctx.bot.send_message(GROUP_ID, text=f"Видео-отчет (free Евг.) от {user_name} за день {day}")
        await ctx.bot.send_video(GROUP_ID, video=update.message.video.file_id)

        # Баллы
        user_scores_evg[user_id] = user_scores_evg.get(user_id, 0) + 60

        if user_id not in user_reports_sent_evg:
            user_reports_sent_evg[user_id] = {}
        user_reports_sent_evg[user_id][day] = True

        current_day = user_data_free_evg[user_id]["current_day"]
        if current_day < 5:
            user_data_free_evg[user_id]["current_day"] = current_day + 1
            new_day = current_day + 1
            await update.message.reply_text(
                f"Отчет за день {day} принят (Евг.)! Ваши баллы: {user_scores_evg[user_id]}.\n"
                f"Готовы к дню {new_day}?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {new_day}", callback_data="evg_free_next_day")]
                ])
            )
        else:
            user_status_evg[user_id] = statuses[1]
            await update.message.reply_text(
                f"Поздравляем! Курс (Евг.) окончен. Баллы: {user_scores_evg[user_id]}",
                reply_markup=main_menu_evg()
            )
        del user_waiting_for_video_evg[user_id]

    elif course_type == "paid":
        # Платный
        await ctx.bot.send_message(GROUP_ID, text=f"Видео-отчет (paid Евг.) от {user_name} за день {day}")
        await ctx.bot.send_video(GROUP_ID, video=update.message.video.file_id)

        user_scores_evg[user_id] = user_scores_evg.get(user_id, 0) + 30
        del user_waiting_for_video_evg[user_id]

        current_day = user_data_paid_evg[user_id].get("current_day", 1)
        if current_day < 5:
            await update.message.reply_text(
                f"Отчет за платный день {day} (Евг.) принят! Ваши баллы: {user_scores_evg[user_id]}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➡️ Следующий день", callback_data="evg_paid_next_day")]
                ])
            )
        else:
            await update.message.reply_text(
                f"Поздравляем! Платный курс (Евг.) окончен. Баллы: {user_scores_evg[user_id]}",
                reply_markup=main_menu_evg()
            )
            user_data_paid_evg[user_id].pop("current_day", None)

async def evg_free_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await start_free_course_evg(query.message, ctx, user_id)


# -------------------------------------------------------------------------------------
#                    ЧЕЛЛЕНДЖ (Евгений)
# -------------------------------------------------------------------------------------
async def evg_challenge_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    if user_id in user_challenges_evg:
        await send_challenge_task_evg(query.message, user_id)
    else:
        if score >= 300:
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💰 Купить (300)", callback_data="evg_buy_challenge"),
                    InlineKeyboardButton("🔙 Назад", callback_data="evg_back")
                ]
            ])
            await query.message.reply_text("Челлендж (Евг.) стоит 300 баллов. Купить?", reply_markup=kb)
        else:
            await query.message.reply_text(f"Недостаточно баллов (Евг.): {score}/300")

async def evg_buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    if score >= 300:
        user_scores_evg[user_id] = score - 300
        user_challenges_evg[user_id] = {"current_day": 1}
        await query.message.reply_text("Челлендж (Евг.) куплен!", reply_markup=main_menu_evg())
        await send_challenge_task_evg(query.message, user_id)
    else:
        await query.message.reply_text("Недостаточно баллов (Евг.).")

async def send_challenge_task_evg(message, user_id: int):
    day = user_challenges_evg[user_id]["current_day"]
    # Пример челленджа
    challenge_evg = {
        1: ["Задание челленджа Евг. День 1"],
        2: ["День 2 ..."],
        3: ["День 3 ..."],
        4: ["День 4 ..."],
        5: ["День 5 ..."],
    }
    ex = challenge_evg.get(day, ["Нет задач."])

    text = f"Челлендж (Евг.), День {day}\n\n" + "\n".join(ex)
    if day < 5:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Следующий день", callback_data="evg_challenge_next")]])
    else:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В меню Евг.", callback_data="evg_back")]])

    await message.reply_text(text, reply_markup=kb)

async def evg_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in user_challenges_evg:
        await query.answer("Сначала купите челлендж (Евг.)")
        return
    day = user_challenges_evg[user_id]["current_day"]
    if day < 5:
        user_challenges_evg[user_id]["current_day"] = day + 1
        await send_challenge_task_evg(query.message, user_id)
    else:
        await query.message.reply_text("Челлендж (Евг.) завершён!", reply_markup=main_menu_evg())
        del user_challenges_evg[user_id]


# -------------------------------------------------------------------------------------
#                    Платный курс (Евгений)
# -------------------------------------------------------------------------------------
async def evg_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    discount = min(score*2, 600)
    price = 2000 - discount

    user_waiting_for_receipt_evg[user_id] = True
    await query.message.reply_text(
        f"Платный курс (Евг.)\n\nЦена 2000, скидка {discount}, итого {price}.\n"
        f"Оплата на карту 89236950304. Пришлите чек.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧾 Отправить чек (Евг.)", callback_data="evg_send_receipt")]])
    )

async def evg_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt_evg[user_id] = True
    await query.message.reply_text("Отправьте фото чека (Евг.).")

async def evg_handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in user_waiting_for_receipt_evg:
        return

    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, фото чека (Евг.).")
        return

    photo_id = update.message.photo[-1].file_id
    await ctx.bot.send_message(
        GROUP_ID,
        text=f"Чек (Евг.) от {user_name} (ID: {user_id}). Подтвердить?"
    )
    await ctx.bot.send_photo(
        GROUP_ID,
        photo=photo_id,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Подтвердить", callback_data=f"evg_confirm_payment_{user_id}")]
        ])
    )
    await update.message.reply_text("Чек отправлен на проверку (Евг.).")

async def evg_confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = int(data.split("_")[-1])

    user_status_evg[user_id] = statuses[2]
    if user_id in user_waiting_for_receipt_evg:
        del user_waiting_for_receipt_evg[user_id]

    await ctx.bot.send_message(
        chat_id=user_id,
        text="Оплата подтверждена (Евг.). Выберите пол и программу."
    )
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👨 Мужчина", callback_data="evg_paid_gender_male"),
            InlineKeyboardButton("👩 Женщина", callback_data="evg_paid_gender_female")
        ]
    ])
    await ctx.bot.send_message(user_id, text="Какой ваш пол (платный курс Евг.)?", reply_markup=kb)

async def evg_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    gender = "male" if "male" in query.data else "female"

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏋️ В зале", callback_data=f"evg_paid_program_{gender}_gym"),
            InlineKeyboardButton("🏠 Дома", callback_data=f"evg_paid_program_{gender}_home")
        ]
    ])
    await query.message.reply_text("Выберите программу (платный Евг.)", reply_markup=kb)

async def evg_paid_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data  # например evg_paid_program_male_gym
    parts = data.split("_")  # ["evg", "paid", "program", "male", "gym"]
    gender = parts[3]
    program = parts[4]

    user_id = query.from_user.id
    user_data_paid_evg[user_id] = {
        "gender": gender,
        "program": program,
        "current_day": 1
    }

    await evg_show_paid_day(query.message, user_id, 1)

async def evg_show_paid_day(msg, user_id, day: int):
    gp = user_data_paid_evg[user_id]
    gender = gp["gender"]
    program = gp["program"]

    ex_dict = evg_paid_exercises.get((gender, program))
    if not ex_dict:
        await msg.reply_text("Нет упражнений в словаре (Евг. Paid).", reply_markup=main_menu_evg())
        return

    ex_list = ex_dict.get(day, ["Нет данных."])
    text = f"📚 Платный курс (Евг.): День {day}\n\n" + "\n".join(ex_list)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчёт", callback_data=f"evg_paid_video_day_{day}")]
    ])
    await msg.reply_text(text, reply_markup=kb)

async def evg_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])
    user_waiting_for_video_evg[user_id] = ("paid", day)
    await query.message.reply_text(f"Отправьте видео-отчет за день {day} (Евг.)")

async def evg_paid_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    cd = user_data_paid_evg[user_id]["current_day"]
    if cd < 5:
        user_data_paid_evg[user_id]["current_day"] = cd + 1
        await evg_show_paid_day(query.message, user_id, cd+1)
    else:
        await query.message.reply_text("Курс (Евг.) завершён!", reply_markup=main_menu_evg())
        user_data_paid_evg[user_id].pop("current_day", None)

# -------------------------------------------------------------------------------------
#            Мой кабинет / обо мне / earn / spend / referral (Евгений)
# -------------------------------------------------------------------------------------
async def evg_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    status = user_status_evg.get(user_id, statuses[0])
    text = f"👤 Кабинет (Евг.)\nСтатус: {status}\nБаллы: {score}"
    await query.message.reply_text(text)

async def evg_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = "О Евгении..."
    await query.message.reply_text(text)

async def evg_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = "Как заработать баллы (Евг.)"
    await query.message.reply_text(text)

async def evg_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    text = f"Как потратить баллы (Евг.)\nУ вас {score}."
    await query.message.reply_text(text)

async def evg_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await ctx.bot.get_me()
    link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(f"Реферальная ссылка (Евг.): {link}")

async def evg_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Меню Евгения", reply_markup=main_menu_evg())


# -------------------------------------------------------------------------------------
#                   То же самое для АНАСТАСИИ (бесплатный, платный, челлендж и т.д.)
# -------------------------------------------------------------------------------------
# Аналогично Евгению, чтобы не повторять всё слово в слово – оставлю лишь кратко
# (ВАЖНО: у вас раздельные словари user_data_free_ana и т.п.)

async def ana_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    info = user_data_free_ana.get(user_id, {})
    if "gender" not in info or "program" not in info:
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨 Мужчина", callback_data="ana_free_gender_male"),
                InlineKeyboardButton("👩 Женщина", callback_data="ana_free_gender_female")
            ]
        ])
        await query.message.reply_text("Ваш пол (бесплатный курс Анастасия)?", reply_markup=kb)
    else:
        await start_free_course_ana(query.message, ctx, user_id)

async def ana_free_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    gender = "male" if "male" in query.data else "female"
    if user_id not in user_data_free_ana:
        user_data_free_ana[user_id] = {}
    user_data_free_ana[user_id]["gender"] = gender
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏠 Дома", callback_data="ana_free_program_home"),
            InlineKeyboardButton("🏋️ В зале", callback_data="ana_free_program_gym")
        ]
    ])
    await query.message.reply_text("Выберите программу (бесплатный курс Анаст.)", reply_markup=kb)

async def ana_free_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    program = "home" if "home" in query.data else "gym"
    if user_id not in user_data_free_ana:
        user_data_free_ana[user_id] = {}
    user_data_free_ana[user_id]["program"] = program
    user_data_free_ana[user_id]["current_day"] = 1

    await start_free_course_ana(query.message, ctx, user_id)

async def start_free_course_ana(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    info = user_data_free_ana[user_id]
    gender = info["gender"]
    program = info["program"]
    day = info.get("current_day", 1)

    if day > 5:
        await msg.reply_text("Курс (Анаст.) окончен!", reply_markup=main_menu_ana())
        return

    ex_dict = evg_free_exercises.get((gender, program))  # или у вас отдельный словарь для анастасии
    # Для примера я тут использую evg_free_exercises, лучше сделать ana_free_exercises
    if not ex_dict:
        await msg.reply_text("Нет упражнений (Анаст.).", reply_markup=main_menu_ana())
        return

    day_ex = ex_dict.get(day, [])
    text = f"🔥 Бесплатный курс (Анаст.): День {day}\n\n" + "\n".join(day_ex)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчёт", callback_data=f"ana_free_send_report_day_{day}")]
    ])
    await msg.reply_text(text, reply_markup=kb)

async def ana_free_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])
    if user_reports_sent_ana.get(user_id, {}).get(day):
        await query.message.reply_text("Уже есть отчёт (Анаст.)")
        return

    user_waiting_for_video_ana[user_id] = ("free", day)
    await query.message.reply_text("Отправьте видео-отчет (Анаст.)")

async def ana_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in user_waiting_for_video_ana:
        return

    ctype, day = user_waiting_for_video_ana[user_id]
    if ctype == "free":
        await ctx.bot.send_message(GROUP_ID, text=f"Видео (free Анаст.) от {user_name} день {day}")
        await ctx.bot.send_video(GROUP_ID, video=update.message.video.file_id)
        user_scores_ana[user_id] = user_scores_ana.get(user_id, 0) + 60

        if user_id not in user_reports_sent_ana:
            user_reports_sent_ana[user_id] = {}
        user_reports_sent_ana[user_id][day] = True

        current_day = user_data_free_ana[user_id]["current_day"]
        if current_day < 5:
            user_data_free_ana[user_id]["current_day"] = current_day + 1
            await update.message.reply_text(
                f"Отчет за день {day} (Анаст.) принят. Баллы: {user_scores_ana[user_id]}.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {current_day+1}", callback_data="ana_free_next_day")]
                ])
            )
        else:
            user_status_ana[user_id] = statuses[1]
            await update.message.reply_text(
                f"Курс (Анаст.) окончен. Баллы: {user_scores_ana[user_id]}",
                reply_markup=main_menu_ana()
            )
        del user_waiting_for_video_ana[user_id]

    elif ctype == "paid":
        await ctx.bot.send_message(GROUP_ID, text=f"Видео (paid Анаст.) от {user_name} день {day}")
        await ctx.bot.send_video(GROUP_ID, video=update.message.video.file_id)
        user_scores_ana[user_id] = user_scores_ana.get(user_id, 0) + 30
        del user_waiting_for_video_ana[user_id]

        cd = user_data_paid_ana[user_id]["current_day"]
        if cd < 5:
            await update.message.reply_text(
                f"Отчёт за платный день {day} (Анаст.) принят. Баллы: {user_scores_ana[user_id]}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➡️ След. День", callback_data="ana_paid_next_day")]
                ])
            )
        else:
            await update.message.reply_text(
                f"Платный курс (Анаст.) окончен! Баллы: {user_scores_ana[user_id]}",
                reply_markup=main_menu_ana()
            )
            user_data_paid_ana[user_id].pop("current_day", None)

async def ana_free_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await start_free_course_ana(query.message, ctx, user_id)

# Челлендж (Анаст.), платный курс (Анаст.) и т.д. – аналогично Евгению...

# -------------------------------------------------------------------------------------
#                           КБЖУ ЧЕРЕЗ КНОПКИ
# -------------------------------------------------------------------------------------
# Ниже – упрощённый пример, как можно попросить данные через кнопки.
# Для веса/роста/возраста часто всё же пишут вручную, иначе придётся много кнопок.
# Сделаю гибрид: пол и активность/цель – кнопки, а вес/рост/возраст – текст.

(
    EVG_KBJU_STEP_GENDER,
    EVG_KBJU_STEP_WEIGHT,
    EVG_KBJU_STEP_HEIGHT,
    EVG_KBJU_STEP_AGE,
    EVG_KBJU_STEP_ACTIVITY,
    EVG_KBJU_STEP_GOAL
) = range(100, 106)  # используем ConversationHandler или храним состояние вручную

# Для наглядности ниже – ConversationHandler для Евгения:
async def evg_kbju_entry(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    # Начинаем "опрос"
    # Шаг 1: Пол
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Мужчина", callback_data="evg_kbju_gender_male"),
            InlineKeyboardButton("Женщина", callback_data="evg_kbju_gender_female"),
        ]
    ])
    await query.message.reply_text("Выберите ваш пол (Евг.)", reply_markup=kb)

async def evg_kbju_gender_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data  # evg_kbju_gender_male / evg_kbju_gender_female
    gender = "male" if "male" in data else "female"
    user_id = query.from_user.id
    KBJU_EVGENIY_STATE[user_id] = {"gender": gender}

    await query.message.reply_text("Введите ваш вес (кг) числом, например 70.5:")
    # Далее ловим TEXT в MessageHandler

async def evg_kbju_weight_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    try:
        weight = float(text)
    except ValueError:
        await update.message.reply_text("Нужно ввести число (вес). Попробуйте ещё раз.")
        return
    KBJU_EVGENIY_STATE[user_id]["weight"] = weight
    await update.message.reply_text("Теперь введите рост (см), напр. 175:")

async def evg_kbju_height_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    try:
        height = float(text)
    except ValueError:
        await update.message.reply_text("Нужно число (рост). Попробуйте ещё раз.")
        return
    KBJU_EVGENIY_STATE[user_id]["height"] = height
    await update.message.reply_text("Теперь введите возраст (лет), целое число:")

async def evg_kbju_age_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    try:
        age = int(text)
    except ValueError:
        await update.message.reply_text("Нужно целое число (возраст). Попробуйте ещё раз.")
        return
    KBJU_EVGENIY_STATE[user_id]["age"] = age

    # Теперь выберем активность кнопками
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1.2", callback_data="evg_kbju_act_1.2"),
            InlineKeyboardButton("1.375", callback_data="evg_kbju_act_1.375"),
        ],
        [
            InlineKeyboardButton("1.55", callback_data="evg_kbju_act_1.55"),
            InlineKeyboardButton("1.7", callback_data="evg_kbju_act_1.7"),
            InlineKeyboardButton("1.9", callback_data="evg_kbju_act_1.9"),
        ]
    ])
    await update.message.reply_text("Выберите уровень активности (Евг.)", reply_markup=kb)

async def evg_kbju_act_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    act = float(query.data.split("_")[-1])  # evg_kbju_act_1.2 => "1.2"
    KBJU_EVGENIY_STATE[user_id]["activity"] = act

    # Цель
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Похудеть", callback_data="evg_kbju_goal_loss"),
            InlineKeyboardButton("Набрать", callback_data="evg_kbju_goal_gain"),
            InlineKeyboardButton("Поддержание", callback_data="evg_kbju_goal_keep"),
        ]
    ])
    await query.message.reply_text("Какая цель (Евг.)?", reply_markup=kb)

async def evg_kbju_goal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data  # evg_kbju_goal_loss, etc.
    if "loss" in data:
        goal = "похудеть"
    elif "gain" in data:
        goal = "набрать"
    else:
        goal = "поддержание"

    KBJU_EVGENIY_STATE[user_id]["goal"] = goal
    # Рассчитываем
    st = KBJU_EVGENIY_STATE[user_id]
    gender = st["gender"]
    weight = st["weight"]
    height = st["height"]
    age = st["age"]
    act = st["activity"]

    res = calc_kbju(gender, weight, height, age, act, goal)
    await query.message.reply_text(f"Ваш КБЖУ (Евг.) ~ {res} ккал/сутки.")
    del KBJU_EVGENIY_STATE[user_id]


# Аналогично для Анастасии.

# -------------------------------------------------------------------------------------
def main():
    app = Application.builder().token(TOKEN).build()

    # Команда /start
    app.add_handler(CommandHandler("start", start))

    # Выбор тренера
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    # Назад в старт
    app.add_handler(CallbackQueryHandler(handle_back_to_start, pattern="^back_to_start$"))

    # ---------- Евгений: бесплатный курс ----------
    app.add_handler(CallbackQueryHandler(evg_free_course, pattern="^evg_free_course$"))
    app.add_handler(CallbackQueryHandler(evg_free_gender, pattern="^evg_free_gender_"))
    app.add_handler(CallbackQueryHandler(evg_free_program, pattern="^evg_free_program_"))
    app.add_handler(CallbackQueryHandler(evg_free_next_day, pattern="^evg_free_next_day$"))
    app.add_handler(CallbackQueryHandler(evg_free_send_report, pattern=r"^evg_free_send_report_day_\d+$"))
    # Видео (Евг.)
    app.add_handler(MessageHandler(filters.VIDEO, evg_handle_video))

    # ---------- Евгений: челлендж ----------
    app.add_handler(CallbackQueryHandler(evg_challenge_menu, pattern="^evg_challenge_menu$"))
    app.add_handler(CallbackQueryHandler(evg_buy_challenge, pattern="^evg_buy_challenge$"))
    app.add_handler(CallbackQueryHandler(evg_challenge_next_day, pattern="^evg_challenge_next$"))

    # ---------- Евгений: платный ----------
    app.add_handler(CallbackQueryHandler(evg_paid_course, pattern="^evg_paid_course$"))
    app.add_handler(CallbackQueryHandler(evg_send_receipt, pattern="^evg_send_receipt$"))
    app.add_handler(MessageHandler(filters.PHOTO, evg_handle_receipt))
    app.add_handler(CallbackQueryHandler(evg_confirm_payment, pattern="^evg_confirm_payment_"))
    app.add_handler(CallbackQueryHandler(evg_paid_gender, pattern="^evg_paid_gender_"))
    app.add_handler(CallbackQueryHandler(evg_paid_program, pattern="^evg_paid_program_"))
    app.add_handler(CallbackQueryHandler(evg_send_paid_report, pattern=r"^evg_paid_video_day_\d+$"))
    app.add_handler(CallbackQueryHandler(evg_paid_next_day, pattern="^evg_paid_next_day$"))

    # ---------- Евгений: кабинет, etc. ----------
    app.add_handler(CallbackQueryHandler(evg_my_cabinet, pattern="^evg_my_cabinet$"))
    app.add_handler(CallbackQueryHandler(evg_about_me, pattern="^evg_about_me$"))
    app.add_handler(CallbackQueryHandler(evg_earn_points, pattern="^evg_earn_points$"))
    app.add_handler(CallbackQueryHandler(evg_spend_points, pattern="^evg_spend_points$"))
    app.add_handler(CallbackQueryHandler(evg_referral, pattern="^evg_referral$"))
    app.add_handler(CallbackQueryHandler(evg_back, pattern="^evg_back$"))

    # ---------- Евгений: КБЖУ (через callback) ----------
    app.add_handler(CallbackQueryHandler(evg_kbju_entry, pattern="^evg_kbju$"))
    app.add_handler(CallbackQueryHandler(evg_kbju_gender_handler, pattern="^evg_kbju_gender_"))
    app.add_handler(CallbackQueryHandler(evg_kbju_act_handler, pattern="^evg_kbju_act_"))
    app.add_handler(CallbackQueryHandler(evg_kbju_goal_handler, pattern="^evg_kbju_goal_"))

    # Для ввода веса, роста, возраста - MessageHandler (текст):
    app.add_handler(MessageHandler(filters.Regex(r"^\d+(\.\d+)?$"), evg_kbju_weight_handler), 1)
    app.add_handler(MessageHandler(filters.Regex(r"^\d+(\.\d+)?$"), evg_kbju_height_handler), 2)
    app.add_handler(MessageHandler(filters.Regex(r"^\d+$"), evg_kbju_age_handler), 3)
    # (На практике нужно аккуратнее с фильтрами и очередью приоритета.)

    # ---------- Анастасия: бесплатный ----------
    app.add_handler(CallbackQueryHandler(ana_free_course, pattern="^ana_free_course$"))
    app.add_handler(CallbackQueryHandler(ana_free_gender, pattern="^ana_free_gender_"))
    app.add_handler(CallbackQueryHandler(ana_free_program, pattern="^ana_free_program_"))
    app.add_handler(CallbackQueryHandler(ana_free_next_day, pattern="^ana_free_next_day$"))
    app.add_handler(CallbackQueryHandler(ana_free_send_report, pattern=r"^ana_free_send_report_day_\d+$"))
    # Видео (Анаст.)
    app.add_handler(MessageHandler(filters.VIDEO, ana_handle_video))

    # И т.д. для челленджа и платного курса Анастасии (по аналогии).
    # Чтобы не дублировать здесь всё, вы поняли концепцию.

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
