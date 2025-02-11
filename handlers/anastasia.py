import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import ContextTypes, CallbackContext

logger = logging.getLogger(__name__)

# Глобальные словари
anastasia_user_scores = {}
anastasia_user_status = {}
anastasia_user_reports_sent = {}
anastasia_user_waiting_for_video = {}
anastasia_user_challenges = {}
anastasia_user_waiting_for_receipt = {}

# Статусы
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Пример group_id - можно импортировать из bot.py или из .env
# Но здесь оставим заглушку
GROUP_ID = os.getenv("GROUP_ID")  # Если хотите, импортируйте os.getenv("GROUP_ID")

###########################
# Вспомогательные функции
###########################
def get_instructor(user_id: int, ctx: ContextTypes.DEFAULT_TYPE) -> str:
    """Какой тренер выбран?"""
    return ctx.user_data.get(user_id, {}).get("instructor", "anastasia")

def get_score(user_id: int) -> int:
    return anastasia_user_scores.get(user_id, 0)

def add_score(user_id: int, amount: int) -> None:
    anastasia_user_scores[user_id] = anastasia_user_scores.get(user_id, 0) + amount

def get_status(user_id: int) -> str:
    return anastasia_user_status.get(user_id, statuses[0])

def set_status(user_id: int, new_status: str) -> None:
    anastasia_user_status[user_id] = new_status

def anastasia_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔥 Пройти бесплатный курс (АНАСТАСИЯ)", callback_data="anastasia_free_course")],
        [InlineKeyboardButton("💪 Челлендж (АНАСТАСИЯ)", callback_data="anastasia_challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс (АНАСТАСИЯ)", callback_data="anastasia_paid_course")],
        [InlineKeyboardButton("👤 Мой кабинет (АНАСТАСИЯ)", callback_data="anastasia_my_cabinet")],
        [InlineKeyboardButton("💰 Как потратить баллы (АНАСТАСИЯ)", callback_data="anastasia_spend_points")],
        [InlineKeyboardButton("🍽 КБЖУ (АНАСТАСИЯ)", callback_data="anastasia_kbju")],
        [InlineKeyboardButton("🔙 Вернуться к выбору тренера", callback_data="choose_instructor_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

###########################
#       БЕСПЛАТНЫЙ КУРС
###########################
async def anastasia_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Текущее значение дня, если нет - ставим 1
    if "anastasia_free_day" not in ctx.user_data[user_id]:
        ctx.user_data[user_id]["anastasia_free_day"] = 1
    day = ctx.user_data[user_id]["anastasia_free_day"]
    if day > 5:
        await query.message.reply_text(
            "Вы уже прошли бесплатный курс Анастасии!",
            reply_markup=anastasia_main_menu()
        )
        return

    # Пример упражнений
    exercises = {
        1: ["Упражнение 1 (день 1)", "Упражнение 2 (день 1)"],
        2: ["Упражнение 1 (день 2)", "Упражнение 2 (день 2)"],
        3: ["Упражнение 1 (день 3)", "Упражнение 2 (день 3)"],
        4: ["Упражнение 1 (день 4)", "Упражнение 2 (день 4)"],
        5: ["Упражнение 1 (день 5)", "Упражнение 2 (день 5)"],
    }
    text = f"Бесплатный курс Анастасии, день {day}:\n\n" + "\n".join(exercises[day])
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Отправить видео-отчет (День {day})", callback_data=f"anastasia_send_report_{day}")]
    ])
    await query.message.reply_text(text, reply_markup=kb)

async def anastasia_send_report_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data  # anastasia_send_report_3
    day = int(data.split("_")[-1])

    # Проверим, не отправлял ли уже
    if anastasia_user_reports_sent.get(user_id, {}).get(day):
        await query.message.reply_text("Вы уже отправляли отчет за этот день!")
        return

    anastasia_user_waiting_for_video[user_id] = day
    await query.message.reply_text(f"Пришлите видео-отчет за день {day} (Анастасия).")

async def anastasia_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Ловим видео. Если бот ждет от пользователя видео (бесплатный курс / платный), обрабатываем.
    """
    user_id = update.message.from_user.id
    if user_id in anastasia_user_waiting_for_video:
        data = anastasia_user_waiting_for_video[user_id]
        if isinstance(data, int):
            # Бесплатный курс
            day = data
            # Отправляем в группу
            user_name = update.message.from_user.first_name
            if GROUP_ID:
                await ctx.bot.send_message(chat_id=GROUP_ID,
                    text=f"Видео-отчет от {user_name} (ID: {user_id}), день {day} (Анастасия)."
                )
                await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

            # Сохраняем, что отчет отправлен
            anastasia_user_reports_sent.setdefault(user_id, {})[day] = True
            add_score(user_id, 60)
            del anastasia_user_waiting_for_video[user_id]

            # Следующий день
            if "anastasia_free_day" not in ctx.user_data[user_id]:
                ctx.user_data[user_id]["anastasia_free_day"] = day
            ctx.user_data[user_id]["anastasia_free_day"] += 1
            if ctx.user_data[user_id]["anastasia_free_day"] <= 5:
                await update.message.reply_text(
                    f"Отчет за день {day} принят! Ваши баллы: {get_score(user_id)}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Следующий день", callback_data="anastasia_free_course")]
                    ])
                )
            else:
                set_status(user_id, statuses[1])  # «Бывалый»
                await update.message.reply_text(
                    f"Поздравляем! Вы завершили бесплатный курс Анастасии!\nБаллы: {get_score(user_id)}",
                    reply_markup=anastasia_main_menu()
                )
        elif isinstance(data, tuple) and data[0] == "paid":
            # Платный курс
            paid_day = data[1]
            user_name = update.message.from_user.first_name
            if GROUP_ID:
                await ctx.bot.send_message(chat_id=GROUP_ID,
                    text=f"[Платный] Видео-отчет от {user_name} (ID: {user_id}), день {paid_day} (Анастасия)."
                )
                await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

            # Начисляем, удаляем из ожидания
            add_score(user_id, 30)
            del anastasia_user_waiting_for_video[user_id]

            # Переход к след. дню
            if ctx.user_data[user_id].get("anastasia_paid_day", 1) < 5:
                ctx.user_data[user_id]["anastasia_paid_day"] += 1
                await update.message.reply_text(
                    f"Отчет за платный день {paid_day} принят!\nБаллы: {get_score(user_id)}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Следующий день платного курса", callback_data="anastasia_paid_next_day")]
                    ])
                )
            else:
                set_status(user_id, statuses[3])  # «Профи»
                await update.message.reply_text(
                    f"Вы завершили платный курс Анастасии!\nБаллы: {get_score(user_id)}",
                    reply_markup=anastasia_main_menu()
                )
        else:
            await update.message.reply_text("Неизвестный формат данных ожидания (Анастасия).")
    else:
        # Видео пришло, но мы не ждем
        await update.message.reply_text("Я не жду видео-отчет от вас (Анастасия).")

###########################
#        ЧЕЛЛЕНДЖ
###########################
async def anastasia_challenge_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in anastasia_user_challenges:
        # Проверяем, хватает ли баллов на покупку
        if get_score(user_id) >= 300:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("Купить челлендж (300 баллов)", callback_data="anastasia_buy_challenge")],
                [InlineKeyboardButton("Назад", callback_data="anastasia_back_to_menu")]
            ])
            await query.message.reply_text("Челлендж у Анастасии стоит 300 баллов.", reply_markup=kb)
        else:
            await query.message.reply_text(
                f"У вас всего {get_score(user_id)} баллов, а нужно 300.",
                reply_markup=anastasia_main_menu()
            )
    else:
        # Уже куплен - показываем задания
        await send_challenge_day(query.message, user_id, ctx)

async def anastasia_buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if get_score(user_id) >= 300:
        add_score(user_id, -300)
        anastasia_user_challenges[user_id] = {"current_day": 1}
        await query.message.reply_text("Челлендж куплен! Начинаем день 1", reply_markup=anastasia_main_menu())
        await send_challenge_day(query.message, user_id, ctx)
    else:
        await query.message.reply_text("Недостаточно баллов.")

async def send_challenge_day(msg: Message, user_id: int, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    day = anastasia_user_challenges[user_id]["current_day"]
    tasks = {
        1: ["Задание 1 (челл. день 1)", "Задание 2 (челл. день 1)"],
        2: ["Задание 1 (челл. день 2)", "Задание 2 (челл. день 2)"],
        3: ["Задание 1 (челл. день 3)", "Задание 2 (челл. день 3)"],
        4: ["Задание 1 (челл. день 4)", "Задание 2 (челл. день 4)"],
        5: ["Задание 1 (челл. день 5)", "Задание 2 (челл. день 5)"],
    }
    ex = tasks.get(day, ["Нет заданий"])
    text = f"Челлендж Анастасии, день {day}:\n" + "\n".join(ex)
    if day < 5:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Следующий день (челлендж)", callback_data="anastasia_challenge_next")]
        ])
    else:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Меню Анастасии", callback_data="anastasia_back_to_menu")]
        ])
    await msg.reply_text(text, reply_markup=kb)

async def anastasia_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in anastasia_user_challenges:
        await query.message.reply_text("Сначала купите челлендж.")
        return

    current_day = anastasia_user_challenges[user_id]["current_day"]
    if current_day < 5:
        anastasia_user_challenges[user_id]["current_day"] += 1
        await send_challenge_day(query.message, user_id, ctx)
    else:
        await query.message.reply_text("Вы уже завершили челлендж!", reply_markup=anastasia_main_menu())
        del anastasia_user_challenges[user_id]

###########################
#       ПЛАТНЫЙ КУРС
###########################
async def anastasia_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    user_points = get_score(user_id)
    discount = min(user_points * 2, 600)
    price = 2000 - discount

    text = (
        f"Платный курс Анастасии\n\n"
        f"Цена: 2000 руб\n"
        f"Ваша скидка: {discount} руб\n"
        f"Итого к оплате: {price} руб\n\n"
        "Оплатите на карту 9999 9999 9999 9999 и отправьте чек."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить чек (Анастасия)", callback_data="anastasia_send_receipt")]
    ])
    anastasia_user_waiting_for_receipt[user_id] = True
    await query.message.reply_text(text, reply_markup=kb)

async def anastasia_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    anastasia_user_waiting_for_receipt[user_id] = True
    await query.message.reply_text("Пришлите фото чека (Анастасия).")

async def anastasia_handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Если мы не ждем от пользователя чек, выходим
    if not anastasia_user_waiting_for_receipt.get(user_id):
        return

    if not update.message.photo:
        await update.message.reply_text("Это не фото.")
        return

    user_name = update.message.from_user.first_name
    if GROUP_ID:
        await ctx.bot.send_message(GROUP_ID, f"Чек от {user_name} (ID: {user_id}) - [Анастасия]")
        photo_id = update.message.photo[-1].file_id
        await ctx.bot.send_photo(GROUP_ID, photo=photo_id,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Подтвердить оплату (Анастасия)",
                                      callback_data=f"anastasia_confirm_payment_{user_id}")]
            ])
        )
    await update.message.reply_text("Чек отправлен на проверку!")

async def anastasia_confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data  # anastasia_confirm_payment_123456
    user_id = int(data.split("_")[-1])

    # Снимаем флаг ожидания чека
    if user_id in anastasia_user_waiting_for_receipt:
        del anastasia_user_waiting_for_receipt[user_id]

    set_status(user_id, statuses[2])  # «Чемпион»
    await ctx.bot.send_message(user_id, "Оплата подтверждена (Анастасия). Вам открыт доступ к платному курсу.")
    ctx.user_data[user_id]["anastasia_paid_day"] = 1
    await send_paid_day(user_id, 1, ctx)

async def send_paid_day(user_id: int, day: int, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    paid_program = {
        1: ["Задания платного дня 1", "Еще что-то"],
        2: ["Задания платного дня 2"],
        3: ["Задания платного дня 3"],
        4: ["Задания платного дня 4"],
        5: ["Задания платного дня 5"],
    }
    text = f"Платный курс Анастасии: день {day}\n" + "\n".join(paid_program.get(day, []))
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Отправить видео-отчет (день {day})",
                              callback_data=f"anastasia_paid_send_report_{day}")]
    ])
    await ctx.bot.send_message(user_id, text, reply_markup=kb)

async def anastasia_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data  # anastasia_paid_send_report_2
    paid_day = int(data.split("_")[-1])
    anastasia_user_waiting_for_video[user_id] = ("paid", paid_day)
    await query.message.reply_text(f"Пришлите видео-отчет за платный день {paid_day} (Анастасия).")

async def anastasia_paid_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    day = ctx.user_data[user_id].get("anastasia_paid_day", 1)
    if day < 5:
        ctx.user_data[user_id]["anastasia_paid_day"] = day + 1
        await send_paid_day(user_id, day + 1, ctx)
    else:
        await query.message.reply_text(
            "Вы уже закончили платный курс!",
            reply_markup=anastasia_main_menu()
        )

###########################
#      МОЙ КАБИНЕТ
###########################
async def anastasia_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    score = get_score(user_id)
    status = get_status(user_id)
    text = f"Мой кабинет (Анастасия)\nСтатус: {status}\nБаллы: {score}"
    await query.message.reply_text(text, reply_markup=anastasia_main_menu())

###########################
#  КАК ПОТРАТИТЬ БАЛЛЫ
###########################
async def anastasia_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    score = get_score(user_id)
    text = (f"Как потратить баллы (Анастасия)?\nУ вас {score} баллов.\n"
            "Можно купить челлендж (300), получить скидку до 600 руб на платный курс и т.д.")
    await query.message.reply_text(text, reply_markup=anastasia_main_menu())

###########################
#     КБЖУ (диалог)
###########################
async def anastasia_kbju_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    ctx.user_data[user_id]["anastasia_kbju_step"] = "gender"
    await query.message.reply_text("Введите ваш пол (м/ж):")

async def anastasia_handle_kbju_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if "anastasia_kbju_step" not in ctx.user_data[user_id]:
        return

    step = ctx.user_data[user_id]["anastasia_kbju_step"]
    text_in = update.message.text.strip().lower()

    if step == "gender":
        ctx.user_data[user_id]["kbju_gender"] = "male" if text_in.startswith('m') else "female"
        ctx.user_data[user_id]["anastasia_kbju_step"] = "weight"
        await update.message.reply_text("Введите вес (кг):")
    elif step == "weight":
        try:
            w = float(text_in)
            ctx.user_data[user_id]["kbju_weight"] = w
        except ValueError:
            await update.message.reply_text("Неверный формат. Введите число (кг):")
            return
        ctx.user_data[user_id]["anastasia_kbju_step"] = "height"
        await update.message.reply_text("Введите рост (см):")
    elif step == "height":
        try:
            h = float(text_in)
            ctx.user_data[user_id]["kbju_height"] = h
        except ValueError:
            await update.message.reply_text("Неверный формат. Введите число (см):")
            return
        ctx.user_data[user_id]["anastasia_kbju_step"] = "age"
        await update.message.reply_text("Введите возраст (лет):")
    elif step == "age":
        try:
            ag = float(text_in)
            ctx.user_data[user_id]["kbju_age"] = ag
        except ValueError:
            await update.message.reply_text("Неверный формат. Введите число:")
            return
        ctx.user_data[user_id]["anastasia_kbju_step"] = "activity"
        await update.message.reply_text("Введите уровень активности (1-5):")
    elif step == "activity":
        try:
            act = float(text_in)
            ctx.user_data[user_id]["kbju_activity"] = act
        except ValueError:
            await update.message.reply_text("Неверный формат. Введите число 1-5:")
            return
        ctx.user_data[user_id]["anastasia_kbju_step"] = "goal"
        await update.message.reply_text("Введите цель (похудеть / набрать / поддержание):")
    elif step == "goal":
        ctx.user_data[user_id]["kbju_goal"] = text_in
        # Простейший расчет
        gender = ctx.user_data[user_id]["kbju_gender"]
        weight = ctx.user_data[user_id]["kbju_weight"]
        height = ctx.user_data[user_id]["kbju_height"]
        age = ctx.user_data[user_id]["kbju_age"]
        activity = ctx.user_data[user_id]["kbju_activity"]
        goal_text = ctx.user_data[user_id]["kbju_goal"]

        if gender == "male":
            base_cal = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            base_cal = 10 * weight + 6.25 * height - 5 * age - 161

        base_cal *= activity

        if "похуд" in goal_text:
            base_cal *= 0.9
        elif "наб" in goal_text:
            base_cal *= 1.1

        protein = 0.3 * base_cal / 4
        fat = 0.3 * base_cal / 9
        carbs = 0.4 * base_cal / 4

        ctx.user_data[user_id].pop("anastasia_kbju_step", None)
        msg = (f"Расчет КБЖУ (Анастасия):\n"
               f"Ккал: {int(base_cal)}\n"
               f"Белки: ~{int(protein)} г\n"
               f"Жиры: ~{int(fat)} г\n"
               f"Углеводы: ~{int(carbs)} г\n")
        await update.message.reply_text(msg, reply_markup=anastasia_main_menu())
    else:
        await update.message.reply_text("Неизвестный шаг КБЖУ.")

###########################
#     КНОПКА «НАЗАД»
###########################
async def anastasia_back_to_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Просто возвращаем главное меню Анастасии."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "Главное меню Анастасии",
        reply_markup=anastasia_main_menu()
    )
