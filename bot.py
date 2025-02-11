import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ------------------------ ГЛОБАЛЬНЫЕ СЛОВАРИ И СТАТУСЫ ------------------------

user_data = {}  # для хранения данных каждого пользователя: {user_id: { ... }}
user_scores = {}  # для хранения баллов: {user_id: int}
user_reports_sent = {}  # для отметки, что отчет по дню уже отправлен
user_waiting_for_video = {}  # отслеживает, за какой день пользователь отправляет видео
user_waiting_for_receipt = {}  # ждём чек об оплате
user_challenges = {}  # челленджи
user_status = {}  # статус пользователя

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# ------------------------ МЕНЮ ------------------------

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
    ])

# ------------------------ СТАРТ / ИНСТРУКТОР ------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start. Предлагает выбрать тренера.
    Инициализируем словари для пользователя.
    """
    user_id = update.effective_user.id
    user_data.setdefault(user_id, {
        "current_day": 1,
        "instructor": None,
        "gender": None,
        "program": None,
        "paid_current_day": 1,
    })
    user_scores.setdefault(user_id, 0)
    user_status.setdefault(user_id, statuses[0])
    user_reports_sent.setdefault(user_id, {})
    user_challenges.setdefault(user_id, {"current_day": 0})

    # Реферальная логика (если надо)
    if context.args:
        try:
            ref = int(context.args[0])
            if ref != user_id:
                # Начисляем реферальные баллы рефереру
                user_scores[ref] = user_scores.get(ref, 0) + 100
                await context.bot.send_message(chat_id=ref, text="🎉 Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!")
        except ValueError:
            pass

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_1"),
         InlineKeyboardButton("💫 Анастасия", callback_data="instructor_2")],
        [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
        [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
        [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")],
    ])
    await update.message.reply_text("Выбери фитнес‑инструктора:", reply_markup=kb)

async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Сохраняем выбор пользователя (какой тренер) и выводим приветствие.
    """
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "instructor_1":
        user_data[user_id]["instructor"] = "evgeniy"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Привет! Я фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu()
        )
    elif data == "instructor_2":
        user_data[user_id]["instructor"] = "anastasiya"
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Привет! Я фитнес-ассистент!\nВы выбрали тренера: Анастасия",
            reply_markup=main_menu()
        )
    else:
        # Остальные тренеры пока заглушки
        sel = {
            "instructor_3": "Тренер 3",
            "instructor_4": "Тренер 4",
            "instructor_5": "Тренер 5",
        }.get(data, "неизвестный тренер")
        await query.message.edit_text(f"Вы выбрали: {sel}. Пока недоступно.", reply_markup=main_menu())

# ------------------------ БЕСПЛАТНЫЙ КУРС ------------------------

def get_free_course_day_text(day: int) -> str:
    """ Возвращает текст упражнений для бесплатного курса на день day. """
    course = {
        1: [
            "1️⃣ Присед с махом 3x20 [Видео](https://t.me/example1)",
            "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/example2)",
            "3️⃣ Велосипед 3x15 [Видео](https://t.me/example3)",
        ],
        2: [
            "1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/example4)",
            "2️⃣ Лодочка прямые руки 3x30 [Видео](https://t.me/example5)",
            "3️⃣ Полные подъёмы корпуса 3x20 [Видео](https://t.me/example6)",
        ],
        3: [
            "1️⃣ Выпады назад 3x15 [Видео](https://t.me/example7)",
            "2️⃣ Махи в бок с колен 3x20 [Видео](https://t.me/example8)",
            "3️⃣ Косые с касанием пяток 3x15 [Видео](https://t.me/example9)",
        ],
        4: [
            "1️⃣ Поочередные подъемы с гантелями 4x20 [Видео](https://t.me/example10)",
            "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/example11)",
            "3️⃣ Планка 3x1 мин [Видео](https://t.me/example12)",
        ],
        5: [
            "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/example13)",
            "2️⃣ Махи под 45 с резинкой 3x20 [Видео](https://t.me/example14)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/example15)",
        ],
    }
    arr = course.get(day, [])
    text = f"🔥 **Бесплатный курс: День {day}** 🔥\n\n" + "\n".join(arr) + "\n\nОтправьте видео-отчет за день! 🎥"
    return text

async def handle_free_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    profile = user_data[user_id]
    # Если пол/программа не выбраны, запросим
    if profile["gender"] is None or profile["program"] is None:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Мужчина", callback_data="gender_male"),
             InlineKeyboardButton("👩 Женщина", callback_data="gender_female")]
        ])
        await query.message.reply_text("Ваш пол:", reply_markup=kb)
        return

    # Проверим текущий день
    day = profile.get("current_day", 1)
    if day < 1 or day > 5:
        profile["current_day"] = 1
        day = 1

    if day > 5:
        await query.message.reply_text("Вы завершили бесплатный курс! 🎉", reply_markup=main_menu())
        return

    text = get_free_course_day_text(day)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"send_report_day_{day}")]
    ])
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "gender_male":
        user_data[user_id]["gender"] = "male"
    else:
        user_data[user_id]["gender"] = "female"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "program_home":
        user_data[user_id]["program"] = "home"
    else:
        user_data[user_id]["program"] = "gym"
    user_data[user_id]["current_day"] = 1
    await handle_free_course(update, context)

async def handle_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Определим день из callback_data
    try:
        parts = query.data.split("_")
        day = int(parts[-1])
    except ValueError:
        await query.message.reply_text("Ошибка: неверные данные.")
        return

    # проверим, не отправлял ли уже
    if user_reports_sent.get(user_id, {}).get(day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {day}.")
        return

    # Ждём видео
    user_waiting_for_video[user_id] = day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет 🎥")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_waiting_for_video:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")
        return

    day = user_waiting_for_video[user_id]
    # Отправляем видео в группу
    try:
        await context.bot.send_message(chat_id=GROUP_ID, text=f"Видео-отчет от {update.message.from_user.first_name} (ID: {user_id}) за день {day}.")
        await context.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
    except Exception as e:
        logger.error(f"Ошибка отправки видео: {e}")
        await update.message.reply_text("Ошибка при отправке видео в группу.")
        return

    # Начисляем баллы
    user_scores[user_id] = user_scores.get(user_id, 0) + 60
    user_reports_sent.setdefault(user_id, {})[day] = True
    del user_waiting_for_video[user_id]

    if day < 5:
        user_data[user_id]["current_day"] = day + 1
        await update.message.reply_text(
            f"Отчет за день {day} принят! 🎉\nВаши баллы: {user_scores[user_id]}\nГотовы к следующему дню?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"➡️ День {day+1}", callback_data="free_course")]
            ])
        )
    else:
        user_status[user_id] = statuses[1]
        await update.message.reply_text(
            f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: {user_scores[user_id]}",
            reply_markup=main_menu()
        )

# ------------------------ ПЛАТНЫЙ КУРС ------------------------

async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    discount = min(score * 2, 600)
    price = 2000 - discount
    text = (f"📚 **Платный курс** 📚\n\n"
            f"Стоимость: 2000 руб.\n"
            f"Ваша скидка: {discount} руб.\n"
            f"Итоговая сумма: {price} руб.\n\n"
            "Переведите сумму на карту 89236950304 (Яндекс Банк). После оплаты отправьте чек.")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧾 Отправить чек", callback_data="send_receipt")]
    ])
    user_waiting_for_receipt[user_id] = True
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_send_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt[user_id] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате.")

async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_waiting_for_receipt or not user_waiting_for_receipt[user_id]:
        await update.message.reply_text("Я не жду чек от вас.")
        return

    photo = update.message.photo[-1]
    try:
        await context.bot.send_message(chat_id=GROUP_ID, text=f"Чек от {update.message.from_user.first_name} (ID: {user_id}).")
        await context.bot.send_photo(chat_id=GROUP_ID, photo=photo.file_id, caption="Подтвердите оплату.",
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_payment_{user_id}")]
                                     ]))
        await update.message.reply_text("Чек отправлен на проверку.")
    except Exception as e:
        logger.error(f"Ошибка отправки чека: {e}")
        await update.message.reply_text("Ошибка при отправке чека.")
        return

async def handle_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    # confirm_payment_userid
    user_id_str = data.replace("confirm_payment_", "")
    try:
        user_id = int(user_id_str)
    except ValueError:
        await query.answer("Ошибка подтверждения.")
        return

    user_status[user_id] = statuses[2]
    user_waiting_for_receipt[user_id] = False
    await context.bot.send_message(chat_id=user_id, text="Оплата подтверждена! Вам открыт доступ к платному курсу.")

    # Допустим, сразу отправляем первый день платного курса
    user_data[user_id]["paid_current_day"] = 1
    await send_paid_day(user_id, context)

async def send_paid_day(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    day = user_data[user_id].get("paid_current_day", 1)
    paid_program = {
        1: [
            "Махи назад 3x25+5",
            "Выпады 3x30 шагов",
            "Разведение ног 3x20"
        ],
        2: [
            "Косые скручивания 3x30+10",
            "Отжимания от пола 3x15+5",
            "Лодочка с локтями 3x20+5"
        ],
        3: [
            "Подъёмы ног 3х15+5",
            "Разгибание ног 3х15+5",
            "Ягодичный мост 3х20+5"
        ],
        4: [
            "Скручивания 3x20+10",
            "Отжимания в ТРХ 3x15+5",
            "Подтягивания в ТРХ 3х15"
        ],
        5: [
            "Финальный день 🏆"
        ],
    }
    ex = paid_program.get(day, [])
    text = f"📚 **Платный курс: День {day}**\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет!"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"paid_video_day_{day}")]
    ])
    await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown", reply_markup=kb)

async def handle_paid_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    # paid_video_day_X
    day_str = data.replace("paid_video_day_", "")
    try:
        day = int(day_str)
    except ValueError:
        await query.answer("Ошибка.")
        return

    user_waiting_for_video[user_id] = ("paid", day)
    await query.message.reply_text(f"Пришлите видео-отчет за платный день {day}.")

async def handle_video_paid(update: Update, context: ContextTypes.DEFAULT_TYPE, paid_day: int):
    user_id = update.message.from_user.id
    # Отправим в группу
    try:
        await context.bot.send_message(chat_id=GROUP_ID, text=f"Платный отчет от {update.message.from_user.first_name} (ID: {user_id}), день {paid_day}.")
        await context.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
    except Exception as e:
        logger.error(f"Ошибка отправки платного видео: {e}")
        await update.message.reply_text("Ошибка при отправке видео.")
        return

    # начисляем баллы
    user_scores[user_id] += 30
    del user_waiting_for_video[user_id]

    if paid_day < 5:
        user_data[user_id]["paid_current_day"] = paid_day + 1
        await update.message.reply_text(
            f"Отчет за платный день {paid_day} принят!\nВаши баллы: {user_scores[user_id]}.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"➡️ День {paid_day+1}", callback_data="paid_next_day")]
            ])
        )
    else:
        await update.message.reply_text(f"Поздравляем! Вы завершили платный курс!\nВаши баллы: {user_scores[user_id]}", reply_markup=main_menu())
        user_data[user_id]["paid_current_day"] = 1
        user_status[user_id] = statuses[3]

async def handle_paid_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    current_day = user_data[user_id].get("paid_current_day", 1)
    if current_day <= 5:
        await send_paid_day(user_id, context)
    else:
        await query.message.reply_text("Вы уже прошли платный курс!", reply_markup=main_menu())

# ------------------------ ЧЕЛЛЕНДЖИ ------------------------

def get_challenge_text(day: int) -> str:
    data = {
        1: [
            "Выпады назад 40 раз",
            "Лодочка + сгибание в локтях 50 раз",
            "Велосипед 30 на каждую ногу"
        ],
        2: [
            "Присед со штангой 30 раз",
            "Отжимания с отрывом рук 25 раз",
            "Полные подъёмы корпуса 30 раз"
        ],
        3: [
            "Планка 3 мин",
            "Подъёмы ног лёжа 3x15"
        ],
        4: [
            "Выпады назад 60 раз",
            "Лодочка + сгибание 50 раз",
            "Велосипед 50 на каждую ногу"
        ],
        5: [
            "Присед со штангой 50 раз",
            "Отжимания с отрывом рук 40 раз",
            "Полные подъёмы корпуса 50 раз"
        ],
    }
    arr = data.get(day, [])
    return f"💪 **Челлендж: День {day}**\n\n" + "\n".join(arr)

async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_challenges[user_id].get("current_day", 0) > 0:
        # уже купили челлендж
        await send_challenge_day(query.message, user_id)
    else:
        if user_scores.get(user_id, 0) >= 300:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Купить за 300 баллов", callback_data="buy_challenge"),
                 InlineKeyboardButton("🔙 Назад", callback_data="back")]
            ])
            await query.message.reply_text("Купить доступ к челленджам за 300 баллов?", reply_markup=kb)
        else:
            await query.message.reply_text(
                f"Недостаточно баллов. Нужно 300, у вас {user_scores.get(user_id, 0)}",
                reply_markup=main_menu()
            )

async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id]["current_day"] = 1
        await query.message.reply_text("Доступ к челленджам получен!", reply_markup=main_menu())
        await send_challenge_day(query.message, user_id)
    else:
        await query.message.reply_text("Недостаточно баллов!", reply_markup=main_menu())

async def send_challenge_day(msg, user_id: int):
    day = user_challenges[user_id].get("current_day", 1)
    if day < 1 or day > 5:
        user_challenges[user_id]["current_day"] = 1
        day = 1
    text = get_challenge_text(day)
    if day < 5:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Следующий день", callback_data="challenge_next")]
        ])
    else:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Главное меню", callback_data="back")]
        ])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_challenge_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    current_day = user_challenges[user_id].get("current_day", 1)
    if current_day < 5:
        user_challenges[user_id]["current_day"] = current_day + 1
        await send_challenge_day(query.message, user_id)
    else:
        await query.message.reply_text("Вы прошли все челленджи!", reply_markup=main_menu())

# ------------------------ МЕНЮ ПИТАНИЯ, РЕФЕРАЛЫ И ДРУГОЕ ------------------------

async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍴 Купить меню питания за 300 баллов", callback_data="buy_nutrition_menu"),
         InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки.", reply_markup=kb)

async def handle_buy_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_scores[user_id] >= 300:
        user_scores[user_id] -= 300
        await query.message.reply_text("Меню питания куплено! Вот ссылка: https://t.me/...", reply_markup=main_menu())
    else:
        await query.message.reply_text("Недостаточно баллов!", reply_markup=main_menu())

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    me = await context.bot.get_me()
    link = f"https://t.me/{me.username}?start={query.from_user.id}"
    await query.message.reply_text(f"Ваша реферальная ссылка:\n{link}")

async def handle_my_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    sc = user_scores.get(user_id, 0)
    st = user_status.get(user_id, statuses[0])
    text = f"👤 Ваш кабинет:\nСтатус: {st}\nБаллы: {sc}"
    await query.message.reply_text(text, reply_markup=main_menu())

async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("👤 О тренере:\n\n"
            "Курочкин Евгений...\n"
            "20 лет в фитнесе!")
    await query.message.reply_text(text, reply_markup=main_menu())

async def handle_earn_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("💡 Как заработать баллы:\n\n"
            "1) Проходите бесплатный курс\n"
            "2) Участвуйте в челленджах\n"
            "3) Приглашайте друзей\n"
            "4) Покупайте платный курс")
    await query.message.reply_text(text, reply_markup=main_menu())

async def handle_spend_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    sc = user_scores.get(user_id, 0)
    text = (f"💰 Как потратить баллы:\n\n"
            f"У вас {sc} баллов.\n"
            "Можно получить скидку на платный курс (1 балл = 2 руб, макс скидка 600 руб)\n")
    await query.message.reply_text(text, reply_markup=main_menu())

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню", reply_markup=main_menu())

# ------------------------ ФУНКЦИЯ MAIN ------------------------

def main():
    app = Application.builder().token(TOKEN).build()

    # /start
    app.add_handler(CommandHandler("start", start))

    # Выбор инструктора
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))

    # Бесплатный курс
    app.add_handler(CallbackQueryHandler(handle_free_course, pattern="^free_course$"))
    app.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    app.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"^send_report_day_\d+$"))

    # Видео (бесплатный)
    app.add_handler(MessageHandler(filters.VIDEO & (~filters.COMMAND), handle_video))

    # Платный курс
    app.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    app.add_handler(CallbackQueryHandler(handle_send_receipt, pattern="^send_receipt$"))
    app.add_handler(CallbackQueryHandler(handle_confirm_payment, pattern="^confirm_payment_"))
    app.add_handler(MessageHandler(filters.PHOTO & (~filters.COMMAND), handle_receipt_photo))
    app.add_handler(CallbackQueryHandler(handle_paid_send_report, pattern="^paid_video_day_\d+$"))
    app.add_handler(CallbackQueryHandler(handle_paid_next_day, pattern="^paid_next_day$"))

    # Челленджи
    app.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    app.add_handler(CallbackQueryHandler(buy_challenge, pattern="^buy_challenge$"))
    app.add_handler(CallbackQueryHandler(handle_challenge_next_day, pattern="^challenge_next$"))

    # Прочее
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern="^buy_nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="^my_cabinet$"))
    app.add_handler(CallbackQueryHandler(handle_about_me, pattern="^about_me$"))
    app.add_handler(CallbackQueryHandler(handle_earn_points, pattern="^earn_points$"))
    app.add_handler(CallbackQueryHandler(handle_spend_points, pattern="^spend_points$"))
    app.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))

    logger.info("Бот запущен и готов к работе 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
