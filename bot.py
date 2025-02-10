import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ===== Токен и ID группы =====
TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# ===== Глобальные словари (Раздельно для Евгения и Анастасии) =====
# -- Евгений
user_scores_evg = {}
user_status_evg = {}
user_reports_sent_evg = {}
user_waiting_for_video_evg = {}
user_waiting_for_receipt_evg = {}
user_challenges_evg = {}
user_data_free_evg = {}   # хранение (gender, program, current_day) для бесплатного курса
user_data_paid_evg = {}   # хранение current_day для платного курса

# -- Анастасия
user_scores_ana = {}
user_status_ana = {}
user_reports_sent_ana = {}
user_waiting_for_video_ana = {}
user_waiting_for_receipt_ana = {}
user_challenges_ana = {}
user_data_free_ana = {}
user_data_paid_ana = {}

# Статусы примерные
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# ====== Константы для ConversationHandler (КБЖУ) ======
(
    EVG_KBJU_GENDER,
    EVG_KBJU_WEIGHT,
    EVG_KBJU_HEIGHT,
    EVG_KBJU_AGE,
    EVG_KBJU_ACTIVITY,
    EVG_KBJU_GOAL,
) = range(6)

(
    ANA_KBJU_GENDER,
    ANA_KBJU_WEIGHT,
    ANA_KBJU_HEIGHT,
    ANA_KBJU_AGE,
    ANA_KBJU_ACTIVITY,
    ANA_KBJU_GOAL,
) = range(16, 22)  # Разные номера, чтобы ConversationHandler’ы не путались

# ===== Функции для расчёта КБЖУ =====
def calculate_kbju(gender: str, weight: float, height: float, age: int, activity: float, goal: str) -> float:
    """
    Пример упрощённой формулы Mifflin-St Jeor:
    BMR (муж)   = 10 * вес + 6.25 * рост - 5 * возраст + 5
    BMR (жен)   = 10 * вес + 6.25 * рост - 5 * возраст - 161

    Затем умножаем на коэффициент активности:
      - Малоподвижный (1.2)
      - Лёгкая активность (1.375)
      - Средняя активность (1.55)
      - Высокая (1.7)
      - Экстра (1.9)

    Затем коррекция на цель:
      - Похудеть: умножаем на 0.85 (примерно -15%)
      - Набрать: умножаем на 1.15 (примерно +15%)
      - Поддержание: умножаем на 1.0
    """
    if gender.lower() in ["м", "m"]:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    cal = bmr * activity

    if goal == "похудеть":
        cal *= 0.85
    elif goal == "набрать":
        cal *= 1.15
    else:
        cal *= 1.0

    return round(cal, 2)


# --------------------------------------------------------------------------------------
#                             МЕНЮ ДЛЯ ЕВГЕНИЯ
# --------------------------------------------------------------------------------------
def main_menu_evg():
    """
    Главное меню для Евгения Курочкина.
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Бесплатный курс (Евгений)", callback_data="evg_free_course")],
        [InlineKeyboardButton("💪 Челлендж (Евгений)", callback_data="evg_challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс (Евгений)", callback_data="evg_paid_course")],
        [InlineKeyboardButton("👤 Мой кабинет (Евгений)", callback_data="evg_my_cabinet")],
        [InlineKeyboardButton("💡 Как заработать баллы", callback_data="evg_earn_points")],
        [InlineKeyboardButton("💰 Как потратить баллы", callback_data="evg_spend_points")],
        [InlineKeyboardButton("🔗 Реферальная ссылка", callback_data="evg_referral")],
        [InlineKeyboardButton("🍽 КБЖУ (Евгений)", callback_data="evg_kbju")],
        [InlineKeyboardButton("ℹ️ Обо мне (Евгений)", callback_data="evg_about_me")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")],
    ])


# --------------------------------------------------------------------------------------
#                             МЕНЮ ДЛЯ АНАСТАСИИ
# --------------------------------------------------------------------------------------
def main_menu_ana():
    """
    Главное меню для Анастасии.
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Бесплатный курс (Анастасия)", callback_data="ana_free_course")],
        [InlineKeyboardButton("💪 Челлендж (Анастасия)", callback_data="ana_challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс (Анастасия)", callback_data="ana_paid_course")],
        [InlineKeyboardButton("👤 Мой кабинет (Анастасия)", callback_data="ana_my_cabinet")],
        [InlineKeyboardButton("💡 Как заработать баллы", callback_data="ana_earn_points")],
        [InlineKeyboardButton("💰 Как потратить баллы", callback_data="ana_spend_points")],
        [InlineKeyboardButton("🔗 Реферальная ссылка", callback_data="ana_referral")],
        [InlineKeyboardButton("🍽 КБЖУ (Анастасия)", callback_data="ana_kbju")],
        [InlineKeyboardButton("ℹ️ Обо мне (Анастасия)", callback_data="ana_about_me")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")],
    ])


# --------------------------------------------------------------------------------------
#                    /start и выбор тренера (первое главное меню)
# --------------------------------------------------------------------------------------
def start_menu():
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_evg"),
         InlineKeyboardButton("💫 Анастасия", callback_data="instructor_ana")],
        [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
        [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
        [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")],
    ])
    return kb


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Хендлер команды /start: 
    1. Считывает ref (реф.ссылка), если есть.
    2. Показывает стартовое меню для выбора тренера.
    """
    user_id = update.effective_user.id

    # Если есть реф.ссылка
    if ctx.args:
        try:
            ref = int(ctx.args[0])
            if ref != user_id:
                # Можно начислить рефереру баллы (куда именно — по желанию; здесь «глобально» не уточняется, 
                # так как мы не знаем, какой тренер у реферера)
                # Но по задаче – "Вы получили 100 баллов!", поэтому просто начисляем в «ничейном» словаре
                # или можно хранить отдельно. Для примера добавим в user_scores_evg.
                user_scores_evg[ref] = user_scores_evg.get(ref, 0) + 100
                try:
                    await ctx.bot.send_message(
                        chat_id=ref,
                        text="🎉 Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!"
                    )
                except Exception as e:
                    logger.error(f"Реферальный бонус: {e}")
        except ValueError:
            pass

    # Показываем клавиатуру выбора тренера
    await update.message.reply_text(
        text="Выбери для себя фитнес-инструктора:",
        reply_markup=start_menu()
    )


# --------------------------------------------------------------------------------------
#               ОБРАБОТКА ВЫБОРА ТРЕНЕРА (ЕВГЕНИЙ / АНАСТАСИЯ / прочие)
# --------------------------------------------------------------------------------------
async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "instructor_evg":
        # Устанавливаем, что пользователь выбрал Евгения
        ctx.user_data[user_id] = {"instructor": "evg"}
        # Инициализируем счета, если надо
        user_scores_evg[user_id] = user_scores_evg.get(user_id, 0)
        user_status_evg[user_id] = user_status_evg.get(user_id, statuses[0])

        # Отправляем приветственное видео
        await ctx.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://t.me/PRIVETSTVIEC/2",  # Пример ссылки (из вашего кода)
            supports_streaming=True,
            caption="🎥 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu_evg()
        )

    elif data == "instructor_ana":
        # Устанавливаем, что пользователь выбрал Анастасию
        ctx.user_data[user_id] = {"instructor": "ana"}
        # Инициализируем счета и статус
        user_scores_ana[user_id] = user_scores_ana.get(user_id, 0)
        user_status_ana[user_id] = user_status_ana.get(user_id, statuses[0])

        await query.message.edit_text("Вы выбрали тренера: Анастасия 💫")
        await ctx.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="📸 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Анастасия",
            reply_markup=main_menu_ana()
        )

    else:
        # Прочие тренеры (3, 4, 5) - функционал пока не реализован
        if data == "instructor_3":
            sel = "Тренер 3 🏋️"
        elif data == "instructor_4":
            sel = "Тренер 4 🤼"
        elif data == "instructor_5":
            sel = "Тренер 5 🤸"
        else:
            sel = "неизвестный тренер"

        await query.message.edit_text(
            text=f"Вы выбрали тренера: {sel}. Функционал пока не реализован 🚧\n"
                 f"Вы будете перенаправлены в главное меню.",
        )
        # Можем ничего не показывать, т.к. у вас нет отдельных меню для этих тренеров


# --------------------------------------------------------------------------------------
#    ВОЗВРАТ К СТАРТОВОМУ МЕНЮ (после нажатия "назад" из меню конкретного тренера)
# --------------------------------------------------------------------------------------
async def handle_back_to_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text(
        text="Выбери для себя фитнес-инструктора:",
        reply_markup=start_menu()
    )


# --------------------------------------------------------------------------------------
#                           БЕСПЛАТНЫЙ КУРС - ЕВГЕНИЙ
# --------------------------------------------------------------------------------------
async def evg_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    При нажатии "🔥 Бесплатный курс (Евгений)" в главном меню Евгения.
    Сначала проверяем, есть ли в словаре user_data_free_evg[user_id] поля gender, program.
    Если нет - запрашиваем. Если да - сразу переходим к start_free_course_evg().
    """
    query = update.callback_query
    user_id = query.from_user.id

    user_info = user_data_free_evg.get(user_id, {})
    if "gender" not in user_info or "program" not in user_info:
        # Попросим пол
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨 Мужчина", callback_data="evg_free_gender_male"),
                InlineKeyboardButton("👩 Женщина", callback_data="evg_free_gender_female")
            ]
        ])
        await query.message.reply_text("Ваш пол (бесплатный курс Евгений):", reply_markup=kb)
    else:
        # Запускаем курс
        await start_free_course_evg(query.message, ctx, user_id)


async def handle_evg_free_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатываем выбор пола для бесплатного курса (Евгений)
    """
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


async def handle_evg_free_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатываем выбор программы (дом/зал) для бесплатного курса (Евгений).
    После выбора - стартуем сам курс.
    """
    query = update.callback_query
    user_id = query.from_user.id
    program = "home" if "home" in query.data else "gym"

    if user_id not in user_data_free_evg:
        user_data_free_evg[user_id] = {}

    user_data_free_evg[user_id]["program"] = program
    user_data_free_evg[user_id]["current_day"] = 1

    await start_free_course_evg(query.message, ctx, user_id)


async def start_free_course_evg(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    """
    Основная логика бесплатного курса Евгения:
    1. Проверяем gender + program. Если не (female/home) — говорим «в разработке».
       (По вашему коду видно, что только "женщина + дома" действительно прописаны упражнения.)
    2. Если текущий день > 5, значит курс пройден.
    3. Отправляем программу дня + кнопку «отправить отчет».
    """

    user_info = user_data_free_evg.get(user_id, {})
    if not (user_info.get("gender") == "female" and user_info.get("program") == "home"):
        await msg.reply_text("Пока в разработке (бесплатный курс Евгений) 🚧", reply_markup=main_menu_evg())
        return

    day = user_info.get("current_day", 1)
    if day > 5:
        await msg.reply_text("Вы завершили курс (Евгений)! 🎉", reply_markup=main_menu_evg())
        return

    # Фотографии
    photos = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
    }

    # Упражнения
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
    text = f"🔥 **Бесплатный курс (Евгений): День {day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день! 🎥"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"evg_free_send_report_day_{day}")]
    ])

    try:
        await ctx.bot.send_photo(
            chat_id=msg.chat_id,
            photo=photos.get(day),
            caption=text,
            parse_mode="Markdown",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото (Евгений free day {day}): {e}")
        await msg.reply_text(
            text="Ошибка: изображение не найдено. Продолжайте без фото.\n\n" + text,
            parse_mode="Markdown",
            reply_markup=kb
        )


async def evg_free_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    После нажатия "Отправить отчет" в бесплатном курсе Евгения.
    """
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])  # evg_free_send_report_day_X

    # Проверка, не отправлял ли уже
    if user_reports_sent_evg.get(user_id, {}).get(day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {day} (Евгений).")
        return

    # Ждем видео:
    user_waiting_for_video_evg[user_id] = ("free", day)
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день (Евгений) 🎥")


async def evg_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Приходит видео в чат. Проверяем, ждем ли мы это видео в контексте Евгения.
    """
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    # Проверяем, ждем ли мы видео именно от Евгения
    if user_id not in user_waiting_for_video_evg:
        return  # Игнорируем, если не ждем

    data = user_waiting_for_video_evg[user_id]
    course_type = data[0]

    if course_type == "free":
        day = data[1]
        # Отправляем в группу
        await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Видео-отчет (бесплатный курс Евгений) от {user_name} (ID: {user_id}) за день {day}.")
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

        # Начисляем баллы
        user_scores_evg[user_id] = user_scores_evg.get(user_id, 0) + 60

        # Помечаем, что отчет отправлен
        if user_id not in user_reports_sent_evg:
            user_reports_sent_evg[user_id] = {}
        user_reports_sent_evg[user_id][day] = True

        # Увеличиваем день
        current_day = user_data_free_evg[user_id]["current_day"]
        if current_day < 5:
            user_data_free_evg[user_id]["current_day"] = current_day + 1
            new_day = user_data_free_evg[user_id]["current_day"]

            await update.message.reply_text(
                f"Отчет за день {day} (Евгений) принят! 🎉\n"
                f"Ваши баллы: {user_scores_evg[user_id]}.\n"
                f"Готовы к следующему дню ({new_day})? ➡️",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {new_day}", callback_data="evg_free_next_day")]
                ])
            )
        else:
            user_status_evg[user_id] = statuses[1]  # Например, повысим статус
            await update.message.reply_text(
                f"Поздравляем! Вы завершили бесплатный курс (Евгений)! 🎉\n"
                f"Ваши баллы: {user_scores_evg[user_id]}.",
                reply_markup=main_menu_evg()
            )

        del user_waiting_for_video_evg[user_id]

    elif course_type == "paid":
        paid_day = data[1]
        # Отправляем отчет в группу
        await ctx.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Платный видео-отчет (Евгений) от {user_name} (ID: {user_id}) за день {paid_day}."
        )
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

        # Начислим баллы
        user_scores_evg[user_id] = user_scores_evg.get(user_id, 0) + 30

        # Уберем из очереди
        del user_waiting_for_video_evg[user_id]

        # Проверим, какой день платного курса
        current_day = user_data_paid_evg[user_id].get("current_day", 1)
        if current_day < 5:
            await update.message.reply_text(
                f"Отчет за платный день {paid_day} (Евгений) принят! 🎉\n"
                f"Ваши баллы: {user_scores_evg[user_id]}.\n"
                f"Готовы к следующему дню ({current_day + 1})? ➡️",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➡️ Следующий день", callback_data="evg_paid_next_day")]
                ])
            )
        else:
            await update.message.reply_text(
                f"Поздравляем! Вы завершили платный курс (Евгений)! 🎉\nВаши баллы: {user_scores_evg[user_id]}.",
                reply_markup=main_menu_evg()
            )
            user_data_paid_evg[user_id].pop("current_day", None)

    else:
        # Какая-то неизвестная ситуация
        await update.message.reply_text("Ошибка: неизвестный формат данных (Евгений).")


async def evg_free_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Пользователь нажал кнопку "➡️ День N" в бесплатном курсе Евгения.
    Просто повторяем логику старта курса, который покажет следующий день.
    """
    query = update.callback_query
    user_id = query.from_user.id
    await start_free_course_evg(query.message, ctx, user_id)


# --------------------------------------------------------------------------------------
#                    ЧЕЛЛЕНДЖ - ЕВГЕНИЙ
# --------------------------------------------------------------------------------------
async def evg_challenge_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Проверяем, куплен ли челлендж у Евгения, есть ли у пользователя 300+ баллов и т.д.
    """
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)

    if user_id in user_challenges_evg:
        # Уже купил челлендж
        await send_challenge_task_evg(query.message, user_id)
    else:
        # Проверяем баллы
        if score >= 300:
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💰 Купить доступ за 300 баллов", callback_data="evg_buy_challenge"),
                    InlineKeyboardButton("🔙 Назад", callback_data="evg_back")
                ]
            ])
            await query.message.reply_text("Доступ к челленджам (Евгений) стоит 300 баллов. Хотите приобрести?", reply_markup=kb)
        else:
            await query.message.reply_text(
                f"⚠️ Для доступа к челленджам (Евгений) нужно 300 баллов.\n"
                f"У вас: {score} баллов.\nПродолжайте тренировки!"
            )


async def evg_buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    if score >= 300:
        user_scores_evg[user_id] = score - 300
        user_challenges_evg[user_id] = {"current_day": 1}
        await query.message.reply_text("✅ Доступ к челленджам (Евгений) открыт!", reply_markup=main_menu_evg())
        await send_challenge_task_evg(query.message, user_id)
    else:
        await query.message.reply_text("⚠️ Недостаточно баллов для покупки доступа к челленджу (Евгений)!")


async def send_challenge_task_evg(message, user_id: int):
    """
    Отправляем задание челленджа (Евгений) на текущий день.
    """
    day = user_challenges_evg[user_id]["current_day"]
    # Пример челленджа на 5 дней
    exercises_by_day = {
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
    exercises = exercises_by_day.get(day, [])
    text = f"💪 **Челлендж (Евгений): День {day}** 💪\n\n" + "\n".join(exercises)

    if day < 5:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Следующий день", callback_data="evg_challenge_next")]
        ])
    else:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="evg_back")]
        ])

    await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def evg_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_challenges_evg:
        await query.answer("Сначала купите челлендж (Евгений)! 🚧")
        return

    day = user_challenges_evg[user_id]["current_day"]
    if day < 5:
        user_challenges_evg[user_id]["current_day"] = day + 1
        await send_challenge_task_evg(query.message, user_id)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж (Евгений)! 🎉", reply_markup=main_menu_evg())
        del user_challenges_evg[user_id]


# --------------------------------------------------------------------------------------
#                   ПЛАТНЫЙ КУРС - ЕВГЕНИЙ
# --------------------------------------------------------------------------------------
async def evg_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Покупка платного курса у Евгения.
    Логика скидки: 1 балл = 2 рубля, макс скидка = 600.
    Итоговая сумма: 2000 - discount.
    """
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    discount = min(score * 2, 600)
    price = 2000 - discount

    user_waiting_for_receipt_evg[user_id] = True

    await query.message.reply_text(
        f"📚 **Платный курс (Евгений)** 📚\n\n"
        f"Стоимость курса: 2000 руб. 💵\n"
        f"Ваша скидка: {discount} руб. 🔖\n"
        f"Итоговая сумма: {price} руб. 💳\n\n"
        f"💳 Переведите сумму на карту: 89236950304 (Яндекс Банк) 🏦\n"
        f"После оплаты отправьте чек для проверки.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧾 Отправить чек", callback_data="evg_send_receipt")]])
    )


async def evg_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt_evg[user_id] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате (Евгений) 📸.")


async def evg_handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Обработка фото чека (Евгений).
    """
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in user_waiting_for_receipt_evg:
        return  # Игнорируем, если не ждем чек

    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фото чека (Евгений) 📸.")
        return

    # Отправим в группу для подтверждения
    photo_id = update.message.photo[-1].file_id
    await ctx.bot.send_message(chat_id=GROUP_ID, text=f"🧾 Чек (Евгений) от {user_name} (ID: {user_id}). Подтвердите оплату.")
    await ctx.bot.send_photo(chat_id=GROUP_ID, photo=photo_id,
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton("✅ Подтвердить", callback_data=f"evg_confirm_payment_{user_id}")]
                             ]))

    await update.message.reply_text("Чек отправлен на проверку (Евгений). Ожидайте подтверждения ⏳.")


async def evg_confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Админ в группе нажимает "Подтвердить" → пользователю открывается доступ к платному курсу Евгения.
    """
    query = update.callback_query
    data = query.data
    # data = "evg_confirm_payment_{user_id}"
    user_id = int(data.split("_")[-1])

    user_status_evg[user_id] = statuses[2]  # Примерно "Чемпион"
    if user_id in user_waiting_for_receipt_evg:
        del user_waiting_for_receipt_evg[user_id]

    await ctx.bot.send_message(
        chat_id=user_id,
        text="✅ Оплата подтверждена! (Евгений)\nВам открыт доступ к платному курсу. 🎉"
    )

    # Предлагаем выбрать пол
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👨 Мужчина", callback_data="evg_paid_gender_male"),
            InlineKeyboardButton("👩 Женщина", callback_data="evg_paid_gender_female")
        ]
    ])
    await ctx.bot.send_message(
        chat_id=user_id,
        text="Пожалуйста, выберите ваш пол для платного курса (Евгений):",
        reply_markup=kb
    )


async def evg_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if "male" in data:
        await query.message.reply_text("В разработке 🚧 (мужская программа платного курса Евгений)")
    else:
        # Женщина
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏋️ В зале", callback_data="evg_paid_program_gym"),
                InlineKeyboardButton("🏠 Дома", callback_data="evg_paid_program_home")
            ]
        ])
        await query.message.reply_text("Выберите программу (платный курс Евгений):", reply_markup=kb)


async def evg_paid_program_gym(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Стартуем день 1 платного курса Евгения (женщина, зал).
    """
    query = update.callback_query
    user_id = query.from_user.id
    user_data_paid_evg[user_id] = {"current_day": 1}

    await evg_show_paid_day(query.message, user_id, day=1)


async def evg_paid_program_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке 🚧 (домашняя программа, платный курс Евгений)")


async def evg_show_paid_day(msg, user_id, day: int):
    """
    Показать упражнения за day (Евгений, платный).
    """
    paid_program = {
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

    ex = paid_program.get(day, ["Нет данных на этот день"])
    text = f"📚 **Платный курс (Евгений): День {day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день! 🎥"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"evg_paid_video_day_{day}")]
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def evg_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Пользователь нажал "Отправить отчет" в платном курсе (Евгений).
    """
    query = update.callback_query
    user_id = query.from_user.id
    paid_day = int(query.data.split("_")[-1])
    user_waiting_for_video_evg[user_id] = ("paid", paid_day)

    await query.message.reply_text(f"Пожалуйста, отправьте видео-отчет за платный день {paid_day} (Евгений) 🎥")


async def evg_paid_next_day_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Пользователь нажал "➡️ Следующий день" в платном курсе (Евгений).
    """
    query = update.callback_query
    user_id = query.from_user.id
    current_day = user_data_paid_evg[user_id].get("current_day", 1)

    if current_day < 5:
        next_day = current_day + 1
        user_data_paid_evg[user_id]["current_day"] = next_day
        await evg_show_paid_day(query.message, user_id, next_day)
    else:
        await query.message.reply_text(
            "Поздравляем! Вы завершили платный курс (Евгений)! 🎉",
            reply_markup=main_menu_evg()
        )
        user_data_paid_evg[user_id].pop("current_day", None)


# --------------------------------------------------------------------------------------
#                  МЕНЮ "МОЙ КАБИНЕТ" / "ОБО МНЕ" / "КАК ЗАРАБОТАТЬ" / "КАК ПОТРАТИТЬ"
#                                 (Евгений)
# --------------------------------------------------------------------------------------
async def evg_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    status = user_status_evg.get(user_id, statuses[0])
    text = (f"👤 Ваш кабинет (Евгений):\n\n"
            f"Статус: {status}\n"
            f"Баллы: {score}\n"
            f"Продолжайте тренироваться, чтобы улучшить статус и заработать больше баллов! 💪")

    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
            caption=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Мой кабинет' (Евгений): {e}")
        await query.message.reply_text(text)


async def evg_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("👤 О тренере (Евгений):\n\n"
            "Курочкин Евгений Витальевич\n"
            "Общий тренировочный стаж - 20 лет\n"
            "Стаж работы - 15 лет\n"
            "МС - по становой тяге\n"
            "МС - по жиму штанги лежа\n"
            "Судья - федеральной категории\n"
            "Организатор соревнований\n"
            "КМС - по бодибилдингу\n\n"
            "20 лет в фитнесе! 💥")

    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
            caption=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Обо мне' (Евгений): {e}")
        await query.message.reply_text(text)


async def evg_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("💡 Как заработать баллы (Евгений):\n\n"
            "1️⃣ Проходите бесплатный курс и отправляйте видео-отчеты.\n"
            "2️⃣ Участвуйте в челленджах и отправляйте видео-отчеты.\n"
            "3️⃣ Приглашайте друзей и получайте баллы за их активность.\n"
            "4️⃣ Покупайте платный курс и получаете дополнительные баллы.")

    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
            caption=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как заработать баллы' (Евгений): {e}")
        await query.message.reply_text(text)


async def evg_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_evg.get(user_id, 0)
    text = (f"💰 Как потратить баллы (Евгений):\n\n"
            f"У вас есть {score} баллов.\n\n"
            "Вы можете потратить баллы на:\n"
            "- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
            "- Максимальная скидка - 600 рублей.\n"
            "- Другие привилегии!")

    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
            caption=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как потратить баллы' (Евгений): {e}")
        await query.message.reply_text(text)


async def evg_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await ctx.bot.get_me()
    link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(
        f"🔗 Ваша реферальная ссылка (Евгений):\n{link}\n\n"
        f"Поделитесь ею с друзьями и получите 100 баллов! 🎉"
    )


async def evg_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню (Евгений)", reply_markup=main_menu_evg())


# --------------------------------------------------------------------------------------
#                       РАСЧЁТ КБЖУ (Евгений) - ConversationHandler
# --------------------------------------------------------------------------------------
async def evg_kbju_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Начинаем диалог сбора данных для КБЖУ (Евгений).
    """
    query = update.callback_query
    await query.message.reply_text(
        "Для расчёта КБЖУ, укажите ваш пол (M / Ж):",
        reply_markup=ReplyKeyboardRemove()
    )
    return EVG_KBJU_GENDER


async def evg_kbju_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text.strip().lower()
    ctx.user_data["evg_kbju_gender"] = gender
    await update.message.reply_text("Укажите ваш вес (кг), например 70.5:")
    return EVG_KBJU_WEIGHT


async def evg_kbju_weight(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    weight = update.message.text.strip()
    ctx.user_data["evg_kbju_weight"] = float(weight)
    await update.message.reply_text("Укажите ваш рост (см), например 170:")
    return EVG_KBJU_HEIGHT


async def evg_kbju_height(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    height = update.message.text.strip()
    ctx.user_data["evg_kbju_height"] = float(height)
    await update.message.reply_text("Укажите ваш возраст (целое число), например 30:")
    return EVG_KBJU_AGE


async def evg_kbju_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    age = update.message.text.strip()
    ctx.user_data["evg_kbju_age"] = int(age)

    # Подсказка по активности
    msg = (
        "Выберите ваш уровень активности (число), например:\n"
        "1.2 - минимальная\n"
        "1.375 - лёгкая\n"
        "1.55 - средняя\n"
        "1.7 - высокая\n"
        "1.9 - экстра\n\n"
        "Напишите число:"
    )
    await update.message.reply_text(msg)
    return EVG_KBJU_ACTIVITY


async def evg_kbju_activity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    act = update.message.text.strip()
    ctx.user_data["evg_kbju_activity"] = float(act)

    # Цель
    msg = "Какая у вас цель? Напишите одно из: похудеть / набрать / поддержание"
    await update.message.reply_text(msg)
    return EVG_KBJU_GOAL


async def evg_kbju_goal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.strip().lower()
    ctx.user_data["evg_kbju_goal"] = goal

    # Теперь считаем
    gender = ctx.user_data["evg_kbju_gender"]
    weight = ctx.user_data["evg_kbju_weight"]
    height = ctx.user_data["evg_kbju_height"]
    age = ctx.user_data["evg_kbju_age"]
    act = ctx.user_data["evg_kbju_activity"]

    cal = calculate_kbju(gender, weight, height, age, act, goal)
    await update.message.reply_text(
        f"Ваш суточный калораж примерно: {cal} ккал.\n"
        f"Это примерный расчёт, корректируйте по ощущениям."
    )
    return ConversationHandler.END


async def evg_kbju_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Расчёт КБЖУ отменён (Евгений).", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# --------------------------------------------------------------------------------------
#                       АНАЛОГИЧНАЯ ЛОГИКА ДЛЯ АНАСТАСИИ
# --------------------------------------------------------------------------------------

# ----------- БЕСПЛАТНЫЙ КУРС (Анастасия) -----------
async def ana_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    user_info = user_data_free_ana.get(user_id, {})
    if "gender" not in user_info or "program" not in user_info:
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨 Мужчина", callback_data="ana_free_gender_male"),
                InlineKeyboardButton("👩 Женщина", callback_data="ana_free_gender_female")
            ]
        ])
        await query.message.reply_text("Ваш пол (бесплатный курс Анастасия):", reply_markup=kb)
    else:
        await start_free_course_ana(query.message, ctx, user_id)


async def handle_ana_free_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
    await query.message.reply_text("Выберите программу (бесплатный курс Анастасия):", reply_markup=kb)


async def handle_ana_free_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    program = "home" if "home" in query.data else "gym"

    if user_id not in user_data_free_ana:
        user_data_free_ana[user_id] = {}

    user_data_free_ana[user_id]["program"] = program
    user_data_free_ana[user_id]["current_day"] = 1

    await start_free_course_ana(query.message, ctx, user_id)


async def start_free_course_ana(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    """
    Аналогично Евгению. 
    Скопирована логика из Евгения, но храним всё в словарях Анастасии.
    """
    user_info = user_data_free_ana.get(user_id, {})
    # Если логика бесплатного курса Анастасии такая же (female/home), то делаем проверку
    if not (user_info.get("gender") == "female" and user_info.get("program") == "home"):
        await msg.reply_text("Пока в разработке (бесплатный курс Анастасия) 🚧", reply_markup=main_menu_ana())
        return

    day = user_info.get("current_day", 1)
    if day > 5:
        await msg.reply_text("Вы завершили курс (Анастасия)! 🎉", reply_markup=main_menu_ana())
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
            "1️⃣ Присед с махом 3x20",
            "2️⃣ Ягодичный мост 3x30",
            "3️⃣ Велосипед 3x15"
        ],
        2: [
            "1️⃣ Отжимания от пола 3x15",
            "2️⃣ Лодочка прямые руки 3x30",
            "3️⃣ Полные подъёмы корпуса 3x20"
        ],
        3: [
            "1️⃣ Выпады назад 3x15",
            "2️⃣ Махи в бок с колен 3x20",
            "3️⃣ Косые с касанием пяток 3x15"
        ],
        4: [
            "1️⃣ Поочередные подъемы с гантелями 4x20",
            "2️⃣ Узкие отжимания 3x15",
            "3️⃣ Планка 3x1 мин"
        ],
        5: [
            "1️⃣ Присед со штангой (без штанги) 3x20",
            "2️⃣ Махи под 45 с резинкой 3x20",
            "3️⃣ Подъёмы ног лёжа 3x15"
        ],
    }

    text = f"🔥 **Бесплатный курс (Анастасия): День {day}** 🔥\n\n" + "\n".join(course[day]) + "\n\nОтправьте видео-отчет за день! 🎥"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"ana_free_send_report_day_{day}")]
    ])

    try:
        await ctx.bot.send_photo(
            chat_id=msg.chat_id,
            photo=photos[day],
            caption=text,
            parse_mode="Markdown",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото (Анастасия free day {day}): {e}")
        await msg.reply_text(
            "Ошибка: изображение не найдено. Продолжайте без фото.\n\n" + text,
            parse_mode="Markdown",
            reply_markup=kb
        )


async def ana_free_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])  # ana_free_send_report_day_X

    if user_reports_sent_ana.get(user_id, {}).get(day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {day} (Анастасия).")
        return

    user_waiting_for_video_ana[user_id] = ("free", day)
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день (Анастасия) 🎥")


async def ana_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in user_waiting_for_video_ana:
        return  # Игнорируем, если не ждем

    data = user_waiting_for_video_ana[user_id]
    course_type = data[0]

    if course_type == "free":
        day = data[1]
        await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Видео-отчет (бесплатный курс Анастасия) от {user_name} (ID: {user_id}) за день {day}.")
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

        user_scores_ana[user_id] = user_scores_ana.get(user_id, 0) + 60

        if user_id not in user_reports_sent_ana:
            user_reports_sent_ana[user_id] = {}
        user_reports_sent_ana[user_id][day] = True

        current_day = user_data_free_ana[user_id]["current_day"]
        if current_day < 5:
            user_data_free_ana[user_id]["current_day"] = current_day + 1
            new_day = user_data_free_ana[user_id]["current_day"]
            await update.message.reply_text(
                f"Отчет за день {day} (Анастасия) принят! 🎉\n"
                f"Ваши баллы: {user_scores_ana[user_id]}.\n"
                f"Готовы к следующему дню ({new_day})? ➡️",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {new_day}", callback_data="ana_free_next_day")]
                ])
            )
        else:
            user_status_ana[user_id] = statuses[1]
            await update.message.reply_text(
                f"Поздравляем! Вы завершили бесплатный курс (Анастасия)! 🎉\n"
                f"Ваши баллы: {user_scores_ana[user_id]}.",
                reply_markup=main_menu_ana()
            )

        del user_waiting_for_video_ana[user_id]

    elif course_type == "paid":
        paid_day = data[1]
        await ctx.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Платный видео-отчет (Анастасия) от {user_name} (ID: {user_id}) за день {paid_day}."
        )
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

        user_scores_ana[user_id] = user_scores_ana.get(user_id, 0) + 30
        del user_waiting_for_video_ana[user_id]

        current_day = user_data_paid_ana[user_id].get("current_day", 1)
        if current_day < 5:
            await update.message.reply_text(
                f"Отчет за платный день {paid_day} (Анастасия) принят! 🎉\n"
                f"Ваши баллы: {user_scores_ana[user_id]}.\n"
                f"Готовы к следующему дню ({current_day + 1})? ➡️",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➡️ Следующий день", callback_data="ana_paid_next_day")]
                ])
            )
        else:
            await update.message.reply_text(
                f"Поздравляем! Вы завершили платный курс (Анастасия)! 🎉\nВаши баллы: {user_scores_ana[user_id]}.",
                reply_markup=main_menu_ana()
            )
            user_data_paid_ana[user_id].pop("current_day", None)

    else:
        await update.message.reply_text("Ошибка: неизвестный формат данных (Анастасия).")


async def ana_free_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await start_free_course_ana(query.message, ctx, user_id)


# ----------- ЧЕЛЛЕНДЖ (Анастасия) -----------
async def ana_challenge_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_ana.get(user_id, 0)

    if user_id in user_challenges_ana:
        await send_challenge_task_ana(query.message, user_id)
    else:
        if score >= 300:
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💰 Купить доступ за 300 баллов", callback_data="ana_buy_challenge"),
                    InlineKeyboardButton("🔙 Назад", callback_data="ana_back")
                ]
            ])
            await query.message.reply_text("Доступ к челленджам (Анастасия) стоит 300 баллов. Хотите приобрести?", reply_markup=kb)
        else:
            await query.message.reply_text(
                f"⚠️ Для доступа к челленджам (Анастасия) нужно 300 баллов.\n"
                f"У вас: {score} баллов.\nПродолжайте тренировки!"
            )


async def ana_buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_ana.get(user_id, 0)
    if score >= 300:
        user_scores_ana[user_id] = score - 300
        user_challenges_ana[user_id] = {"current_day": 1}
        await query.message.reply_text("✅ Доступ к челленджам (Анастасия) открыт!", reply_markup=main_menu_ana())
        await send_challenge_task_ana(query.message, user_id)
    else:
        await query.message.reply_text("⚠️ Недостаточно баллов для покупки доступа к челленджу (Анастасия)!")


async def send_challenge_task_ana(message, user_id: int):
    day = user_challenges_ana[user_id]["current_day"]
    exercises_by_day = {
        1: [
            "1️⃣ Выпады назад 40 раз",
            "2️⃣ Лодочка + сгибание в локтях 50 раз",
            "3️⃣ Велосипед 30 на каждую ногу"
        ],
        2: [
            "1️⃣ Присед со штангой 30 раз",
            "2️⃣ Отжимания с отрывом рук 25 раз",
            "3️⃣ Полные подъёмы корпуса 30 раз"
        ],
        3: [
            "1️⃣ Планка 3 мин",
            "2️⃣ Подъёмы ног лёжа 3x15"
        ],
        4: [
            "1️⃣ Выпады назад 60 раз",
            "2️⃣ Лодочка + сгибание в локтях 50 раз",
            "3️⃣ Велосипед 50 на каждую ногу"
        ],
        5: [
            "1️⃣ Присед со штангой 50 раз",
            "2️⃣ Отжимания с отрывом рук 40 раз",
            "3️⃣ Полные подъёмы корпуса 50 раз"
        ],
    }
    exercises = exercises_by_day.get(day, [])
    text = f"💪 **Челлендж (Анастасия): День {day}** 💪\n\n" + "\n".join(exercises)

    if day < 5:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Следующий день", callback_data="ana_challenge_next")]
        ])
    else:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="ana_back")]
        ])

    await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def ana_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in user_challenges_ana:
        await query.answer("Сначала купите челлендж (Анастасия)! 🚧")
        return

    day = user_challenges_ana[user_id]["current_day"]
    if day < 5:
        user_challenges_ana[user_id]["current_day"] = day + 1
        await send_challenge_task_ana(query.message, user_id)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж (Анастасия)! 🎉", reply_markup=main_menu_ana())
        del user_challenges_ana[user_id]


# ----------- ПЛАТНЫЙ КУРС (Анастасия) -----------
async def ana_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_ana.get(user_id, 0)
    discount = min(score * 2, 600)
    price = 2000 - discount

    user_waiting_for_receipt_ana[user_id] = True

    await query.message.reply_text(
        f"📚 **Платный курс (Анастасия)** 📚\n\n"
        f"Стоимость курса: 2000 руб. 💵\n"
        f"Ваша скидка: {discount} руб. 🔖\n"
        f"Итоговая сумма: {price} руб. 💳\n\n"
        f"💳 Переведите сумму на карту: 89236950304 (Яндекс Банк) 🏦\n"
        f"После оплаты отправьте чек для проверки.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧾 Отправить чек", callback_data="ana_send_receipt")]])
    )


async def ana_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt_ana[user_id] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате (Анастасия) 📸.")


async def ana_handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id not in user_waiting_for_receipt_ana:
        return

    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фото чека (Анастасия) 📸.")
        return

    photo_id = update.message.photo[-1].file_id
    await ctx.bot.send_message(chat_id=GROUP_ID, text=f"🧾 Чек (Анастасия) от {user_name} (ID: {user_id}). Подтвердите оплату.")
    await ctx.bot.send_photo(
        chat_id=GROUP_ID,
        photo=photo_id,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Подтвердить", callback_data=f"ana_confirm_payment_{user_id}")]
        ])
    )
    await update.message.reply_text("Чек отправлен на проверку (Анастасия). Ожидайте подтверждения ⏳.")


async def ana_confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = int(data.split("_")[-1])

    user_status_ana[user_id] = statuses[2]
    if user_id in user_waiting_for_receipt_ana:
        del user_waiting_for_receipt_ana[user_id]

    await ctx.bot.send_message(
        chat_id=user_id,
        text="✅ Оплата подтверждена! (Анастасия)\nВам открыт доступ к платному курсу. 🎉"
    )

    # Аналогично, спрашиваем пол
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👨 Мужчина", callback_data="ana_paid_gender_male"),
            InlineKeyboardButton("👩 Женщина", callback_data="ana_paid_gender_female")
        ]
    ])
    await ctx.bot.send_message(
        chat_id=user_id,
        text="Пожалуйста, выберите ваш пол для платного курса (Анастасия):",
        reply_markup=kb
    )


async def ana_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if "male" in data:
        await query.message.reply_text("В разработке 🚧 (мужская программа платного курса Анастасия)")
    else:
        # Женщина
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏋️ В зале", callback_data="ana_paid_program_gym"),
                InlineKeyboardButton("🏠 Дома", callback_data="ana_paid_program_home")
            ]
        ])
        await query.message.reply_text("Выберите программу (платный курс Анастасия):", reply_markup=kb)


async def ana_paid_program_gym(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_data_paid_ana[user_id] = {"current_day": 1}

    await ana_show_paid_day(query.message, user_id, day=1)


async def ana_paid_program_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке 🚧 (домашняя программа, платный курс Анастасия)")


async def ana_show_paid_day(msg, user_id, day: int):
    paid_program = {
        1: [
            "Махи назад с утяжелителями 3х25+5",
            "Выпады 3х30 шагов х 2кг",
            "Разведение ног 3х20",
            "Сведение ног 3х20",
            "Сгибание ног 3х15",
        ],
        2: [
            "Косые скручивания 3х30+10",
            "Отжимания от пола 3х15+5",
            "Лодочка с локтями 3х20+5",
            "Жим гантелей 3х15+5",
            "Гантели в развороте 3х15+5",
            "Разгибание с веревкой 3х1+5",
        ],
        3: [
            "Подъёмы ног 3х15+5",
            "Разгибание ног 3х15+5",
            "Выпады назад 3х15",
            "Ягодичный мост 3х20+5",
            "Двойные разведения ног 3х20+5",
            "Мертвая тяга с гантелями 3х15+5",
        ],
        4: [
            "Скручивания 3х20+10",
            "Отжимания в ТРХ ремнях 3х15+5",
            "Подтягивания в ТРХ ремнях 3х15",
            "Разводка с гантелями 35 3х15+5",
            "Тяга блока к груди широким хватом 3х12",
            "Жим гантелей сидя 3х12",
            "Скручивания на скамье 3х20",
        ],
        5: [
            "Вместо дня 5 оставим пример или финальную программу 🏆",
        ],
    }
    ex = paid_program.get(day, ["Нет данных на этот день"])
    text = f"📚 **Платный курс (Анастасия): День {day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день! 🎥"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"ana_paid_video_day_{day}")]
    ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def ana_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    paid_day = int(query.data.split("_")[-1])
    user_waiting_for_video_ana[user_id] = ("paid", paid_day)

    await query.message.reply_text(f"Пожалуйста, отправьте видео-отчет за платный день {paid_day} (Анастасия) 🎥")


async def ana_paid_next_day_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    current_day = user_data_paid_ana[user_id].get("current_day", 1)

    if current_day < 5:
        next_day = current_day + 1
        user_data_paid_ana[user_id]["current_day"] = next_day
        await ana_show_paid_day(query.message, user_id, next_day)
    else:
        await query.message.reply_text(
            "Поздравляем! Вы завершили платный курс (Анастасия)! 🎉",
            reply_markup=main_menu_ana()
        )
        user_data_paid_ana[user_id].pop("current_day", None)


# ----------- Мой кабинет / обо мне / как заработать / как потратить (Анастасия) -----------
async def ana_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_ana.get(user_id, 0)
    status = user_status_ana.get(user_id, statuses[0])
    text = (f"👤 Ваш кабинет (Анастасия):\n\n"
            f"Статус: {status}\n"
            f"Баллы: {score}\n"
            f"Продолжайте тренироваться, чтобы улучшить статус и заработать больше баллов! 💪")

    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
            caption=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Мой кабинет' (Анастасия): {e}")
        await query.message.reply_text(text)


async def ana_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("👤 О тренере (Анастасия):\n\n"
            "Пример био Анастасии...\n"
            "Стаж, регалии и т.д.\n\n"
            "15 лет в фитнесе! 💥 (пример)")

    await query.message.reply_text(text)


async def ana_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("💡 Как заработать баллы (Анастасия):\n\n"
            "1️⃣ Проходите бесплатный курс и отправляйте видео-отчеты.\n"
            "2️⃣ Участвуйте в челленджах и отправляйте видео-отчеты.\n"
            "3️⃣ Приглашайте друзей и получайте баллы за их активность.\n"
            "4️⃣ Покупайте платный курс и получаете дополнительные баллы.")

    await query.message.reply_text(text)


async def ana_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores_ana.get(user_id, 0)
    text = (f"💰 Как потратить баллы (Анастасия):\n\n"
            f"У вас есть {score} баллов.\n\n"
            "Вы можете потратить баллы на:\n"
            "- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
            "- Максимальная скидка - 600 рублей.\n"
            "- Другие привилегии!")

    await query.message.reply_text(text)


async def ana_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await ctx.bot.get_me()
    link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(
        f"🔗 Ваша реферальная ссылка (Анастасия):\n{link}\n\n"
        f"Поделитесь ею с друзьями и получите 100 баллов! 🎉"
    )


async def ana_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню (Анастасия)", reply_markup=main_menu_ana())


# ----------- РАСЧЁТ КБЖУ (Анастасия) -----------
async def ana_kbju_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Для расчёта КБЖУ (Анастасия), введите ваш пол (M / Ж):")
    return ANA_KBJU_GENDER


async def ana_kbju_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text.strip().lower()
    ctx.user_data["ana_kbju_gender"] = gender
    await update.message.reply_text("Укажите ваш вес (кг), например 70.5:")
    return ANA_KBJU_WEIGHT


async def ana_kbju_weight(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    weight = update.message.text.strip()
    ctx.user_data["ana_kbju_weight"] = float(weight)
    await update.message.reply_text("Укажите ваш рост (см), например 170:")
    return ANA_KBJU_HEIGHT


async def ana_kbju_height(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    height = update.message.text.strip()
    ctx.user_data["ana_kbju_height"] = float(height)
    await update.message.reply_text("Укажите ваш возраст (целое число), например 30:")
    return ANA_KBJU_AGE


async def ana_kbju_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    age = update.message.text.strip()
    ctx.user_data["ana_kbju_age"] = int(age)

    msg = (
        "Выберите ваш уровень активности (число), например:\n"
        "1.2 - минимальная\n"
        "1.375 - лёгкая\n"
        "1.55 - средняя\n"
        "1.7 - высокая\n"
        "1.9 - экстра\n\n"
        "Напишите число:"
    )
    await update.message.reply_text(msg)
    return ANA_KBJU_ACTIVITY


async def ana_kbju_activity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    act = update.message.text.strip()
    ctx.user_data["ana_kbju_activity"] = float(act)

    msg = "Какая у вас цель? Напишите одно из: похудеть / набрать / поддержание"
    await update.message.reply_text(msg)
    return ANA_KBJU_GOAL


async def ana_kbju_goal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text.strip().lower()
    ctx.user_data["ana_kbju_goal"] = goal

    gender = ctx.user_data["ana_kbju_gender"]
    weight = ctx.user_data["ana_kbju_weight"]
    height = ctx.user_data["ana_kbju_height"]
    age = ctx.user_data["ana_kbju_age"]
    act = ctx.user_data["ana_kbju_activity"]

    cal = calculate_kbju(gender, weight, height, age, act, goal)
    await update.message.reply_text(
        f"Ваш суточный калораж (Анастасия) примерно: {cal} ккал.\n"
        f"Это примерный расчёт, корректируйте по ощущениям."
    )
    return ConversationHandler.END


async def ana_kbju_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Расчёт КБЖУ отменён (Анастасия).", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# --------------------------------------------------------------------------------------
#                                MAIN
# --------------------------------------------------------------------------------------
def main():
    app = Application.builder().token(TOKEN).build()

    # ---------- ConversationHandler для КБЖУ (Евгений) ----------
    evg_kbju_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(evg_kbju_start, pattern="^evg_kbju$")],
        states={
            EVG_KBJU_GENDER: [MessageHandler(filters.TEXT, evg_kbju_gender)],
            EVG_KBJU_WEIGHT: [MessageHandler(filters.TEXT, evg_kbju_weight)],
            EVG_KBJU_HEIGHT: [MessageHandler(filters.TEXT, evg_kbju_height)],
            EVG_KBJU_AGE: [MessageHandler(filters.TEXT, evg_kbju_age)],
            EVG_KBJU_ACTIVITY: [MessageHandler(filters.TEXT, evg_kbju_activity)],
            EVG_KBJU_GOAL: [MessageHandler(filters.TEXT, evg_kbju_goal)],
        },
        fallbacks=[CommandHandler("cancel", evg_kbju_cancel)]
    )

    # ---------- ConversationHandler для КБЖУ (Анастасия) ----------
    ana_kbju_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ana_kbju_start, pattern="^ana_kbju$")],
        states={
            ANA_KBJU_GENDER: [MessageHandler(filters.TEXT, ana_kbju_gender)],
            ANA_KBJU_WEIGHT: [MessageHandler(filters.TEXT, ana_kbju_weight)],
            ANA_KBJU_HEIGHT: [MessageHandler(filters.TEXT, ana_kbju_height)],
            ANA_KBJU_AGE: [MessageHandler(filters.TEXT, ana_kbju_age)],
            ANA_KBJU_ACTIVITY: [MessageHandler(filters.TEXT, ana_kbju_activity)],
            ANA_KBJU_GOAL: [MessageHandler(filters.TEXT, ana_kbju_goal)],
        },
        fallbacks=[CommandHandler("cancel", ana_kbju_cancel)]
    )

    # -------------------------- Команда /start --------------------------
    app.add_handler(CommandHandler("start", start))

    # -------------------------- Обработка выбора тренера ----------------
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))

    # -------------------------- Возврат к старту ------------------------
    app.add_handler(CallbackQueryHandler(handle_back_to_start, pattern="^back_to_start$"))

    # -------------------------- Евгений: Бесплатный курс ----------------
    app.add_handler(CallbackQueryHandler(evg_free_course, pattern="^evg_free_course$"))
    app.add_handler(CallbackQueryHandler(handle_evg_free_gender, pattern="^evg_free_gender_"))
    app.add_handler(CallbackQueryHandler(handle_evg_free_program, pattern="^evg_free_program_"))
    app.add_handler(CallbackQueryHandler(evg_free_next_day, pattern="^evg_free_next_day$"))
    app.add_handler(CallbackQueryHandler(evg_free_send_report, pattern=r"^evg_free_send_report_day_\d+$"))

    # -------------------------- Евгений: Видео ----------------
    #   Ловим все видео в чате
    app.add_handler(MessageHandler(filters.VIDEO, evg_handle_video))

    # -------------------------- Евгений: Челлендж ----------------
    app.add_handler(CallbackQueryHandler(evg_challenge_menu, pattern="^evg_challenge_menu$"))
    app.add_handler(CallbackQueryHandler(evg_buy_challenge, pattern="^evg_buy_challenge$"))
    app.add_handler(CallbackQueryHandler(evg_challenge_next_day, pattern="^evg_challenge_next$"))

    # -------------------------- Евгений: Платный курс ----------------
    app.add_handler(CallbackQueryHandler(evg_paid_course, pattern="^evg_paid_course$"))
    app.add_handler(CallbackQueryHandler(evg_send_receipt, pattern="^evg_send_receipt$"))
    app.add_handler(CallbackQueryHandler(evg_confirm_payment, pattern="^evg_confirm_payment_\d+$"))
    #   Выбор пола
    app.add_handler(CallbackQueryHandler(evg_paid_gender, pattern="^evg_paid_gender_"))
    #   Программа
    app.add_handler(CallbackQueryHandler(evg_paid_program_gym, pattern="^evg_paid_program_gym$"))
    app.add_handler(CallbackQueryHandler(evg_paid_program_home, pattern="^evg_paid_program_home$"))
    #   Дни
    app.add_handler(CallbackQueryHandler(evg_send_paid_report, pattern=r"^evg_paid_video_day_\d+$"))
    app.add_handler(CallbackQueryHandler(evg_paid_next_day_handler, pattern="^evg_paid_next_day$"))

    # -------------------------- Евгений: Фото чека ----------------
    app.add_handler(MessageHandler(filters.PHOTO, evg_handle_receipt))

    # -------------------------- Евгений: Остальные кнопки ----------------
    app.add_handler(CallbackQueryHandler(evg_my_cabinet, pattern="^evg_my_cabinet$"))
    app.add_handler(CallbackQueryHandler(evg_about_me, pattern="^evg_about_me$"))
    app.add_handler(CallbackQueryHandler(evg_earn_points, pattern="^evg_earn_points$"))
    app.add_handler(CallbackQueryHandler(evg_spend_points, pattern="^evg_spend_points$"))
    app.add_handler(CallbackQueryHandler(evg_referral, pattern="^evg_referral$"))
    app.add_handler(CallbackQueryHandler(evg_back, pattern="^evg_back$"))

    # -------------------------- Евгений: КБЖУ (ConversationHandler) -------
    app.add_handler(evg_kbju_conv)

    # -------------------------- Анастасия: Бесплатный курс ----------------
    app.add_handler(CallbackQueryHandler(ana_free_course, pattern="^ana_free_course$"))
    app.add_handler(CallbackQueryHandler(handle_ana_free_gender, pattern="^ana_free_gender_"))
    app.add_handler(CallbackQueryHandler(handle_ana_free_program, pattern="^ana_free_program_"))
    app.add_handler(CallbackQueryHandler(ana_free_next_day, pattern="^ana_free_next_day$"))
    app.add_handler(CallbackQueryHandler(ana_free_send_report, pattern=r"^ana_free_send_report_day_\d+$"))

    # -------------------------- Анастасия: Видео ----------------
    app.add_handler(MessageHandler(filters.VIDEO, ana_handle_video))

    # -------------------------- Анастасия: Челлендж ----------------
    app.add_handler(CallbackQueryHandler(ana_challenge_menu, pattern="^ana_challenge_menu$"))
    app.add_handler(CallbackQueryHandler(ana_buy_challenge, pattern="^ana_buy_challenge$"))
    app.add_handler(CallbackQueryHandler(ana_challenge_next_day, pattern="^ana_challenge_next$"))

    # -------------------------- Анастасия: Платный курс ----------------
    app.add_handler(CallbackQueryHandler(ana_paid_course, pattern="^ana_paid_course$"))
    app.add_handler(CallbackQueryHandler(ana_send_receipt, pattern="^ana_send_receipt$"))
    app.add_handler(CallbackQueryHandler(ana_confirm_payment, pattern="^ana_confirm_payment_\d+$"))
    #   Выбор пола
    app.add_handler(CallbackQueryHandler(ana_paid_gender, pattern="^ana_paid_gender_"))
    #   Программа
    app.add_handler(CallbackQueryHandler(ana_paid_program_gym, pattern="^ana_paid_program_gym$"))
    app.add_handler(CallbackQueryHandler(ana_paid_program_home, pattern="^ana_paid_program_home$"))
    #   Дни
    app.add_handler(CallbackQueryHandler(ana_send_paid_report, pattern=r"^ana_paid_video_day_\d+$"))
    app.add_handler(CallbackQueryHandler(ana_paid_next_day_handler, pattern="^ana_paid_next_day$"))

    # -------------------------- Анастасия: Фото чека ----------------
    app.add_handler(MessageHandler(filters.PHOTO, ana_handle_receipt))

    # -------------------------- Анастасия: Остальные кнопки ----------------
    app.add_handler(CallbackQueryHandler(ana_my_cabinet, pattern="^ana_my_cabinet$"))
    app.add_handler(CallbackQueryHandler(ana_about_me, pattern="^ana_about_me$"))
    app.add_handler(CallbackQueryHandler(ana_earn_points, pattern="^ana_earn_points$"))
    app.add_handler(CallbackQueryHandler(ana_spend_points, pattern="^ana_spend_points$"))
    app.add_handler(CallbackQueryHandler(ana_referral, pattern="^ana_referral$"))
    app.add_handler(CallbackQueryHandler(ana_back, pattern="^ana_back$"))

    # -------------------------- Анастасия: КБЖУ (ConversationHandler) ------
    app.add_handler(ana_kbju_conv)

    # -------------------------- Запуск бота -------------------------------
    print("Бот запущен и готов к работе. 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
