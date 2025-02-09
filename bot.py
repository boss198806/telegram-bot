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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# Глобальные словари и константы
user_scores = {}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}
user_waiting_for_challenge_video = {}
user_waiting_for_receipt = {}
user_challenges = {}
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Программа бесплатного курса
free_course = {
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
        "1️⃣ Поочередные подъемы с гантелями 4x20 [Видео](https://t.me/c/2241417709/226/227)",
        "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
        "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)",
    ],
    5: [
        "1️⃣ Присед со штангой 3x20 [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Махи под 45 с резинкой 3x20 [Видео](https://t.me/c/2241417709/339/340)",
        "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)",
    ],
}
free_photos = {
    1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
    2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
    3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
    4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
    5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
}

# Программа платного курса для Евгения Курочкина (ваши данные)
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
}

# Основное меню
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
        [InlineKeyboardButton("Подсчет КБЖУ", callback_data="kbju_calc")],
    ])

def get_report_button_text(ctx: ContextTypes.DEFAULT_TYPE, uid: int):
    gender = ctx.user_data[uid].get("gender", "male")
    prog = ctx.user_data[uid].get("program", "home")
    return ("👩" if gender == "female" else "👨") + ("🏠" if prog == "home" else "🏋️") + " Отправить отчет"

# 1. Бесплатный курс
async def start_free_course(msg, ctx: ContextTypes.DEFAULT_TYPE, uid: int):
    if not (ctx.user_data[uid].get("gender") == "female" and ctx.user_data[uid].get("program") == "home"):
        return await msg.reply_text("Пока в разработке", reply_markup=main_menu())
    day = ctx.user_data[uid].get("current_day", 1)
    if day > 5:
        return await msg.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
    ex = free_course.get(day, [])
    text = f"🔥 **Бесплатный курс: День {day}** 🔥\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день!"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(get_report_button_text(ctx, uid), callback_data=f"send_report_day_{day}")]])
    try:
        await ctx.bot.send_photo(chat_id=msg.chat_id, photo=free_photos.get(day), caption=text, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        await msg.reply_text("Ошибка: изображение не найдено. Продолжайте без фото.", reply_markup=kb)

async def handle_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    day = int(q.data.split("_")[-1])
    if user_reports_sent.get(uid, {}).get(day):
        return await q.message.reply_text(f"Вы уже отправили отчет за день {day}.")
    user_waiting_for_video[uid] = day
    await q.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")

async def handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    uname = update.message.from_user.first_name
    if uid in user_waiting_for_video:
        day = user_waiting_for_video[uid]
        await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Видео-отчет от {uname} (ID: {uid}) за день {day}.")
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
        user_reports_sent.setdefault(uid, {})[day] = True
        user_scores[uid] = user_scores.get(uid, 0) + 60
        del user_waiting_for_video[uid]
        if day < 5:
            ctx.user_data[uid]["current_day"] = day + 1
            user_waiting_for_video[uid] = day + 1
            await update.message.reply_text(
                f"Отчет за день {day} принят! 🎉\nВаши баллы: {user_scores[uid]}.\nГотовы к следующему дню ({day+1})?",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {day+1}", callback_data="next_day")]])
            )
        else:
            user_status[uid] = statuses[1]
            await update.message.reply_text(f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: {user_scores[uid]}.", reply_markup=main_menu())
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")

# 2. Обработчики пола/программы для бесплатного курса
async def handle_free_course_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    if q.data == "free_course" and ("gender" not in ctx.user_data[uid] or "program" not in ctx.user_data[uid]):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Мужчина", callback_data="gender_male"),
                                      InlineKeyboardButton("Женщина", callback_data="gender_female")]])
        return await q.message.reply_text("Ваш пол:", reply_markup=kb)
    await start_free_course(q.message, ctx, uid)

async def handle_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    ctx.user_data[uid]["gender"] = "male" if q.data == "gender_male" else "female"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
                                  InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]])
    await q.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    ctx.user_data[uid]["program"] = "home" if q.data == "program_home" else "gym"
    ctx.user_data[uid]["current_day"] = 1
    await start_free_course(q.message, ctx, uid)

# 3. /start и выбор инструктора
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        if ctx.args:
            try:
                ref = int(ctx.args[0])
                if ref != uid:
                    user_scores[ref] = user_scores.get(ref, 0) + 100
                    try:
                        await ctx.bot.send_message(chat_id=ref, text="Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!")
                    except Exception as e:
                        logger.error(f"Реферальный бонус: {e}")
            except ValueError:
                pass
        ctx.user_data.setdefault(uid, {"current_day": 1})
        user_scores[uid] = user_scores.get(uid, 0)
        user_status[uid] = user_status.get(uid, statuses[0])
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Евгений Курочкин", callback_data="instructor_1")],
            [InlineKeyboardButton("АНАСТАСИЯ", callback_data="instructor_2")],
            [InlineKeyboardButton("Тренер 3", callback_data="instructor_3")],
            [InlineKeyboardButton("Тренер 4", callback_data="instructor_4")],
            [InlineKeyboardButton("Тренер 5", callback_data="instructor_5")],
        ])
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Выбери для себя фитнес инструктора:", reply_markup=kb)
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    uid = q.from_user.id
    logger.info(f"Instructor selection received: {data} from user {uid}")
    await q.answer()
    if data == "instructor_1":
        ctx.user_data[uid]["instructor"] = "evgeniy"
        # Просто выводим сообщение и основное меню, не переключая курс автоматически
        await q.message.edit_text("Вы выбрали тренера: Евгений Курочкин", reply_markup=main_menu())
    elif data == "instructor_2":
        ctx.user_data[uid]["instructor"] = "anastasiya"
        await q.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ")
        await ctx.bot.send_photo(
            chat_id=q.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu()
        )
    else:
        sel = "неизвестный тренер"
        if data == "instructor_3":
            sel = "Тренер 3"
        elif data == "instructor_4":
            sel = "Тренер 4"
        elif data == "instructor_5":
            sel = "Тренер 5"
        await q.message.edit_text(f"Вы выбрали тренера: {sel}. Функционал пока не реализован.\nВы будете перенаправлены в главное меню.", reply_markup=main_menu())

# 4. Функционал КБЖУ (без изменений)
async def handle_kbju_calc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not ctx.user_data.get("kbju_purchased"):
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Купить за 300 баллов", callback_data="buy_kbju")],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ])
        await q.message.reply_text("Для доступа к подсчету КБЖУ требуется 300 баллов. Хотите приобрести?", reply_markup=kb)
    else:
        await start_kbju_flow(q.message, ctx, q.from_user.id)

async def handle_buy_kbju(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    if user_scores.get(uid, 0) >= 300:
        user_scores[uid] -= 300
        ctx.user_data["kbju_purchased"] = True
        await q.message.reply_text("Подсчет КБЖУ приобретен!")
        await start_kbju_flow(q.message, ctx, uid)
    else:
        await q.message.reply_text("Недостаточно баллов для покупки подсчета КБЖУ.")

async def start_kbju_flow(msg, ctx: ContextTypes.DEFAULT_TYPE, uid: int):
    ctx.user_data.setdefault("kbju", {})
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Мужской", callback_data="kbju_gender_male"),
         InlineKeyboardButton("Женский", callback_data="kbju_gender_female")]
    ])
    await msg.reply_text("Выберите ваш пол:", reply_markup=kb)

async def handle_kbju_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    gender = "male" if q.data == "kbju_gender_male" else "female"
    ctx.user_data.setdefault("kbju", {})["gender"] = gender
    ctx.user_data["kbju_step"] = "age"
    await q.message.reply_text("Введите ваш возраст (в годах):")

async def process_kbju_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if "kbju_step" not in ctx.user_data:
        return
    step = ctx.user_data["kbju_step"]
    try:
        val = float(update.message.text)
    except ValueError:
        return await update.message.reply_text("Введите корректное число.")
    if step == "age":
        ctx.user_data.setdefault("kbju", {})["age"] = val
        ctx.user_data["kbju_step"] = "height"
        await update.message.reply_text("Введите ваш рост (в см):")
    elif step == "height":
        ctx.user_data.setdefault("kbju", {})["height"] = val
        ctx.user_data["kbju_step"] = "activity"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Малая", callback_data="kbju_activity_low"),
             InlineKeyboardButton("Средняя", callback_data="kbju_activity_medium"),
             InlineKeyboardButton("Высокая", callback_data="kbju_activity_high")]
        ])
        await update.message.reply_text("Выберите уровень активности:", reply_markup=kb)
    elif step == "weight":
        ctx.user_data.setdefault("kbju", {})["weight"] = val
        ctx.user_data["kbju_step"] = "goal"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Поддерживать", callback_data="kbju_goal_maintain"),
             InlineKeyboardButton("Похудеть", callback_data="kbju_goal_lose"),
             InlineKeyboardButton("Набрать", callback_data="kbju_goal_gain")]
        ])
        await update.message.reply_text("Выберите вашу цель:", reply_markup=kb)

async def handle_kbju_activity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    act = q.data.split("_")[-1]
    ctx.user_data.setdefault("kbju", {})["activity"] = act
    ctx.user_data["kbju_step"] = "weight"
    await q.message.reply_text("Введите ваш вес (в кг):")

async def handle_kbju_goal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    goal = q.data.split("_")[-1]
    ctx.user_data.setdefault("kbju", {})["goal"] = goal
    kbju = ctx.user_data.get("kbju", {})
    try:
        gender = kbju["gender"]
        age = float(kbju["age"])
        height = float(kbju["height"])
        weight = float(kbju["weight"])
        act = kbju["activity"]
        goal = kbju["goal"]
    except KeyError:
        return await q.message.reply_text("Ошибка: недостаточно данных для расчета.")
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    if act == "low":
        mult = 1.2
    elif act == "medium":
        mult = 1.55
    elif act == "high":
        mult = 1.9
    else:
        mult = 1.2
    cal = bmr * mult
    if goal == "lose":
        cal -= 500
    elif goal == "gain":
        cal += 500
    prot = (cal * 0.3) / 4
    fat = (cal * 0.25) / 9
    carb = (cal * 0.45) / 4
    res = f"Ваш расчет КБЖУ:\nКалорий: {cal:.0f} ккал\nБелков: {prot:.0f} г\nЖиров: {fat:.0f} г\nУглеводов: {carb:.0f} г"
    await q.message.reply_text(res, reply_markup=main_menu())
    ctx.user_data.pop("kbju_step", None)
    ctx.user_data.pop("kbju", None)

# 4. Обработчики платного курса для Евгения Курочкина
async def start_paid_course(msg, ctx: ContextTypes.DEFAULT_TYPE, uid: int):
    day = ctx.user_data[uid].get("paid_current_day", 1)
    if day > 5:
        return await msg.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=main_menu())
    ex = paid_program.get(day, [])
    text = f"📚 **Платный курс: День {day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте чек (фото) оплаты."
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Отправить чек", callback_data=f"send_paid_receipt_day_{day}")]])
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_send_paid_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    day = int(q.data.split("_")[-1])
    ctx.user_data.setdefault(uid, {})["waiting_for_paid_receipt"] = True
    await q.message.reply_text("Пожалуйста, отправьте фото чека об оплате.")

async def handle_paid_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    day = ctx.user_data[uid].get("paid_current_day", 1)
    if day < 5:
        ctx.user_data[uid]["paid_current_day"] = day + 1
        await start_paid_course(q.message, ctx, uid)
    else:
        await q.message.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=main_menu())
        ctx.user_data[uid].pop("paid_current_day", None)

# Обработка фото для платного курса
async def handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if ctx.user_data.get(uid, {}).get("waiting_for_paid_receipt"):
        await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Чек (оплата) от пользователя (ID: {uid}). Подтвердите оплату.")
        photo_id = update.message.photo[-1].file_id
        await ctx.bot.send_photo(
            chat_id=GROUP_ID,
            photo=photo_id,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Подтвердить", callback_data=r"^confirm_payment_(\d+)$")]])
        )
        await update.message.reply_text("Чек отправлен на проверку. Ожидайте подтверждения.")
        ctx.user_data[uid].pop("waiting_for_paid_receipt", None)
        return
    await update.message.reply_text("Этот тип фото не ожидается в текущем режиме.")

async def confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = int(q.data.split("_")[-1])
    user_status[uid] = statuses[2]  # Оплата подтверждена
    del user_waiting_for_receipt[uid]
    await ctx.bot.send_message(chat_id=uid, text="Оплата подтверждена! Вам открыт доступ к платному курсу. 🎉")
    # Если это платный курс, отправляем первый день тренировки
    if ctx.user_data.get(uid, {}).get("paid_course"):
        ctx.user_data[uid]["paid_current_day"] = 1
        await start_paid_course(q.message, ctx, uid)

async def handle_paid_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    uname = update.message.from_user.first_name
    day = ctx.user_data[uid].get("paid_current_day")
    if day:
        await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Платный видео-отчет от {uname} (ID: {uid}) за день {day}.")
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
        user_scores[uid] = user_scores.get(uid, 0) + 30
        ctx.user_data[uid]["paid_current_day"] = day + 1
        if day < 5:
            await update.message.reply_text(
                f"Отчет за день {day} принят! 🎉\nВаши баллы: {user_scores[uid]}.\nГотовы к следующему дню ({day+1})?",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {day+1}", callback_data="paid_next_day")]])
            )
        else:
            await update.message.reply_text(f"Поздравляем! Вы завершили платный курс! 🎉\nВаши баллы: {user_scores[uid]}.", reply_markup=main_menu())
            ctx.user_data[uid].pop("paid_current_day", None)
    else:
        await update.message.reply_text("Я не жду видео для платного курса.")

async def handle_video_dispatch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if "paid_current_day" in ctx.user_data.get(uid, {}):
        await handle_paid_video(update, ctx)
    else:
        await handle_video(update, ctx)

async def handle_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.message.reply_text("Главное меню", reply_markup=main_menu())

# 5. Остальной функционал (КБЖУ, Мой кабинет, Обо мне, как заработать/потратить баллы)
async def handle_earn_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    text = ("💡 Как заработать баллы:\n\n1. Проходите бесплатный курс и отправляйте видео-отчеты.\n2. Участвуйте в челленджах и отправляйте видео-отчеты.\n"
            "3. Приглашайте друзей и получайте баллы за их активность.\n4. Покупайте платный курс и получаете дополнительные баллы.")
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id, photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG?raw=true", caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Как заработать баллы': {e}")
        await q.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    score = user_scores.get(uid, 0)
    text = (f"💰 Как потратить баллы:\n\nУ вас есть {score} баллов.\nВы можете потратить баллы на:\n"
            "- Скидку при покупке платного курса (1 балл = 2 рубля).\n- Максимальная скидка - 600 рублей.\n- Другие привилегии!")
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id, photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG?raw=true", caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Как потратить баллы': {e}")
        await q.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    score = user_scores.get(uid, 0)
    stat = user_status.get(uid, statuses[0])
    text = f"👤 Ваш кабинет:\n\nСтатус: {stat}\nБаллы: {score}\nПродолжайте тренироваться, чтобы улучшить статус и заработать больше баллов!"
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id, photo="https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG?raw=true", caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Мой кабинет': {e}")
        await q.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

async def handle_about_me(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    text = ("👤 О тренере:\n\nКурочкин Евгений Витальевич\nОбщий тренировочный стаж - 20 лет\nСтаж работы - 15 лет\n"
            "МС - по становой тяге\nМС - по жиму штанги лежа\nСудья - федеральной категории\nОрганизатор соревнований\n"
            "КМС - по бодибилдингу\n\n20 лет в фитнесе!")
    try:
        await ctx.bot.send_photo(chat_id=update.effective_chat.id, photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg?raw=true", caption=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка для 'Обо мне': {e}")
        await q.message.reply_text("Ошибка при загрузке фото. Попробуйте позже.")

# Функция для обработки текстовых сообщений для КБЖУ
async def process_kbju_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if "kbju_step" not in ctx.user_data:
        return
    step = ctx.user_data["kbju_step"]
    try:
        val = float(update.message.text)
    except ValueError:
        return await update.message.reply_text("Введите корректное число.")
    if step == "age":
        ctx.user_data.setdefault("kbju", {})["age"] = val
        ctx.user_data["kbju_step"] = "height"
        await update.message.reply_text("Введите ваш рост (в см):")
    elif step == "height":
        ctx.user_data.setdefault("kbju", {})["height"] = val
        ctx.user_data["kbju_step"] = "activity"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Малая", callback_data="kbju_activity_low"),
             InlineKeyboardButton("Средняя", callback_data="kbju_activity_medium"),
             InlineKeyboardButton("Высокая", callback_data="kbju_activity_high")]
        ])
        await update.message.reply_text("Выберите уровень активности:", reply_markup=kb)
    elif step == "weight":
        ctx.user_data.setdefault("kbju", {})["weight"] = val
        ctx.user_data["kbju_step"] = "goal"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Поддерживать", callback_data="kbju_goal_maintain"),
             InlineKeyboardButton("Похудеть", callback_data="kbju_goal_lose"),
             InlineKeyboardButton("Набрать", callback_data="kbju_goal_gain")]
        ])
        await update.message.reply_text("Выберите вашу цель:", reply_markup=kb)

# --------------- Main ---------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern=r"^instructor_"))
    app.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern=r"^(free_course|next_day)$"))
    app.add_handler(CallbackQueryHandler(handle_gender, pattern=r"^gender_"))
    app.add_handler(CallbackQueryHandler(handle_program, pattern=r"^program_"))
    app.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"^send_report_day_(\d+)$"))
    app.add_handler(CallbackQueryHandler(handle_challenges, pattern=r"^challenge_menu$"))
    app.add_handler(CallbackQueryHandler(buy_challenge, pattern=r"^buy_challenge$"))
    app.add_handler(CallbackQueryHandler(handle_paid_course, pattern=r"^paid_course$"))
    app.add_handler(CallbackQueryHandler(confirm_payment, pattern=r"^confirm_payment_(\d+)$"))
    app.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern=r"^my_cabinet$"))
    app.add_handler(CallbackQueryHandler(handle_about_me, pattern=r"^about_me$"))
    app.add_handler(CallbackQueryHandler(handle_earn_points, pattern=r"^earn_points$"))
    app.add_handler(CallbackQueryHandler(handle_spend_points, pattern=r"^spend_points$"))
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern=r"^nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern=r"^buy_nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_referral, pattern=r"^referral$"))
    app.add_handler(CallbackQueryHandler(handle_challenge_next_day, pattern=r"^challenge_next$"))
    app.add_handler(CallbackQueryHandler(handle_back, pattern=r"^back$"))
    # Обработчики КБЖУ
    app.add_handler(CallbackQueryHandler(handle_kbju_calc, pattern=r"^kbju_calc$"))
    app.add_handler(CallbackQueryHandler(handle_buy_kbju, pattern=r"^buy_kbju$"))
    app.add_handler(CallbackQueryHandler(handle_kbju_gender, pattern=r"^kbju_gender_"))
    app.add_handler(CallbackQueryHandler(handle_kbju_activity, pattern=r"^kbju_activity_"))
    app.add_handler(CallbackQueryHandler(handle_kbju_goal, pattern=r"^kbju_goal_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_kbju_text))
    # Видеообработчики
    app.add_handler(MessageHandler(filters.VIDEO, handle_video_dispatch))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    # Обработчики для платного чека
    app.add_handler(CallbackQueryHandler(handle_send_paid_receipt, pattern=r"^send_paid_receipt_day_(\d+)$"))
    app.add_handler(CallbackQueryHandler(handle_paid_next_day, pattern=r"^paid_next_day$"))
    print("Бот запущен и готов к работе.")
    app.run_polling()

if __name__ == "__main__":
    main()
