from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

# Глобальные словари
user_scores = {}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}  # Для бесплатного и платного курсов
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
    return (("👩" if gender=="female" else "👨") + ("🏠" if prog=="home" else "🏋️") + " Отправить отчет 📹")

async def start_free_course(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    if not (ctx.user_data[user_id].get("gender")=="female" and ctx.user_data[user_id].get("program")=="home"):
        return await msg.reply_text("Пока в разработке 🚧", reply_markup=main_menu())
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
        1: ["1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
            "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
            "3️⃣ Велосипед 3x15 [Видео](https://t.me/c/2241417709/278/279)"],
        2: ["1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/c/2241417709/167/168)",
            "2️⃣ Лодочка прямые руки 3x30 [Видео](https://t.me/c/2241417709/395/396)",
            "3️⃣ Полные подъёмы корпуса 3x20 [Видео](https://t.me/c/2241417709/274/275)"],
        3: ["1️⃣ Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Махи в бок с колен 3x20 [Видео](https://t.me/c/2241417709/385/386)",
            "3️⃣ Косые с касанием пяток 3x15 [Видео](https://t.me/c/2241417709/282/283)"],
        4: ["1️⃣ Поочередные подъемы с гантелями 4x20 [Видео](https://t.me/c/2241417709/226/227)",
            "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
            "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)"],
        5: ["1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Махи под 45 с резинкой 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"],
    }
    exercises = course.get(day, [])
    text = f"🔥 **Бесплатный курс: День {day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день! 🎥"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(get_report_button_text(ctx, user_id), callback_data=f"send_report_day_{day}")]])
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
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день 🎥")

async def handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in user_waiting_for_video:
        data = user_waiting_for_video[user_id]
        if isinstance(data, tuple) and data[0] == "paid":
            paid_day = data[1]
            await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Платный видео-отчет от {user_name} (ID: {user_id}) за день {paid_day}.")
            await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
            user_scores[user_id] = user_scores.get(user_id, 0) + 30
            del user_waiting_for_video[user_id]
            if paid_day < 5:
                await update.message.reply_text(
                    f"Отчет за платный день {paid_day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.\nГотовы к следующему дню ({paid_day+1})? ➡️",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {paid_day+1}", callback_data="paid_next_day")]])
                )
            else:
                await update.message.reply_text(f"Поздравляем! Вы завершили платный курс! 🎉\nВаши баллы: {user_scores[user_id]}.", reply_markup=main_menu())
                ctx.user_data[user_id].pop("paid_current_day", None)
        elif isinstance(data, int):
            day = data
            await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {day}.")
            await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
            user_reports_sent.setdefault(user_id, {})[day] = True
            user_scores[user_id] += 60
            del user_waiting_for_video[user_id]
            if day < 5:
                ctx.user_data[user_id]["current_day"] += 1
                new_day = ctx.user_data[user_id]["current_day"]
                user_waiting_for_video[user_id] = new_day
                await update.message.reply_text(
                    f"Отчет за день {day} принят! 🎉\nВаши баллы: {user_scores[user_id]}.\nГотовы к следующему дню ({new_day})? ➡️",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {new_day}", callback_data="next_day")]])
                )
            else:
                user_status[user_id] = statuses[1]
                await update.message.reply_text(f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: {user_scores[user_id]}.", reply_markup=main_menu())
        else:
            await update.message.reply_text("Ошибка: неизвестный формат данных.")
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")

async def handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if not user_waiting_for_receipt.get(user_id) and not ctx.user_data.get(user_id, {}).get("paid_current_day"):
        return await update.message.reply_text("Я не жду чек от вас. Пожалуйста, выберите платный курс и отправьте чек. 🚧")
    if not update.message.photo:
        return await update.message.reply_text("Пожалуйста, отправьте фото чека 📸.")
    await ctx.bot.send_message(chat_id=GROUP_ID, text=f"🧾 Чек от {user_name} (ID: {user_id}). Подтвердите оплату.")
    photo_id = update.message.photo[-1].file_id
    await ctx.bot.send_photo(chat_id=GROUP_ID, photo=photo_id,
                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_payment_{user_id}")]]))
    await update.message.reply_text("Чек отправлен на проверку. Ожидайте подтверждения ⏳.")

async def confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[-1])
    user_status[user_id] = statuses[2]
    if user_id in user_waiting_for_receipt:
        del user_waiting_for_receipt[user_id]
    await ctx.bot.send_message(chat_id=user_id, text="✅ Оплата подтверждена! Вам открыт доступ к платному курсу. 🎉")
    if ctx.user_data[user_id].get("instructor") == "evgeniy":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨 Мужчина", callback_data="paid_gender_male")],
            [InlineKeyboardButton("👩 Женщина", callback_data="paid_gender_female")]
        ])
        await ctx.bot.send_message(chat_id=user_id, text="Пожалуйста, выберите ваш пол для платного курса:", reply_markup=kb)
    else:
        ctx.user_data[user_id]["paid_current_day"] = 1
        day1_ex = [
            "Махи назад с утяжелителями 3х25+5 https://t.me/c/2241417709/337/338",
            "Выпады 3х30 шагов х 2кг https://t.me/c/2241417709/157/158",
            "Разведение ног 3х20 https://t.me/c/2241417709/128/129",
            "Сведение ног 3х20 https://t.me/c/2241417709/126/127",
            "Сгибание ног 3х15 https://t.me/c/2241417709/130/131",
        ]
        txt_day1 = ("📚 **Платный курс: День 1** 📚\n\n" + "\n".join(day1_ex) + "\n\nОтправьте видео-отчет за день! 🎥")
        kb_day1 = InlineKeyboardMarkup([[InlineKeyboardButton("📹 Отправить отчет", callback_data="paid_video_day_1")]])
        await ctx.bot.send_message(chat_id=user_id, text=txt_day1, parse_mode="Markdown", reply_markup=kb_day1)

async def handle_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])
    text = f"👤 Ваш кабинет:\n\nСтатус: {status}\nБаллы: {score}\nПродолжайте тренироваться, чтобы улучшить статус и заработать больше баллов! 💪"
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true",
                                   caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Мой кабинет': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("👤 О тренере:\n\nКурочкин Евгений Витальевич\nОбщий тренировочный стаж - 20 лет\nСтаж работы - 15 лет\n"
            "МС - по становой тяге\nМС - по жиму штанги лежа\nСудья - федеральной категории\nОрганизатор соревнований\n"
            "КМС - по бодибилдингу\n\n20 лет в фитнесе! 💥")
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true",
                                   caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Обо мне': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = ("💡 Как заработать баллы:\n\n1️⃣ Проходите бесплатный курс и отправляйте видео-отчеты.\n"
            "2️⃣ Участвуйте в челленджах и отправляйте видео-отчеты.\n3️⃣ Приглашайте друзей и получайте баллы за их активность.\n"
            "4️⃣ Покупайте платный курс и получаете дополнительные баллы.")
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true",
                                   caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Как заработать баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    text = (f"💰 Как потратить баллы:\n\nУ вас есть {score} баллов.\n"
            "Вы можете потратить баллы на:\n- Скидку при покупке платного курса (1 балл = 2 рубля).\n"
            "- Максимальная скидка - 600 рублей.\n- Другие привилегии!")
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true",
                                   caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Как потратить баллы': {e}")
        await query.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("🏠 Главное меню", reply_markup=main_menu())

async def handle_nutrition_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍴 Купить меню питания за 300 баллов", callback_data="buy_nutrition_menu")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки:", reply_markup=kb)

async def handle_buy_nutrition_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        await query.message.reply_text("✅ Покупка меню питания успешно завершена!\nВот ваше меню питания: https://t.me/MENUKURO4KIN/2", reply_markup=main_menu())
    else:
        await query.message.reply_text("⚠️ Недостаточно баллов для покупки меню питания!")

async def handle_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    me = await ctx.bot.get_me()
    link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(f"🔗 Ваша реферальная ссылка:\n{link}\n\nПоделитесь ею с друзьями, и вы получите 100 баллов! 🎉")

async def handle_challenges(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_challenges.get(user_id):
        await send_challenge_task(query.message, user_id)
    elif user_scores.get(user_id, 0) >= 300:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Купить доступ за 300 баллов", callback_data="buy_challenge")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ])
        await query.message.reply_text("Доступ к челленджам стоит 300 баллов. Хотите приобрести?", reply_markup=kb)
    else:
        await query.message.reply_text(f"⚠️ Для доступа к челленджам нужно 300 баллов.\nУ вас: {user_scores.get(user_id, 0)} баллов.\nПродолжайте тренировки!")

async def buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id] = {"current_day": 1}
        await query.message.reply_text("✅ Доступ к челленджам открыт!", reply_markup=main_menu())
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("⚠️ Недостаточно баллов для покупки доступа!")

async def send_challenge_task(message, user_id: int):
    day = user_challenges[user_id]["current_day"]
    exercises = {
        1: ["1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
            "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"],
        2: ["1️⃣ Присед со штангой 30 раз [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Отжимания с отрывом рук 25 раз [Видео](https://t.me/c/2241417709/393/394)",
            "3️⃣ Полные подъёмы корпуса 30 раз [Видео](https://t.me/c/2241417709/274/275)"],
        3: ["1️⃣ Планка 3 мин [Видео](https://t.me/c/2241417709/286/296)",
            "2️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"],
        4: ["1️⃣ Выпады назад 60 раз [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
            "3️⃣ Велосипед 50 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"],
        5: ["1️⃣ Присед со штангой 50 раз [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
            "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)"],
    }.get(day, [])
    text = f"💪 **Челлендж: День {day}** 💪\n\n" + "\n".join(exercises)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Следующий день", callback_data="challenge_next")]]
                              if day < 5 else [[InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="back")]])
    await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in user_challenges:
        return await query.answer("Сначала купите челлендж! 🚧")
    day = user_challenges[user_id]["current_day"]
    if day < 5:
        user_challenges[user_id]["current_day"] = day + 1
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж! 🎉", reply_markup=main_menu())
        del user_challenges[user_id]
