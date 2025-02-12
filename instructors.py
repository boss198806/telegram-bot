from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from common import user_data, statuses, main_menu, get_report_button_text, logger

async def start_free_course(msg, ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    instructor = ctx.user_data[user_id]['instructor']
    if not (ctx.user_data[user_id].get("gender") == "female" and ctx.user_data[user_id].get("program") == "home"):
        return await msg.reply_text("Пока в разработке 🚧", reply_markup=main_menu())
    
    day = user_data[instructor]['current_day'].get(user_id, 1)
    if day > 5:
        return await msg.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
    
    photos = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
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

async def handle_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data.setdefault(user_id, {})["gender"] = "male" if query.data == "gender_male" else "female"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
        [InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = ctx.user_data[user_id]['instructor']
    ctx.user_data[user_id]["program"] = "home" if query.data == "program_home" else "gym"
    user_data[instructor]['current_day'][user_id] = 1
    await start_free_course(query.message, ctx, user_id)

async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE, instructor_name: str):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data.setdefault(user_id, {})['instructor'] = instructor_name
    
    if instructor_name == 'evgeniy':
        await ctx.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://t.me/PRIVETSTVIEC/2",
            caption="🎥 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu()
        )
    elif instructor_name == 'anastasiya':
        await ctx.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="📸 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu()
        )
