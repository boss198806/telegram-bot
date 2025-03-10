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
user_scores_evgeniy = {}
user_scores_anastasiya = {}
user_status = {}
user_reports_sent_evgeniy = {}
user_reports_sent_anastasiya = {}
user_waiting_for_video_evgeniy = {}
user_waiting_for_video_anastasiya = {}
user_waiting_for_challenge_video_evgeniy = {}
user_waiting_for_challenge_video_anastasiya = {}
user_waiting_for_receipt = {}
user_challenges_evgeniy = {}
user_challenges_anastasiya = {}
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

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

async def start_free_course(message, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    instructor = context.user_data[user_id].get("instructor")
    user_scores, user_reports_sent, user_waiting_for_video = get_instructor_data(instructor)

    # Установим текущий день для каждого инструктора отдельно
    current_day_key = f"current_day_{instructor}"
    if current_day_key not in context.user_data[user_id]:
        context.user_data[user_id][current_day_key] = 1

    current_day = context.user_data[user_id][current_day_key]

    if not (context.user_data[user_id].get("gender") == "female" and context.user_data[user_id].get("program") == "home"):
        await message.reply_text("Пока в разработке", reply_markup=main_menu())
        return

    if current_day > 5:
        await message.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
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
    caption = f"🔥 **Бесплатный курс: День {current_day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    report_button_text = get_report_button_text(context, user_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(report_button_text, callback_data=f"send_report_day_{current_day}")]
    ])

    # Убедимся, что текущий день обновляется корректно
    if current_day < 5:
        next_day = current_day + 1
        keyboard.inline_keyboard.append([InlineKeyboardButton(f"➡️ День {next_day}", callback_data=f"next_day_{next_day}")])

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
    current_day = int(query.data.split("_")[-1])
    instructor = context.user_data[user_id].get("instructor")
    user_reports_sent, user_waiting_for_video = get_instructor_data(instructor)[1:3]

    current_day_key = f"current_day_{instructor}"

    if user_reports_sent.get(user_id, {}).get(current_day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day}.")
        return

    user_waiting_for_video[user_id] = current_day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    instructor = context.user_data[user_id].get("instructor")
    user_scores, user_reports_sent, user_waiting_for_video, user_waiting_for_challenge_video = get_instructor_data(instructor)

    current_day_key = f"current_day_{instructor}"

    if user_id in user_waiting_for_video:
        current_day = user_waiting_for_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {current_day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        user_reports_sent.setdefault(user_id, {})[current_day] = True
        user_scores[user_id] += 60
        del user_waiting_for_video[user_id]

        if current_day < 5:
            context.user_data[user_id][current_day_key] += 1
            new_day = context.user_data[user_id][current_day_key]
            user_waiting_for_video[user_id] = new_day
            await update.message.reply_text(
                f"Отчет за день {current_day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.\nГотовы к следующему дню ({new_day})?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {new_day}", callback_data="next_day")]
                ]),
            )
        else:
            user_status[user_id] = statuses[1]
            await update.message.reply_text(
                f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: {user_scores[user_id]}.",
                reply_markup=main_menu(),
            )
    elif user_id in user_waiting_for_challenge_video:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от {user_name} (ID: {user_id}) за челлендж."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )
        user_scores[user_id] += 60
        del user_waiting_for_challenge_video[user_id]
        await update.message.reply_text(
            f"Отчет за челлендж принят! 🎉\nВаши баллы: {user_scores[user_id]}."
        )
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")

# --- Обработчики выбора пола и программы для бесплатного курса ---

async def handle_free_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "free_course":
        if "gender" not in context.user_data[user_id] or "program" not in context.user_data[user_id]:
            gender_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Мужчина", callback_data="gender_male"),
                 InlineKeyboardButton("Женщина", callback_data="gender_female")]
            ])
            await query.message.reply_text("Ваш пол:", reply_markup=gender_keyboard)
            return
    await start_free_course(query.message, context, user_id)

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
    context.user_data[user_id]["current_day"] = 1
    await start_free_course(query.message, context, user_id)

# --- Функции для обработки команды /start и выбора инструктора ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        # Обработка реферального параметра
        if context.args:
            referrer_id_str = context.args[0]
            try:
                referrer_id = int(referrer_id_str)
                if referrer_id != user_id:
                    user_scores_evgeniy[referrer_id] = user_scores_evgeniy.get(referrer_id, 0) + 100
                    user_scores_anastasiya[referrer_id] = user_scores_anastasiya.get(referrer_id, 0) + 100
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text="Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!"
                        )
                    except Exception as e:
                        logger.error(f"Не удалось отправить сообщение о реферальном бонусе пользователю {referrer_id}: {e}")
            except ValueError:
                pass

        context.user_data.setdefault(user_id, {"current_day": 1})
        user_scores_evgeniy[user_id] = user_scores_evgeniy.get(user_id, 0)
        user_scores_anastasiya[user_id] = user_scores_anastasiya.get(user_id, 0)
        user_status[user_id] = user_status.get(user_id, statuses[0])

        # Выбор инструктора (5 кнопок)
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
        # Отправляем видео с поддержкой потокового воспроизведения
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

# --- Остальной функционал ---

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
    if instructor == "evgeniy":
        user_scores = user_scores_evgeniy
    else:
        user_scores = user_scores_anastasiya

    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        await query.message.reply_text(
            "Покупка меню питания успешно завершена!\nВот ваше меню питания: https://t.me/MENUKURO4KIN/2",
            reply_markup=main_menu()
        )
    else:
        await query.message.reply_text("Недостаточно баллов для покупки меню питания!")

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await context.bot.get_me()
    referral_link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(
        f"Ваша реферальная ссылка:\n{referral_link}\n\nПоделитесь этой ссылкой с друзьями, и когда они начнут пользоваться ботом, вы получите 100 баллов!"
    )

async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor == "evgeniy":
        user_scores = user_scores_evgeniy
        user_challenges = user_challenges_evgeniy
    else:
        user_scores = user_scores_anastasiya
        user_challenges = user_challenges_anastasiya

    if user_challenges.get(user_id):
        await send_challenge_task(query.message, user_id)
    elif user_scores.get(user_id, 0) >= 300:
        buttons = [
            [InlineKeyboardButton("Купить доступ за 300 баллов", callback_data="buy_challenge")],
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]
        await query.message.reply_text(
            "Доступ к челленджам стоит 300 баллов. Хотите приобрести?",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        await query.message.reply_text(
            f"Для доступа к челленджам нужно 300 баллов.\nУ вас: {user_scores.get(user_id, 0)} баллов.\nПродолжайте тренировки!"
        )

async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor == "evgeniy":
        user_scores = user_scores_evgeniy
        user_challenges = user_challenges_evgeniy
    else:
        user_scores = user_scores_anastasiya
        user_challenges = user_challenges_anastasiya

    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id] = {"current_day": 1}
        await query.message.reply_text("✅ Доступ к челленджам открыт!")
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("Недостаточно баллов для покупки доступа!")

async def send_challenge_task(message: Update, user_id: int):
    instructor = context.user_data[user_id].get("instructor")
    if instructor == "evgeniy":
        user_challenges = user_challenges_evgeniy
    else:
        user_challenges = user_challenges_anastasiya

    current_day = user_challenges[user_id]["current_day"]
    exercises = {
        1: [
            "1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
            "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)",
        ],
        2: [
            "1️⃣ Присед со штангой (можно без) 30 раз [Видео](https://t.me/c/2241417709/140/141)",
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
            "1️⃣ Присед со штангой (можно без) 50 раз [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
            "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)",
        ],
    }.get(current_day, [])
    caption = f"💪 **Челлендж: День {current_day}** 💪\n\n" + "\n".join(exercises)
    if current_day < 5:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Следующий день", callback_data="challenge_next")]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="back")]
        ])
    await message.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_challenge_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor == "evgeniy":
        user_challenges = user_challenges_evgeniy
    else:
        user_challenges = user_challenges_anastasiya

    if user_id not in user_challenges:
        await query.answer("Сначала купите челлендж!")
        return
    current_day = user_challenges[user_id]["current_day"]
    if current_day < 5:
        user_challenges[user_id]["current_day"] += 1
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж!", reply_markup=main_menu())
        del user_challenges[user_id]

async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor == "evgeniy":
        user_scores = user_scores_evgeniy
    else:
        user_scores = user_scores_anastasiya

    discount = min(user_scores.get(user_id, 0) * 2, 600)
    final_price = 2000 - discount
    await query.message.reply_text(
        f"📚 **Платный курс** 📚\n\n"
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
    user_status[user_id] = statuses[2]
    del user_waiting_for_receipt[user_id]
    await context.bot.send_message(
        chat_id=user_id,
        text="Оплата подтверждена! Вам открыт доступ к платному курсу. 🎉",
    )

async def handle_my_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor == "evgeniy":
        user_scores = user_scores_evgeniy
    else:
        user_scores = user_scores_anastasiya

    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])
    caption = (
        f"👤 Ваш кабинет:\n\n"
        f"Статус: {status}\n"
        f"Баллы: {score}\n"
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
    if instructor == "evgeniy":
        user_scores = user_scores_evgeniy
    else:
        user_scores = user_scores_anastasiya

    score = user_scores.get(user_id, 0)
    caption = (
        f"💰 Как потратить баллы:\n\n"
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

# 4. Функция main – регистрация всех обработчиков
def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern="^(free_course|next_day)$"))
    application.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    application.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
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

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))

    print("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == "__main__":
    main()
