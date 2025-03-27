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

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# Глобальные словари для хранения данных
user_scores = {}  # {user_id: {instructor: баллы}}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}
user_waiting_for_challenge_video = {}
user_waiting_for_receipt = {}
user_challenges = {}
user_paid_course = {}
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Вспомогательные функции
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

def get_report_button_text(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    gender = context.user_data[user_id].get("gender", "male")
    program = context.user_data[user_id].get("program", "home")
    prefix = "👩" if gender == "female" else "👨"
    suffix = "🏠" if program == "home" else "🏋️"
    return f"{prefix}{suffix} Отправить отчет"

# Функции бесплатного курса
async def start_free_course(message, context: ContextTypes.DEFAULT_TYPE, user_id: int, instructor: str):
    if not (context.user_data[user_id].get("gender") == "female" and context.user_data[user_id].get("program") == "home"):
        await message.reply_text("Пока в разработке", reply_markup=main_menu())
        return

    context.user_data[user_id].setdefault("free_course", {})
    context.user_data[user_id]["free_course"].setdefault(instructor, {"current_day": 1})
    current_day = context.user_data[user_id]["free_course"][instructor]["current_day"]

    if current_day > 5:
        await message.reply_text(f"Вы завершили бесплатный курс у тренера {instructor}! 🎉", reply_markup=main_menu())
        return

    photo_paths = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
    }

    course_program = {
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
            "2️⃣ Махи под 45 с резинкой (можно без нее) 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
        ],
    }

    exercises = course_program.get(current_day, [])
    caption = f"🔥 **Бесплатный курс у {instructor}: День {current_day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    report_button_text = get_report_button_text(context, user_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(report_button_text, callback_data=f"send_report_day_{current_day}_{instructor}")]
    ])
    try:
        await context.bot.send_photo(
            chat_id=message.chat_id,
            photo=photo_paths.get(current_day),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await message.reply_text(
            "Ошибка: изображение не найдено. Продолжайте без фото.",
            reply_markup=keyboard,
        )

async def handle_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split("_")
    current_day = int(data[3])
    instructor = data[4]
    if user_reports_sent.get(user_id, {}).get(f"{instructor}_free_{current_day}"):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day} у тренера {instructor}.")
        return
    user_waiting_for_video[user_id] = (current_day, instructor, "free")
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in user_waiting_for_video:
        current_day, instructor, course_type = user_waiting_for_video[user_id]
        if course_type == "free":
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {current_day} бесплатного курса у тренера {instructor}."
            )
            await context.bot.send_video(
                chat_id=GROUP_ID,
                video=update.message.video.file_id
            )
            user_reports_sent.setdefault(user_id, {})[f"{instructor}_free_{current_day}"] = True
            user_scores.setdefault(user_id, {}).setdefault(instructor, 0)
            user_scores[user_id][instructor] += 60
            del user_waiting_for_video[user_id]
            if current_day < 5:
                context.user_data[user_id]["free_course"][instructor]["current_day"] += 1
                new_day = context.user_data[user_id]["free_course"][instructor]["current_day"]
                await update.message.reply_text(
                    f"Отчет за день {current_day} принят! 🎉\nВаши баллы у тренера {instructor}: {user_scores[user_id][instructor]}.\nГотовы к следующему дню ({new_day})?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"➡️ День {new_day}", callback_data=f"next_day_{instructor}")]
                    ]),
                )
            else:
                user_status[user_id] = statuses[1]
                await update.message.reply_text(
                    f"Поздравляем! Вы завершили бесплатный курс у тренера {instructor}! 🎉\nВаши баллы: {user_scores[user_id][instructor]}.",
                    reply_markup=main_menu(),
                )
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.", reply_markup=main_menu())

# Обработчики выбора пола и программы
async def handle_free_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if not instructor:
        await query.message.reply_text("Сначала выберите тренера.", reply_markup=main_menu())
        return
    if query.data == "free_course":
        if "gender" not in context.user_data[user_id] or "program" not in context.user_data[user_id]:
            gender_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Мужчина", callback_data="gender_male"),
                 InlineKeyboardButton("Женщина", callback_data="gender_female")]
            ])
            await query.message.reply_text("Ваш пол:", reply_markup=gender_keyboard)
            return
    await start_free_course(query.message, context, user_id, instructor)

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data[user_id]["gender"] = "male" if query.data == "gender_male" else "female"
    program_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=program_keyboard)

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data[user_id]["program"] = "home" if query.data == "program_home" else "gym"
    instructor = context.user_data[user_id].get("instructor")
    await start_free_course(query.message, context, user_id, instructor)

# Функции для платного курса
async def start_paid_course(message, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    instructor = user_paid_course[user_id]["instructor"]
    current_day = user_paid_course[user_id]["current_day"]
    if current_day > 5:
        await message.reply_text(f"Вы завершили платный курс у тренера {instructor}! 🎉", reply_markup=main_menu())
        return

    paid_course_programs = {
        "evgeniy": {
            1: [
                "1️⃣ Становая тяга (без веса) 3x15 [Видео](https://t.me/c/2241417709/140/141)",
                "2️⃣ Жим ногами (имитация) 3x20 [Видео](https://t.me/c/2241417709/155/156)",
                "3️⃣ Планка с подъемом ног 3x1 мин [Видео](https://t.me/c/2241417709/286/296)",
            ],
        },
        "anastasiya": {
            1: [
                "1️⃣ Ягодичный мост с резинкой 3x30 [Видео](https://t.me/c/2241417709/381/382)",
                "2️⃣ Махи ногами назад 3x20 [Видео](https://t.me/c/2241417709/339/340)",
                "3️⃣ Планка на локтях 3x1 мин [Видео](https://t.me/c/2241417709/286/296)",
            ],
        },
    }

    exercises = paid_course_programs.get(instructor, {}).get(current_day, ["Пока в разработке"])
    caption = f"📚 **Платный курс у {instructor}: День {current_day}** 📚\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"send_paid_report_day_{current_day}_{instructor}")]
    ])
    await context.bot.send_message(
        chat_id=message.chat_id,
        text=caption,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

async def handle_send_paid_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split("_")
    current_day = int(data[4])
    instructor = data[5]
    if user_reports_sent.get(user_id, {}).get(f"{instructor}_paid_{current_day}"):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day} платного курса у тренера {instructor}.")
        return
    user_waiting_for_video[user_id] = (current_day, instructor, "paid")
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день платного курса.")

# Функции для челленджей
async def send_challenge_task(message: Update, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    instructor = user_challenges[user_id]["instructor"]
    current_day = user_challenges[user_id]["current_day"]
    if current_day > 5:
        await message.reply_text(f"Вы завершили челлендж у тренера {instructor}! 🎉", reply_markup=main_menu())
        return

    challenge_programs = {
        "evgeniy": {
            1: [
                "1️⃣ Становая тяга (имитация) 40 раз [Видео](https://t.me/c/2241417709/140/141)",
                "2️⃣ Планка с подъемом ног 3 мин [Видео](https://t.me/c/2241417709/286/296)",
                "3️⃣ Велосипед с утяжелением 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
            ],
        },
        "anastasiya": {
            1: [
                "1️⃣ Ягодичный мост с резинкой 50 раз [Видео](https://t.me/c/2241417709/381/382)",
                "2️⃣ Махи ногами назад 40 раз [Видео](https://t.me/c/2241417709/339/340)",
                "3️⃣ Планка на локтях 3 мин [Видео](https://t.me/c/2241417709/286/296)",
            ],
        },
    }

    exercises = challenge_programs.get(instructor, {}).get(current_day, ["Пока в разработке"])
    caption = f"💪 **Челлендж у {instructor}: День {current_day}** 💪\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    buttons = [
        [InlineKeyboardButton("📹 Отправить отчет", callback_data=f"send_challenge_report_day_{current_day}_{instructor}")]
    ]
    if current_day < 5:
        buttons.append([InlineKeyboardButton("➡️ Следующий день", callback_data="challenge_next")])
    else:
        buttons.append([InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="back")])
    keyboard = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_send_challenge_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split("_")
    current_day = int(data[4])
    instructor = data[5]
    if user_reports_sent.get(user_id, {}).get(f"{instructor}_challenge_{current_day}"):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day} челленджа у тренера {instructor}.")
        return
    user_waiting_for_challenge_video[user_id] = (current_day, instructor)
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день челленджа.")

async def handle_challenge_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in user_challenges:
        await query.answer("Сначала купите челлендж!")
        return
    current_day = user_challenges[user_id]["current_day"]
    if current_day < 5:
        user_challenges[user_id]["current_day"] += 1
        await send_challenge_task(query.message, user_id, context)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж!", reply_markup=main_menu())
        if user_id in user_waiting_for_challenge_video:
            del user_waiting_for_challenge_video[user_id]
        del user_challenges[user_id]

# Обработка команды /start и выбора тренера
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if context.args:
            referrer_id_str = context.args[0]
            try:
                referrer_id = int(referrer_id_str)
                if referrer_id != user_id:
                    instructor = context.user_data[referrer_id].get("instructor")
                    if instructor:
                        user_scores.setdefault(referrer_id, {}).setdefault(instructor, 0)
                        user_scores[referrer_id][instructor] += 100
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов у тренера {instructor}!"
                        )
            except ValueError:
                pass

        context.user_data.setdefault(user_id, {})
        if user_id not in user_scores:
            user_scores[user_id] = {}
        if user_id not in user_status:
            user_status[user_id] = statuses[0]
        
        instructor_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Евгений Курочкин", callback_data="instructor_1")],
            [InlineKeyboardButton("АНАСТАСИЯ", callback_data="instructor_2")],
            [InlineKeyboardButton("Тренер 3", callback_data="instructor_3")],
            [InlineKeyboardButton("Тренер 4", callback_data="instructor_4")],
            [InlineKeyboardButton("Тренер 5", callback_data="instructor_5")],
        ])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери для себя фитнес инструктора:",
            reply_markup=instructor_keyboard,
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()
    if data == "instructor_1":
        context.user_data[user_id]["instructor"] = "evgeniy"
        await query.message.edit_text("Вы выбрали тренера: Евгений Курочкин")
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://github.com/boss198806/telegram-bot/raw/refs/heads/main/IMG_1484.MOV",
            supports_streaming=True,
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu()
        )
    elif data == "instructor_2":
        context.user_data[user_id]["instructor"] = "anastasiya"
        await query.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ")
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu()
        )
    else:
        if data == "instructor_3":
            selected_name = "Тренер 3"
        elif data == "instructor_4":
            selected_name = "Тренер 4"
        elif data == "instructor_5":
            selected_name = "Тренер 5"
        else:
            selected_name = "неизвестный тренер"
        await query.message.edit_text(
            f"Вы выбрали тренера: {selected_name}. Функционал пока не реализован.\nВы будете перенаправлены в главное меню.",
            reply_markup=main_menu()
        )

# Остальной функционал
async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Купить меню питания за 300 баллов", callback_data="buy_nutrition_menu")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки:", reply_markup=keyboard)

async def handle_buy_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor and user_scores.get(user_id, {}).get(instructor, 0) >= 300:
        user_scores[user_id][instructor] -= 300
        await query.message.reply_text(
            f"Покупка меню питания успешно завершена у тренера {instructor}!\nВот ваше меню питания: https://t.me/MENUKURO4KIN/2",
            reply_markup=main_menu()
        )
    else:
        await query.message.reply_text(f"Недостаточно баллов у тренера {instructor} для покупки меню питания!")

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await context.bot.get_me()
    referral_link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(
        f"Ваша реферальная ссылка:\n{referral_link}\n\nПоделитесь этой ссылкой с друзьями, и когда они начнут пользоваться ботом, вы получите 100 баллов у вашего текущего тренера!"
    )

async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if user_challenges.get(user_id):
        await send_challenge_task(query.message, user_id, context)
    elif user_scores.get(user_id, {}).get(instructor, 0) >= 300:
        buttons = [
            [InlineKeyboardButton("Купить доступ за 300 баллов", callback_data="buy_challenge")],
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]
        await query.message.reply_text(
            f"Доступ к челленджам у тренера {instructor} стоит 300 баллов. Хотите приобрести?",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        await query.message.reply_text(
            f"Для доступа к челленджам у тренера {instructor} нужно 300 баллов.\nУ вас: {user_scores.get(user_id, {}).get(instructor, 0)} баллов.\nПродолжайте тренировки!"
        )

async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if user_scores.get(user_id, {}).get(instructor, 0) >= 300:
        user_scores[user_id][instructor] -= 300
        user_challenges[user_id] = {"current_day": 1, "instructor": instructor}
        await query.message.reply_text(f"✅ Доступ к челленджам у тренера {instructor} открыт!")
        await send_challenge_task(query.message, user_id, context)
    else:
        await query.message.reply_text(f"Недостаточно баллов у тренера {instructor} для покупки доступа!")

async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    discount = min(user_scores.get(user_id, {}).get(instructor, 0) * 2, 600)
    final_price = 2000 - discount
    await query.message.reply_text(
        f"📚 **Платный курс у {instructor}** 📚\n\n"
        f"Стоимость курса: 2000 рублей.\n"
        f"Ваша скидка: {discount} рублей.\n"
        f"Итоговая сумма: {final_price} рублей.\n\n"
        f"Переведите сумму на карту: 89236950304 (Яндекс Банк).\n"
        f"После оплаты отправьте чек для проверки.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Отправить чек", callback_data="send_receipt")]
        ]),
    )
    user_waiting_for_receipt[user_id] = True

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id not in user_waiting_for_receipt:
        await update.message.reply_text("Я не жду чек от вас. Пожалуйста, выберите платный курс и отправьте чек.")
        return
    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фото чека.")
        return
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"Чек от {user_name} (ID: {user_id}). Подтвердите оплату.",
    )
    photo_file_id = update.message.photo[-1].file_id
    await context.bot.send_photo(
        chat_id=GROUP_ID,
        photo=photo_file_id,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Подтвердить", callback_data=f"confirm_payment_{user_id}")]
        ]),
    )
    await update.message.reply_text("Чек отправлен на проверку. Ожидайте подтверждения.")

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = int(query.data.split("_")[-1])
    instructor = context.user_data[user_id].get("instructor")
    user_status[user_id] = statuses[2]
    del user_waiting_for_receipt[user_id]
    user_paid_course[user_id] = {"current_day": 1, "instructor": instructor}
    await context.bot.send_message(
        chat_id=user_id,
        text=f"Оплата подтверждена! Вам открыт доступ к платному курсу у тренера {instructor}. 🎉",
    )
    await start_paid_course(query.message, context, user_id)

async def handle_my_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    status = user_status.get(user_id, statuses[0])
    scores_text = "\n".join([f"Баллы у {instructor}: {score}" for instructor, score in user_scores.get(user_id, {}).items()])
    caption = (
        f"👤 Ваш кабинет:\n\n"
        f"Статус: {status}\n"
        f"{scores_text}\n"
        "Продолжайте тренироваться, чтобы улучшить статус и заработать больше баллов!"
    )
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
            caption=caption,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото для 'Мой кабинет': {e}")
        await query.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")

async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    caption = (
        "👤 О тренере:\n\n"
        "Курочкин Евгений Витальевич\n"
        "Общий тренировочный стаж - 20 лет\n"
        "Стаж работы - 15 лет\n"
        "МС - по становой тяге\n"
        "МС - по жиму штанги лежа\n"
        "Судья - федеральной категории\n"
        "Организатор соревнований\n"
        "КМС - по бодибилдингу\n\n"
        "20 лет в фитнесе!"
    )
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
            caption=caption,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото для 'Обо мне': {e}")
        await query.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")

async def handle_earn_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    caption = (
        "💡 Как заработать баллы:\n\n"
        "1. Проходите бесплатный курс и отправляйте видео-отчеты.\n"
        "2. Участвуйте в челленджах и отправляйте видео-отчеты.\n"
        "3. Приглашайте друзей и получайте баллы за их активность.\n"
        "4. Покупайте платный курс и получаете дополнительные баллы."
    )
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
            caption=caption,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото для 'Как заработать баллы': {e}")
        await query.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")

async def handle_spend_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    score = user_scores.get(user_id, {}).get(instructor, 0)
    caption = (
        f"💰 Как потратить баллы у тренера {instructor}:\n\n"
        f"У вас есть {score} баллов.\n"
        "Вы можете потратить баллы на:\n"
        "- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
        "- Максимальная скидка - 600 рублей.\n"
        "- Другие привилегии в будущем!"
    )
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
            caption=caption,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке фото для 'Как потратить баллы': {e}")
        await query.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню", reply_markup=main_menu())

# Регистрация обработчиков
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern="^(free_course|next_day)$"))
    application.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    application.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)_(\w+)"))
    application.add_handler(CallbackQueryHandler(handle_send_paid_report, pattern=r"send_paid_report_day_(\d+)_(\w+)"))
    application.add_handler(CallbackQueryHandler(handle_send_challenge_report, pattern=r"send_challenge_report_day_(\d+)_(\w+)"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    application.add_handler(CallbackQueryHandler(buy_challenge, pattern="^buy_challenge$"))
    application.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment_"))
    application.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="^my_cabinet$"))
    application.add_handler(CallbackQueryHandler(handle_about_me, pattern="^about_me$"))
    application.add_handler(CallbackQueryHandler(handle_earn_points, pattern="^earn_points$"))
    application.add_handler(CallbackQueryHandler(handle_spend_points, pattern="^spend_points$"))
    application.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern="^buy_nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))
    application.add_handler(CallbackQueryHandler(handle_challenge_next_day, pattern="^challenge_next$"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))

    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
