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

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"

# Глобальные словари
user_scores = {}           # Баллы пользователя (общие и индивидуальные для тренеров)
user_status = {}
free_reports = {}          # Отчёты по бесплатному курсу
paid_reports = {}          # Отчёты по платному курсу
free_waiting_for_video = {}    # Ожидание видео (бесплатный курс): {user_id: day}
paid_waiting_for_video = {}    # Ожидание видео (платный курс): {user_id: day}
user_waiting_for_challenge_video = {}
user_waiting_for_receipt = {}  # Ожидание фото чека (платный курс)
user_challenges = {}
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Главное меню (кнопки в два столбца)
def main_menu():
    buttons = [
        ("🔥 Пройти бесплатный курс", "free_course"),
        ("💪 Челленджи", "challenge_menu"),
        ("📚 Платный курс", "paid_course"),
        ("🍽 Меню питания", "nutrition_menu"),
        ("👤 Мой кабинет", "my_cabinet"),
        ("💡 Как заработать баллы", "earn_points"),
        ("💰 Как потратить баллы", "spend_points"),
        ("ℹ️ Обо мне", "about_me"),
        ("🔗 Реферальная ссылка", "referral"),
        ("🍎 Подсчет КБЖУ", "calc_kbju")
    ]
    kb = []
    for i in range(0, len(buttons), 2):
        row = [InlineKeyboardButton(buttons[i][0], callback_data=buttons[i][1])]
        if i + 1 < len(buttons):
            row.append(InlineKeyboardButton(buttons[i+1][0], callback_data=buttons[i+1][1]))
        kb.append(row)
    return InlineKeyboardMarkup(kb)

def get_report_button_text(ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    gender = ctx.user_data[user_id].get("gender", "male")
    prog = ctx.user_data[user_id].get("program", "home")
    return (("👩" if gender=="female" else "👨") + ("🏠" if prog=="home" else "🏋️") + " Отправить отчет 📹")

# --------------------- ОБРАБОТКА /start ---------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if ctx.args:
            try:
                ref = int(ctx.args[0])
                if ref != user_id:
                    user_scores[ref] = user_scores.get(ref, 0) + 100
                    await ctx.bot.send_message(chat_id=ref,
                        text="🎉 Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!")
            except ValueError:
                pass
        ctx.user_data.setdefault(user_id, {"current_day": 1})
        user_scores[user_id] = user_scores.get(user_id, 0)
        user_status[user_id] = user_status.get(user_id, statuses[0])
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_1"),
             InlineKeyboardButton("💫 АНАСТАСИЯ", callback_data="instructor_2")],
            [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
            [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
            [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")]
        ])
        await ctx.bot.send_message(chat_id=update.effective_chat.id,
            text="Выбери для себя фитнес инструктора:", reply_markup=kb)
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# --------------------- ОБРАБОТКА ВЫБОРА ИНСТРУКТОРА ---------------------
async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()
    if data == "instructor_1":
        ctx.user_data[user_id]["instructor"] = "evgeniy"
        await ctx.bot.send_video(chat_id=query.message.chat_id,
            video="https://t.me/PRIVETSTVIEC/2",
            supports_streaming=True,
            caption="🎥 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu())
    elif data == "instructor_2":
        ctx.user_data[user_id]["instructor"] = "anastasiya"
        await query.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ 💫")
        await ctx.bot.send_photo(chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="📸 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu())
    else:
        sel = {"instructor_3": "Тренер 3 🏋️", "instructor_4": "Тренер 4 🤼", "instructor_5": "Тренер 5 🤸"}.get(data, "неизвестный тренер")
        await query.message.edit_text(f"Вы выбрали тренера: {sel}. Функционал пока не реализован 🚧\nВы будете перенаправлены в главное меню.", reply_markup=main_menu())

# --------------------- ОБРАБОТКА БЕСПЛАТНОГО КУРСА ---------------------
# Функция для обработки callback при выборе бесплатного курса
async def handle_free_course_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "free_course" and ("gender" not in ctx.user_data[user_id] or "program" not in ctx.user_data[user_id]):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("👨 Мужчина", callback_data="gender_male"),
                                      InlineKeyboardButton("👩 Женщина", callback_data="gender_female")]])
        return await query.message.reply_text("Ваш пол:", reply_markup=kb)
    await start_free_course(query.message, ctx, user_id)

async def handle_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["gender"] = "male" if query.data=="gender_male" else "female"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
                                  InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]])
    await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["program"] = "home" if query.data=="program_home" else "gym"
    ctx.user_data[user_id]["current_day"] = 1
    await start_free_course(query.message, ctx, user_id)

# --------------------- ОБРАБОТКА ОТПРАВКИ ОТЧЕТА (БЕСПЛАТНЫЙ КУРС) ---------------------
async def handle_send_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    day = int(query.data.split("_")[-1])
    if free_reports.get(user_id, {}).get(day):
        return await query.message.reply_text(f"Вы уже отправили отчет за день {day}.")
    free_waiting_for_video[user_id] = day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день 🎥")

# --------------------- ОБРАБОТКА ВИДЕО ОТЧЕТА (БЕСПЛАТНЫЙ/ПЛАТНЫЙ) ---------------------
async def handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in free_waiting_for_video:
        day = free_waiting_for_video[user_id]
        await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {day}.")
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
        free_reports.setdefault(user_id, {})[day] = True
        # Начисление 60 баллов за бесплатный курс
        instructor = ctx.user_data[user_id].get("instructor")
        if instructor in ["evgeniy", "anastasiya"]:
            ctx.user_data[user_id][f"{instructor}_score"] = ctx.user_data[user_id].get(f"{instructor}_score", 0) + 60
        else:
            user_scores[user_id] += 60
        del free_waiting_for_video[user_id]
        if day < 5:
            # Переход на следующий день
            if instructor in ["evgeniy", "anastasiya"]:
                ctx.user_data[user_id][f"{instructor}_free_day"] = day + 1
            else:
                ctx.user_data[user_id]["current_day"] = day + 1
            await update.message.reply_text(
                f"Отчет за день {day} принят! 🎉\nВаши баллы обновлены.\nГотовы к следующему дню ({day+1})? ➡️",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {day+1}", callback_data="next_day")]])
            )
        else:
            user_status[user_id] = statuses[1]
            await update.message.reply_text(f"Поздравляем! Вы завершили бесплатный курс! 🎉\nВаши баллы: обновлены.", reply_markup=main_menu())
    elif user_id in paid_waiting_for_video:
        day = paid_waiting_for_video[user_id]
        await ctx.bot.send_message(chat_id=GROUP_ID, text=f"Платный видео-отчет от {user_name} (ID: {user_id}) за день {day}.")
        await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
        paid_reports.setdefault(user_id, {})[day] = True
        # Начисление 30 баллов за платный курс
        user_scores[user_id] = user_scores.get(user_id, 0) + 30
        del paid_waiting_for_video[user_id]
        if day < 5:
            ctx.user_data[user_id]["paid_current_day"] = day + 1
            await update.message.reply_text(
                f"Отчет за платный день {day} принят! 🎉\nВаши баллы: обновлены.\nГотовы к следующему дню ({day+1})? ➡️",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"➡️ День {day+1}", callback_data="paid_next_day")]])
            )
        else:
            await update.message.reply_text(f"Поздравляем! Вы завершили платный курс! 🎉\nВаши баллы: обновлены.", reply_markup=main_menu())
            ctx.user_data[user_id].pop("paid_current_day", None)
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")

# --------------------- ПЛАТНЫЙ КУРС ---------------------
async def handle_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    discount = min(ctx.user_data[user_id].get("global_score", 0) * 2, 600)
    price = 2000 - discount
    instructor = ctx.user_data[user_id].get("instructor")
    callback_receipt = "send_receipt" if instructor == "evgeniy" else "send_receipt_anastasiya"
    await query.message.reply_text(
        f"📚 **Платный курс** 📚\n\nСтоимость курса: 2000 руб. 💵\nВаша скидка: {discount} руб. 🔖\nИтоговая сумма: {price} руб. 💳\n\n"
        f"💳 Переведите сумму на карту: 89236950304 (Яндекс Банк) 🏦\nПосле оплаты отправьте чек для проверки.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧾 Отправить чек", callback_data=callback_receipt)]])
    )
    user_waiting_for_receipt[user_id] = True

async def handle_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt[user_id] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате 📸.")

async def handle_send_receipt_anastasiya(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt[user_id] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате 📸.")

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
            [InlineKeyboardButton("👨 Мужчина", callback_data="paid_gender_male"),
             InlineKeyboardButton("👩 Женщина", callback_data="paid_gender_female")]
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

# --------------------- ОБРАБОТКА ВЫБОРА ПОЛА ДЛЯ ПЛАТНОГО КУРСА (ТОЛЬКО ДЛЯ EVGENIY) ---------------------
async def handle_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "paid_gender_male":
        await query.message.reply_text("В разработке 🚧")
    elif query.data == "paid_gender_female":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏋️ В зале", callback_data="paid_program_gym"),
                                     InlineKeyboardButton("🏠 Дома", callback_data="paid_program_home")]])
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
    txt_day1 = ("📚 **Платный курс: День 1** 📚\n\n" + "\n".join(day1_ex) + "\n\nОтправьте видео-отчет за день! 🎥")
    kb_day1 = InlineKeyboardMarkup([[InlineKeyboardButton("📹 Отправить отчет", callback_data="paid_video_day_1")]])
    await ctx.bot.send_message(chat_id=user_id, text=txt_day1, parse_mode="Markdown", reply_markup=kb_day1)

async def handle_paid_program_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке 🚧")

async def handle_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    paid_day = int(query.data.split("_")[-1])
    paid_waiting_for_video[user_id] = paid_day
    await query.message.reply_text(f"Пожалуйста, отправьте видео-отчет за платный день {paid_day} 🎥")

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
        text = f"📚 **Платный курс: День {next_day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день! 🎥"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📹 Отправить отчет", callback_data=f"paid_video_day_{next_day}")]])
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await query.message.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=main_menu())
        ctx.user_data[user_id].pop("paid_current_day", None)

# --------------------- ПОДСЧЕТ КБЖУ ---------------------
async def handle_calc_kbju(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Купить за 300 баллов", callback_data="buy_kbju"),
         InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Функция «Подсчет КБЖУ» стоит 300 баллов. Хотите купить? 💵", reply_markup=kb)

async def handle_buy_kbju(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = ctx.user_data[user_id].get("instructor")
    if instructor in ["evgeniy", "anastasiya"]:
        score_key = f"{instructor}_score"
        current_score = ctx.user_data[user_id].get(score_key, 0)
        if current_score < 300:
            return await query.message.reply_text("⚠️ Недостаточно баллов для покупки функции «Подсчет КБЖУ».", reply_markup=main_menu())
        ctx.user_data[user_id][score_key] = current_score - 300
    else:
        current_score = ctx.user_data[user_id].get("global_score", 0)
        if current_score < 300:
            return await query.message.reply_text("⚠️ Недостаточно баллов для покупки функции «Подсчет КБЖУ».", reply_markup=main_menu())
        ctx.user_data[user_id]["global_score"] = current_score - 300
    ctx.user_data[user_id]["kbju"] = {}
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨 Мужчина", callback_data="kbju_gender_male"),
         InlineKeyboardButton("👩 Женщина", callback_data="kbju_gender_female")]
    ])
    await query.message.reply_text("Пожалуйста, выберите ваш пол для расчёта КБЖУ:", reply_markup=kb)

async def handle_kbju_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    gender = "male" if query.data == "kbju_gender_male" else "female"
    ctx.user_data[user_id]["kbju"]["gender"] = gender
    ctx.user_data[user_id]["awaiting_kbju_age_height"] = True
    await query.message.reply_text("Введите ваш возраст и рост через запятую (например: 25,175):")

async def handle_kbju_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if ctx.user_data.get(user_id, {}).get("awaiting_kbju_age_height"):
        try:
            parts = update.message.text.split(',')
            age = int(parts[0].strip())
            height = int(parts[1].strip())
            ctx.user_data[user_id]["kbju"]["age"] = age
            ctx.user_data[user_id]["kbju"]["height"] = height
            ctx.user_data[user_id].pop("awaiting_kbju_age_height", None)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📉 Малая", callback_data="kbju_activity_low"),
                 InlineKeyboardButton("📈 Средняя", callback_data="kbju_activity_medium"),
                 InlineKeyboardButton("🚀 Высокая", callback_data="kbju_activity_high")]
            ])
            await update.message.reply_text("Выберите уровень активности:", reply_markup=kb)
        except Exception as e:
            logger.error(f"Ошибка при разборе возраста и роста: {e}")
            await update.message.reply_text("Неверный формат. Введите данные в формате: 25,175")
    elif ctx.user_data.get(user_id, {}).get("awaiting_kbju_weight"):
        try:
            weight = float(update.message.text.strip())
            ctx.user_data[user_id]["kbju"]["weight"] = weight
            ctx.user_data[user_id].pop("awaiting_kbju_weight", None)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚖️ Поддерживать", callback_data="kbju_goal_maintain"),
                 InlineKeyboardButton("⬇️ Похудеть", callback_data="kbju_goal_lose"),
                 InlineKeyboardButton("⬆️ Набрать массу", callback_data="kbju_goal_gain")]
            ])
            await update.message.reply_text("Выберите вашу цель:", reply_markup=kb)
        except Exception as e:
            logger.error(f"Ошибка при вводе веса: {e}")
            await update.message.reply_text("Неверный формат. Введите число, например: 70")
    else:
        pass

async def handle_kbju_activity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    activity = "low" if query.data == "kbju_activity_low" else ("medium" if query.data == "kbju_activity_medium" else "high")
    ctx.user_data[user_id]["kbju"]["activity"] = activity
    ctx.user_data[user_id]["awaiting_kbju_weight"] = True
    await query.message.reply_text("Введите ваш вес в кг (например: 70):")

async def handle_kbju_goal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    goal = "maintain" if query.data == "kbju_goal_maintain" else ("lose" if query.data == "kbju_goal_lose" else "gain")
    ctx.user_data[user_id]["kbju"]["goal"] = goal
    kbju_data = ctx.user_data[user_id]["kbju"]
    result = (f"Ваш расчет КБЖУ:\nКалорий: 2200 ккал\nБелков: 150 г\nЖиров: 70 г\nУглеводов: 250 г\n\n"
              f"(Входные данные: пол: {kbju_data.get('gender')}, возраст: {kbju_data.get('age')}, "
              f"рост: {kbju_data.get('height')} см, вес: {kbju_data.get('weight')} кг, активность: {kbju_data.get('activity')}, цель: {kbju_data.get('goal')})")
    await query.message.reply_text(result, reply_markup=main_menu())
    ctx.user_data[user_id].pop("kbju", None)

# --------------------- ОСТАЛОЙ ФУНКЦИОНАЛ ---------------------
async def handle_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = ctx.user_data[user_id].get("instructor")
    score = ctx.user_data[user_id].get(f"{instructor}_score", 0) if instructor in ["evgeniy", "anastasiya"] else ctx.user_data[user_id].get("global_score", 0)
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
    instructor = ctx.user_data[user_id].get("instructor")
    score = ctx.user_data[user_id].get(f"{instructor}_score", 0) if instructor in ["evgeniy", "anastasiya"] else ctx.user_data[user_id].get("global_score", 0)
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

# --------------------- ОБРАБОТКА ПОЛА/ПРОГРАММЫ ДЛЯ ПЛАТНОГО КУРСА (ТОЛЬКО ДЛЯ EVGENIY) ---------------------
async def handle_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "paid_gender_male":
        await query.message.reply_text("В разработке 🚧")
    elif query.data == "paid_gender_female":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏋️ В зале", callback_data="paid_program_gym"),
                                     InlineKeyboardButton("🏠 Дома", callback_data="paid_program_home")]])
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
    txt_day1 = ("📚 **Платный курс: День 1** 📚\n\n" + "\n".join(day1_ex) + "\n\nОтправьте видео-отчет за день! 🎥")
    kb_day1 = InlineKeyboardMarkup([[InlineKeyboardButton("📹 Отправить отчет", callback_data="paid_video_day_1")]])
    await ctx.bot.send_message(chat_id=user_id, text=txt_day1, parse_mode="Markdown", reply_markup=kb_day1)

async def handle_paid_program_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("В разработке 🚧")

async def handle_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    paid_day = int(query.data.split("_")[-1])
    paid_waiting_for_video[user_id] = paid_day
    await query.message.reply_text(f"Пожалуйста, отправьте видео-отчет за платный день {paid_day} 🎥")

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
        text = f"📚 **Платный курс: День {next_day}** 📚\n\n" + "\n".join(ex) + "\n\nОтправьте видео-отчет за день! 🎥"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📹 Отправить отчет", callback_data=f"paid_video_day_{next_day}")]])
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await query.message.reply_text("Поздравляем! Вы завершили платный курс! 🎉", reply_markup=main_menu())
        ctx.user_data[user_id].pop("paid_current_day", None)

# --------------------- ПОДСЧЕТ КБЖУ ---------------------
async def handle_calc_kbju(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Купить за 300 баллов", callback_data="buy_kbju"),
         InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ])
    await query.message.reply_text("Функция «Подсчет КБЖУ» стоит 300 баллов. Хотите купить? 💵", reply_markup=kb)

async def handle_buy_kbju(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = ctx.user_data[user_id].get("instructor")
    if instructor in ["evgeniy", "anastasiya"]:
        score_key = f"{instructor}_score"
        current_score = ctx.user_data[user_id].get(score_key, 0)
        if current_score < 300:
            return await query.message.reply_text("⚠️ Недостаточно баллов для покупки функции «Подсчет КБЖУ».", reply_markup=main_menu())
        ctx.user_data[user_id][score_key] = current_score - 300
    else:
        current_score = ctx.user_data[user_id].get("global_score", 0)
        if current_score < 300:
            return await query.message.reply_text("⚠️ Недостаточно баллов для покупки функции «Подсчет КБЖУ».", reply_markup=main_menu())
        ctx.user_data[user_id]["global_score"] = current_score - 300
    ctx.user_data[user_id]["kbju"] = {}
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨 Мужчина", callback_data="kbju_gender_male"),
         InlineKeyboardButton("👩 Женщина", callback_data="kbju_gender_female")]
    ])
    await query.message.reply_text("Пожалуйста, выберите ваш пол для расчёта КБЖУ:", reply_markup=kb)

async def handle_kbju_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    gender = "male" if query.data == "kbju_gender_male" else "female"
    ctx.user_data[user_id]["kbju"]["gender"] = gender
    ctx.user_data[user_id]["awaiting_kbju_age_height"] = True
    await query.message.reply_text("Введите ваш возраст и рост через запятую (например: 25,175):")

async def handle_kbju_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if ctx.user_data.get(user_id, {}).get("awaiting_kbju_age_height"):
        try:
            parts = update.message.text.split(',')
            age = int(parts[0].strip())
            height = int(parts[1].strip())
            ctx.user_data[user_id]["kbju"]["age"] = age
            ctx.user_data[user_id]["kbju"]["height"] = height
            ctx.user_data[user_id].pop("awaiting_kbju_age_height", None)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📉 Малая", callback_data="kbju_activity_low"),
                 InlineKeyboardButton("📈 Средняя", callback_data="kbju_activity_medium"),
                 InlineKeyboardButton("🚀 Высокая", callback_data="kbju_activity_high")]
            ])
            await update.message.reply_text("Выберите уровень активности:", reply_markup=kb)
        except Exception as e:
            logger.error(f"Ошибка при разборе возраста и роста: {e}")
            await update.message.reply_text("Неверный формат. Введите данные в формате: 25,175")
    elif ctx.user_data.get(user_id, {}).get("awaiting_kbju_weight"):
        try:
            weight = float(update.message.text.strip())
            ctx.user_data[user_id]["kbju"]["weight"] = weight
            ctx.user_data[user_id].pop("awaiting_kbju_weight", None)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚖️ Поддерживать", callback_data="kbju_goal_maintain"),
                 InlineKeyboardButton("⬇️ Похудеть", callback_data="kbju_goal_lose"),
                 InlineKeyboardButton("⬆️ Набрать массу", callback_data="kbju_goal_gain")]
            ])
            await update.message.reply_text("Выберите вашу цель:", reply_markup=kb)
        except Exception as e:
            logger.error(f"Ошибка при вводе веса: {e}")
            await update.message.reply_text("Неверный формат. Введите число, например: 70")
    else:
        pass

async def handle_kbju_activity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    activity = "low" if query.data == "kbju_activity_low" else ("medium" if query.data == "kbju_activity_medium" else "high")
    ctx.user_data[user_id]["kbju"]["activity"] = activity
    ctx.user_data[user_id]["awaiting_kbju_weight"] = True
    await query.message.reply_text("Введите ваш вес в кг (например: 70):")

async def handle_kbju_goal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    goal = "maintain" if query.data == "kbju_goal_maintain" else ("lose" if query.data == "kbju_goal_lose" else "gain")
    ctx.user_data[user_id]["kbju"]["goal"] = goal
    kbju_data = ctx.user_data[user_id]["kbju"]
    result = (f"Ваш расчет КБЖУ:\nКалорий: 2200 ккал\nБелков: 150 г\nЖиров: 70 г\nУглеводов: 250 г\n\n"
              f"(Входные данные: пол: {kbju_data.get('gender')}, возраст: {kbju_data.get('age')}, "
              f"рост: {kbju_data.get('height')} см, вес: {kbju_data.get('weight')} кг, активность: {kbju_data.get('activity')}, цель: {kbju_data.get('goal')})")
    await query.message.reply_text(result, reply_markup=main_menu())
    ctx.user_data[user_id].pop("kbju", None)

# --------------------- ОСТАЛОЙ ФУНКЦИОНАЛ ---------------------
async def handle_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    instructor = ctx.user_data[user_id].get("instructor")
    score = ctx.user_data[user_id].get(f"{instructor}_score", 0) if instructor in ["evgeniy", "anastasiya"] else ctx.user_data[user_id].get("global_score", 0)
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
    instructor = ctx.user_data[user_id].get("instructor")
    score = ctx.user_data[user_id].get(f"{instructor}_score", 0) if instructor in ["evgeniy", "anastasiya"] else ctx.user_data[user_id].get("global_score", 0)
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

# --------------------- MAIN ---------------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    app.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern="^(free_course|next_day)$"))
    app.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    app.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"^send_report_day_(\d+)$"))
    app.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    app.add_handler(CallbackQueryHandler(buy_challenge, pattern="^buy_challenge$"))
    app.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    app.add_handler(CallbackQueryHandler(handle_send_receipt, pattern="^send_receipt$"))
    app.add_handler(CallbackQueryHandler(handle_send_receipt_anastasiya, pattern="^send_receipt_anastasiya$"))
    app.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment_"))
    app.add_handler(CallbackQueryHandler(handle_send_paid_report, pattern=r"^paid_video_day_(\d+)$"))
    app.add_handler(CallbackQueryHandler(handle_paid_next_day, pattern="^paid_next_day$"))
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
    app.add_handler(CallbackQueryHandler(handle_calc_kbju, pattern="^calc_kbju$"))
    app.add_handler(CallbackQueryHandler(handle_buy_kbju, pattern="^buy_kbju$"))
    app.add_handler(CallbackQueryHandler(handle_kbju_gender, pattern="^kbju_gender_"))
    app.add_handler(CallbackQueryHandler(handle_kbju_activity, pattern="^kbju_activity_"))
    app.add_handler(CallbackQueryHandler(handle_kbju_goal, pattern="^kbju_goal_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_kbju_text))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    print("Бот запущен и готов к работе. 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
