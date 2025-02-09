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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# Глобальные словари
user_scores = {}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}             # Используется и для бесплатного, и для платного курсов
user_waiting_for_challenge_video = {}
user_waiting_for_receipt = {}
user_challenges = {}
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

def get_report_button_text(ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    gender = ctx.user_data[user_id].get("gender", "male")
    prog = ctx.user_data[user_id].get("program", "home")
    return ("👩" if gender=="female" else "👨") + ("🏠" if prog=="home" else "🏋️") + " Отправить отчет"

# --------------------- БЕСПЛАТНЫЙ КУРС ---------------------
async def start_free_course(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    if not (ctx.user_data[user_id].get("gender")=="female" and ctx.user_data[user_id].get("program")=="home"):
        return await msg.reply_text("Пока в разработке", reply_markup=main_menu())
    day = ctx.user_data[user_id].get("current_day", 1)
    if day > 5:
        return await msg.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
    photos = {
        1:"https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2:"https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3:"https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4:"https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5:"https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
    }
    course = {
        1: [
            "1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
            "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
            "3️⃣ Велосипед 3x15 [Видео](https://t.me/c/2241417709/278/279)",
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
            "1️⃣ Поочередные подъемы с гантелями 4x20 [Видео](https://t.me/c/2241417709/226/227)",
            "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
            "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)",
        ],
        5: [
            "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Махи под 45 с резинкой (можно без нее) 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
        ],
    }
    exercises = course.get(day, [])
    text = f"🔥 **Бесплатный курс: День {day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_report_button_text(ctx, user_id), callback_data=f"send_report_day_{day}")]
    ])
    try:
        await ctx.bot.send_photo(chat_id=msg.chat_id, photo=photos.get(day), caption=text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await msg.reply_text("Ошибка: изображение не найдено. Продолжайте без фото.", reply_markup=kb)

async def handle_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])
    if user_reports_sent.get(user_id, {}).get(day):
        return await query.message.reply_text(f"Вы уже отправили отчет за день {day}.")
    user_waiting_for_video[user_id] = day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")

# -------------- НОВАЯ ФУНКЦИЯ ДЛЯ ПЛАТНОГО ОТЧЁТА --------------
async def handle_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Обработка колбэка вида "paid_video_day_N".
    Устанавливаем, что ждём видео-отчет за платный день N и выводим сообщение.
    """
    query = update.callback_query
    user_id = query.from_user.id
    day_str = query.data.split("_")[-1]  # Например, "1"
    paid_day = int(day_str)
    user_waiting_for_video[user_id] = ("paid", paid_day)
    await query.message.reply_text(
        f"Пожалуйста, отправьте видео-отчет за платный день {paid_day}."
    )

# -------------- ОБРАБОТКА ВИДЕО (БЕСПЛАТНОЕ / ПЛАТНОЕ) --------------
async def handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in user_waiting_for_video:
        data = user_waiting_for_video[user_id]
        if isinstance(data, tuple) and data[0] == "paid":
            # Платный курс
            paid_day = data[1]
            await ctx.bot.send_message(
                chat_id=GROUP_ID,
                text=f"Платный видео-отчет от {user_name} (ID: {user_id}) за день {paid_day}."
            )
            await ctx.bot.send_video(
                chat_id=GROUP_ID,
                video=update.message.video.file_id
            )
            user_scores[user_id] = user_scores.get(user_id, 0) + 30
            del user_waiting_for_video[user_id]
            if paid_day < 5:
                await update.message.reply_text(
                    f"Отчет за платный день {paid_day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.\nГотовы к следующему дню ({paid_day+1})?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"➡️ День {paid_day+1}", callback_data="paid_next_day")]
                    ])
                )
            else:
                await update.message.reply_text(
                    f"Поздравляем! Вы завершили платный курс! 🎉\nВаши баллы: {user_scores[user_id]}.",
                    reply_markup=main_menu()
                )
                ctx.user_data[user_id].pop("paid_current_day", None)
        elif isinstance(data, int):
            # Бесплатный курс
            day = data
            await ctx.bot.send_message(
                chat_id=GROUP_ID,
                text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {day}."
            )
            await ctx.bot.send_video(
                chat_id=GROUP_ID,
                video=update.message.video.file_id
            )
            user_reports_sent.setdefault(user_id, {})[day] = True
            user_scores[user_id] += 60
            del user_waiting_for_video[user_id]
            if day < 5:
                ctx.user_data[user_id]["current_day"] += 1
                new_day = ctx.user_data[user_id]["current_day"]
                user_waiting_for_video[user_id] = new_day
                await update.message.reply_text(
                    f"Отчет за день {day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.\nГотовы к следующему дню ({new_day})?",
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
        else:
            await update.message.reply_text("Ошибка: неизвестный формат данных.")
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")

# --------------------- ЛОГИКА ПОЛ/ПРОГРАММА (БЕСПЛАТНОГО) ---------------------
async def handle_free_course_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "free_course" and ("gender" not in ctx.user_data[user_id] or "program" not in ctx.user_data[user_id]):
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Мужчина", callback_data="gender_male"),
             InlineKeyboardButton("Женщина", callback_data="gender_female")]
        ])
        return await query.message.reply_text("Ваш пол:", reply_markup=kb)
    await start_free_course(query.message, ctx, user_id)

async def handle_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["gender"] = "male" if query.data=="gender_male" else "female"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["program"] = "home" if query.data=="program_home" else "gym"
    ctx.user_data[user_id]["current_day"] = 1
    await start_free_course(query.message, ctx, user_id)

# --------------------- /start, Выбор инструктора ---------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if ctx.args:
            try:
                ref = int(ctx.args[0])
                if ref != user_id:
                    user_scores[ref] = user_scores.get(ref, 0) + 100
                    try:
                        await ctx.bot.send_message(
                            chat_id=ref,
                            text="Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!"
                        )
                    except Exception as e:
                        logger.error(f"Реферальный бонус: {e}")
            except ValueError:
                pass
        ctx.user_data.setdefault(user_id, {"current_day": 1})
        user_scores[user_id] = user_scores.get(user_id, 0)
        user_status[user_id] = user_status.get(user_id, statuses[0])
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Евгений Курочкин", callback_data="instructor_1")],
            [InlineKeyboardButton("АНАСТАСИЯ", callback_data="instructor_2")],
            [InlineKeyboardButton("Тренер 3", callback_data="instructor_3")],
            [InlineKeyboardButton("Тренер 4", callback_data="instructor_4")],
            [InlineKeyboardButton("Тренер 5", callback_data="instructor_5")],
        ])
        await ctx.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери для себя фитнес инструктора:",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()
    if data == "instructor_1":
        ctx.user_data[user_id]["instructor"] = "evgeniy"
        await ctx.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://t.me/PRIVETSTVIEC/2",
            supports_streaming=True,
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu()
        )
    elif data == "instructor_2":
        ctx.user_data[user_id]["instructor"] = "anastasiya"
        await query.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ")
        await ctx.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu()
        )
    else:
        sel = "неизвестный тренер"
        if data=="instructor_3":
            sel = "Тренер 3"
        elif data=="instructor_4":
            sel = "Тренер 4"
        elif data=="instructor_5":
            sel = "Тренер 5"
        await query.message.edit_text(
            f"Вы выбрали тренера: {sel}. Функционал пока не реализован.\nВы будете перенаправлены в главное меню.",
            reply_markup=main_menu()
        )

# --------------------- Меню питания, рефералка, челленджи и т.п. ---------------------
async def handle_nutrition_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Купить меню питания за 300 баллов", callback_data="buy_nutrition_menu")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки:", reply_markup=kb)

async def handle_buy_nutrition_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        await query.message.reply_text(
            "Покупка меню питания успешно завершена!\nВот ваше меню питания: https://t.me/MENUKURO4KIN/2",
            reply_markup=main_menu()
        )
    else:
        await query.message.reply_text("Недостаточно баллов для покупки меню питания!")

async def handle_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await ctx.bot.get_me()
    link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(
        f"Ваша реферальная ссылка:\n{link}\n\nПоделитесь ею с друзьями, и вы получите 100 баллов!"
    )

# --------------------- Челленджи ---------------------
async def handle_challenges(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_challenges.get(user_id):
        await send_challenge_task(query.message, user_id)
    elif user_scores.get(user_id, 0) >= 300:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Купить доступ за 300 баллов", callback_data="buy_challenge")],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ])
        await query.message.reply_text(
            "Доступ к челленджам стоит 300 баллов. Хотите приобрести?",
            reply_markup=kb
        )
    else:
        await query.message.reply_text(
            f"Для доступа к челленджам нужно 300 баллов.\nУ вас: {user_scores.get(user_id, 0)} баллов.\nПродолжайте тренировки!"
        )

async def buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id] = {"current_day": 1}
        await query.message.reply_text("✅ Доступ к челленджам открыт!")
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("Недостаточно баллов для покупки доступа!")

async def send_challenge_task(message, user_id: int):
    day = user_challenges[user_id]["current_day"]
    exercises = {
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
    }.get(day, [])
    text = f"💪 **Челлендж: День {day}** 💪\n\n" + "\n".join(exercises)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Следующий день", callback_data="challenge_next")]]
                              if day < 5 else [[InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="back")]])
    await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in user_challenges:
        return await query.answer("Сначала купите челлендж!")
    day = user_challenges[user_id]["current_day"]
    if day < 5:
        user_challenges[user_id]["current_day"] = day + 1
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж!", reply_markup=main_menu())
        del user_challenges[user_id]

# --------------------- ПЛАТНЫЙ КУРС ---------------------
async def handle_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Показываем стоимость, скидку и кнопку 'Отправить чек'."""
    query = update.callback_query
    user_id = query.from_user.id
    discount = min(user_scores.get(user_id, 0) * 2, 600)
    price = 2000 - discount
    await query.message.reply_text(
        f"📚 **Платный курс** 📚\n\n"
        f"Стоимость курса: 2000 рублей.\n"
        f"Ваша скидка: {discount} рублей.\n"
        f"Итоговая сумма: {price} рублей.\n\n"
        f"Переведите сумму на карту: 89236950304 (Яндекс Банк).\n"
        f"После оплаты отправьте чек для проверки.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Отправить чек", callback_data="send_receipt")]
        ])
    )
    user_waiting_for_receipt[user_id] = True

async def handle_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Пользователь нажал «Отправить чек»."""
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt[user_id] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате.")

async def handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """При получении фото чека – отправляем его в группу с кнопкой подтверждения."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id not in user_waiting_for_receipt:
        return await update.message.reply_text(
            "Я не жду чек от вас. Пожалуйста, выберите платный курс и отправьте чек."
        )
    if not update.message.photo:
        return await update.message.reply_text("Пожалуйста, отправьте фото чека.")
    await ctx.bot.send_message(
        chat_id=GROUP_ID,
        text=f"Чек от {user_name} (ID: {user_id}). Подтвердите оплату."
    )
    photo_id = update.message.photo[-1].file_id
    await ctx.bot.send_photo(
        chat_id=GROUP_ID,
        photo=photo_id,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Подтвердить", callback_data=f"confirm_payment_{user_id}")]
        ])
    )
    await update.message.reply_text("Чек отправлен на проверку. Ожидайте подтверждения.")

async def confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Подтверждаем оплату и выдаем доступ к платному курсу с 1 дня.
    Если инструктор – Евгений Курочкин, вместо мгновенной отправки программы выводим меню выбора пола;
    иначе отправляем программу сразу.
    """
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[-1])
    user_status[user_id] = statuses[2]  # Например, 'Чемпион'
    if user_id in user_waiting_for_receipt:
        del user_waiting_for_receipt[user_id]
    await ctx.bot.send_message(
        chat_id=user_id,
        text="Оплата подтверждена! Вам открыт доступ к платному курсу. 🎉"
    )
    # Если выбран инструктор Евгений, выводим меню выбора пола; иначе, сразу запускаем курс
    if ctx.user_data[user_id].get("instructor") == "evgeniy":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Мужчина", callback_data="paid_gender_male"),
             InlineKeyboardButton("Женщина", callback_data="paid_gender_female")]
        ])
        await ctx.bot.send_message(
            chat_id=user_id,
            text="Пожалуйста, выберите ваш пол для платного курса:",
            reply_markup=kb
        )
    else:
        ctx.user_data[user_id]["paid_current_day"] = 1
        day1_ex = [
            "Махи назад с утяжелителями 3х25+5 https://t.me/c/2241417709/337/338",
            "Выпады 3х30 шагов х 2кг https://t.me/c/2241417709/157/158",
            "Разведение ног 3х20 https://t.me/c/2241417709/128/129",
            "Сведение ног 3х20 https://t.me/c/2241417709/126/127",
            "Сгибание ног 3х15 https://t.me/c/2241417709/130/131",
        ]
        txt_day1 = ("📚 **Платный курс: День 1** 📚\n\n" + "\n".join(day1_ex)
                    + "\n\nОтправьте видео-отчет за день!")
        kb_day1 = InlineKeyboardMarkup([
            [InlineKeyboardButton("Отправить отчет", callback_data="paid_video_day_1")]
        ])
        await ctx.bot.send_message(
            chat_id=user_id,
            text=txt_day1,
            parse_mode="Markdown",
            reply_markup=kb_day1
        )

# --------------------- ОБРАБОТКА ВЫБОРА ПОЛА И ПРОГРАММЫ ДЛЯ ПЛАТНОГО КУРСА (ТОЛЬКО ДЛЯ EVGENIY) ---------------------
async def handle_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "paid_gender_male":
        await query.message.reply_text("В разработке")
    elif query.data == "paid_gender_female":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("В зале", callback_data="paid_program_gym"),
             InlineKeyboardButton("Дома", callback_data="paid_program_home")]
        ])
        await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_paid_program_gym(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["paid_current_day"] = 1
    day1_ex = [
        "Махи назад с утяжелителями 3х25+5 https://t.me/c/2241417709/337/338",
        "Выпады 3х30 шагов х 2кг https://t.me/c/2241417709/157/158",
        "Разведение ног 3х20 https://t.me/c/2241417709/128/129",
        "Сведение ног 3х20 https://t.me/c/2241417709/126/127",
        "Сгибание ног 3х15 https://t.me/c/2241417709/130/131",
    ]
    txt_day1 = ("📚 **Платный курс: День 1** 📚\n\n" + "\n".join(day1_ex)
                + "\n\nОтправьте видео-отчет за день!")
    kb_day1 = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data="paid_video_day_1")]
    ])
    await ctx.bot.send_message(
        chat_id=user_id,
        text=txt_day1,
        parse_mode="Markdown",
        reply_markup=kb_day1
    )

async def handle_paid_program_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке")

# --------------------- Обработчик "paid_video_day_X" ---------------------
async def handle_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """При нажатии на кнопку для платного отчета (например, 'paid_video_day_1')."""
    query = update.callback_query
    user_id = query.from_user.id
    day_str = query.data.split("_")[-1]
    paid_day = int(day_str)
    user_waiting_for_video[user_id] = ("paid", paid_day)
    await query.message.reply_text(
        f"Пожалуйста, отправьте видео-отчет за платный день {paid_day}."
    )

# --------------------- Обработчик "paid_next_day" ---------------------
async def handle_paid_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    paid_day = ctx.user_data[user_id].get("paid_current_day", 1)
    if paid_day < 5:
        next_day = paid_day + 1
        ctx.user_data[user_id]["paid_current_day"] = next_day
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
        ex = paid_program[next_day]
        text = f"📚 **Платный курс: День {next_day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день!"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Отправить отчет", callback_data=f"paid_video_day_{next_day}")]
        ])
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await query.message.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=main_menu())
        ctx.user_data[user_id].pop("paid_current_day", None)

# --------------------- Остальной функционал ---------------------
async def handle_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])
    text = (
        f"👤 Ваш кабинет:\n\n"
        f"Статус: {status}\n"
        f"Баллы: {score}\n"
        "Продолжайте тренироваться, чтобы улучшить статус и заработать больше баллов!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Мой кабинет': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        "20 лет в фитнесе!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Обо мне': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "💡 Как заработать баллы:\n\n"
        "1. Проходите бесплатный курс и отправляйте видео-отчеты.\n"
        "2. Участвуйте в челленджах и отправляйте видео-отчеты.\n"
        "3. Приглашайте друзей и получайте баллы за их активность.\n"
        "4. Покупайте платный курс и получаете дополнительные баллы."
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как заработать баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    text = (
        f"💰 Как потратить баллы:\n\nУ вас есть {score} баллов.\n"
        "Вы можете потратить баллы на:\n"
        "- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
        "- Максимальная скидка - 600 рублей.\n"
        "- Другие привилегии!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как потратить баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню", reply_markup=main_menu())

# --------------------- ОБРАБОТКА ВЫБОРА ПОЛА И ПРОГРАММЫ ДЛЯ ПЛАТНОГО КУРСА (ТОЛЬКО ДЛЯ EVGENIY) ---------------------
async def handle_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "paid_gender_male":
        await query.message.reply_text("В разработке")
    elif query.data == "paid_gender_female":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("В зале", callback_data="paid_program_gym"),
             InlineKeyboardButton("Дома", callback_data="paid_program_home")]
        ])
        await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_paid_program_gym(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["paid_current_day"] = 1
    day1_ex = [
        "Махи назад с утяжелителями 3х25+5 https://t.me/c/2241417709/337/338",
        "Выпады 3х30 шагов х 2кг https://t.me/c/2241417709/157/158",
        "Разведение ног 3х20 https://t.me/c/2241417709/128/129",
        "Сведение ног 3х20 https://t.me/c/2241417709/126/127",
        "Сгибание ног 3х15 https://t.me/c/2241417709/130/131",
    ]
    txt_day1 = ("📚 **Платный курс: День 1** 📚\n\n" + "\n".join(day1_ex)
                + "\n\nОтправьте видео-отчет за день!")
    kb_day1 = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data="paid_video_day_1")]
    ])
    await ctx.bot.send_message(
        chat_id=user_id,
        text=txt_day1,
        parse_mode="Markdown",
        reply_markup=kb_day1
    )

async def handle_paid_program_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке")

# --------------------- Обработчик "paid_video_day_X" ---------------------
async def handle_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """При нажатии на кнопку для платного отчета (например, 'paid_video_day_1')."""
    query = update.callback_query
    user_id = query.from_user.id
    day_str = query.data.split("_")[-1]
    paid_day = int(day_str)
    user_waiting_for_video[user_id] = ("paid", paid_day)
    await query.message.reply_text(
        f"Пожалуйста, отправьте видео-отчет за платный день {paid_day}."
    )

# --------------------- Обработчик "paid_next_day" ---------------------
async def handle_paid_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    paid_day = ctx.user_data[user_id].get("paid_current_day", 1)
    if paid_day < 5:
        next_day = paid_day + 1
        ctx.user_data[user_id]["paid_current_day"] = next_day
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
        ex = paid_program[next_day]
        text = f"📚 **Платный курс: День {next_day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день!"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Отправить отчет", callback_data=f"paid_video_day_{next_day}")]
        ])
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await query.message.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=main_menu())
        ctx.user_data[user_id].pop("paid_current_day", None)

# --------------------- Остальной функционал ---------------------
async def handle_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])
    text = (
        f"👤 Ваш кабинет:\n\n"
        f"Статус: {status}\n"
        f"Баллы: {score}\n"
        "Продолжайте тренироваться, чтобы улучшить статус и заработать больше баллов!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Мой кабинет': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        "20 лет в фитнесе!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Обо мне': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "💡 Как заработать баллы:\n\n"
        "1. Проходите бесплатный курс и отправляйте видео-отчеты.\n"
        "2. Участвуйте в челленджах и отправляйте видео-отчеты.\n"
        "3. Приглашайте друзей и получайте баллы за их активность.\n"
        "4. Покупайте платный курс и получаете дополнительные баллы."
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как заработать баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    text = (
        f"💰 Как потратить баллы:\n\nУ вас есть {score} баллов.\n"
        "Вы можете потратить баллы на:\n"
        "- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
        "- Максимальная скидка - 600 рублей.\n"
        "- Другие привилегии!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как потратить баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню", reply_markup=main_menu())

# --------------------- ОБРАБОТКА ВЫБОРА ПОЛА И ПРОГРАММЫ ДЛЯ ПЛАТНОГО КУРСА (ТОЛЬКО ДЛЯ EVGENIY) ---------------------
async def handle_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "paid_gender_male":
        await query.message.reply_text("В разработке")
    elif query.data == "paid_gender_female":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("В зале", callback_data="paid_program_gym"),
             InlineKeyboardButton("Дома", callback_data="paid_program_home")]
        ])
        await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_paid_program_gym(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["paid_current_day"] = 1
    day1_ex = [
        "Махи назад с утяжелителями 3х25+5 https://t.me/c/2241417709/337/338",
        "Выпады 3х30 шагов х 2кг https://t.me/c/2241417709/157/158",
        "Разведение ног 3х20 https://t.me/c/2241417709/128/129",
        "Сведение ног 3х20 https://t.me/c/2241417709/126/127",
        "Сгибание ног 3х15 https://t.me/c/2241417709/130/131",
    ]
    txt_day1 = ("📚 **Платный курс: День 1** 📚\n\n" + "\n".join(day1_ex)
                + "\n\nОтправьте видео-отчет за день!")
    kb_day1 = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить отчет", callback_data="paid_video_day_1")]
    ])
    await ctx.bot.send_message(
        chat_id=user_id,
        text=txt_day1,
        parse_mode="Markdown",
        reply_markup=kb_day1
    )

async def handle_paid_program_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке")

# --------------------- Обработчик "paid_video_day_X" ---------------------
async def handle_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """При нажатии на кнопку для платного отчета (например, 'paid_video_day_1')."""
    query = update.callback_query
    user_id = query.from_user.id
    day_str = query.data.split("_")[-1]
    paid_day = int(day_str)
    user_waiting_for_video[user_id] = ("paid", paid_day)
    await query.message.reply_text(
        f"Пожалуйста, отправьте видео-отчет за платный день {paid_day}."
    )

# --------------------- Обработчик "paid_next_day" ---------------------
async def handle_paid_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    paid_day = ctx.user_data[user_id].get("paid_current_day", 1)
    if paid_day < 5:
        next_day = paid_day + 1
        ctx.user_data[user_id]["paid_current_day"] = next_day
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
        ex = paid_program[next_day]
        text = f"📚 **Платный курс: День {next_day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день!"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Отправить отчет", callback_data=f"paid_video_day_{next_day}")]
        ])
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await query.message.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=main_menu())
        ctx.user_data[user_id].pop("paid_current_day", None)

# --------------------- Остальной функционал ---------------------
async def handle_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])
    text = (
        f"👤 Ваш кабинет:\n\n"
        f"Статус: {status}\n"
        f"Баллы: {score}\n"
        "Продолжайте тренироваться, чтобы улучшить статус и заработать больше баллов!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Мой кабинет': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        "20 лет в фитнесе!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Обо мне': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "💡 Как заработать баллы:\n\n"
        "1. Проходите бесплатный курс и отправляйте видео-отчеты.\n"
        "2. Участвуйте в челленджах и отправляйте видео-отчеты.\n"
        "3. Приглашайте друзей и получайте баллы за их активность.\n"
        "4. Покупайте платный курс и получаете дополнительные баллы."
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как заработать баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    text = (
        f"💰 Как потратить баллы:\n\nУ вас есть {score} баллов.\n"
        "Вы можете потратить баллы на:\n"
        "- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
        "- Максимальная скидка - 600 рублей.\n"
        "- Другие привилегии!"
    )
    try:
        await ctx.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
            caption=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Ошибка для 'Как потратить баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("Главное меню", reply_markup=main_menu())

# --------------------- MAIN ---------------------
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
    # Обработчики для выбора пола и программы для платного курса (только для Евгения)
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

    # Видео и Фото
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))

    print("Бот запущен и готов к работе.")
    app.run_polling()

if __name__ == "__main__":
    main()
