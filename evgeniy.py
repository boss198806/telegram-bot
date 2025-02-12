from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging
from common import main_menu, start_free_course, handle_send_report, handle_video, handle_receipt, confirm_payment
from common import handle_my_cabinet, handle_about_me, handle_earn_points, handle_spend_points, handle_back
from common import handle_nutrition_menu, handle_buy_nutrition_menu, handle_referral, handle_challenge_next_day

logger = logging.getLogger(__name__)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if ctx.args:
            try:
                ref = int(ctx.args[0])
                if ref != user_id:
                    user_scores[ref] = user_scores.get(ref, 0) + 100
                    try:
                        await ctx.bot.send_message(chat_id=ref, text="🎉 Поздравляем! Новый пользователь воспользовался вашей реферальной ссылкой. Вы получили 100 баллов!")
                    except Exception as e:
                        logger.error(f"Реферальный бонус: {e}")
            except ValueError:
                pass
        ctx.user_data.setdefault(user_id, {"current_day": 1})
        user_scores[user_id] = user_scores.get(user_id, 0)
        user_status[user_id] = user_status.get(user_id, statuses[0])
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_1")],
            [InlineKeyboardButton("💫 АНАСТАСИЯ", callback_data="instructor_2")],
            [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
            [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
            [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")],
        ])
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Выбери для себя фитнес инструктора:", reply_markup=kb)
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
            caption="🎥 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu()
        )
    elif data == "instructor_2":
        ctx.user_data[user_id]["instructor"] = "anastasiya"
        await query.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ 💫")
        await ctx.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="📸 Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu()
        )
    else:
        sel = "неизвестный тренер"
        if data=="instructor_3":
            sel = "Тренер 3 🏋️"
        elif data=="instructor_4":
            sel = "Тренер 4 🤼"
        elif data=="instructor_5":
            sel = "Тренер 5 🤸"
        await query.message.edit_text(f"Вы выбрали тренера: {sel}. Функционал пока не реализован 🚧\nВы будете перенаправлены в главное меню.", reply_markup=main_menu())

async def handle_free_course_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "free_course" and ("gender" not in ctx.user_data[user_id] or "program" not in ctx.user_data[user_id]):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("👨 Мужчина", callback_data="gender_male")],
                                    [InlineKeyboardButton("👩 Женщина", callback_data="gender_female")]])
        return await query.message.reply_text("Ваш пол:", reply_markup=kb)
    await start_free_course(query.message, ctx, user_id)

async def handle_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["gender"] = "male" if query.data=="gender_male" else "female"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Дома", callback_data="program_home")],
                                [InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]])
    await query.message.reply_text("Выберите программу:", reply_markup=kb)

async def handle_program(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    ctx.user_data[user_id]["program"] = "home" if query.data=="program_home" else "gym"
    ctx.user_data[user_id]["current_day"] = 1
    await start_free_course(query.message, ctx, user_id)

async def handle_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    discount = min(user_scores.get(user_id, 0) * 2, 600)
    price = 2000 - discount
    await query.message.reply_text(
        f"📚 **Платный курс** 📚\n\nСтоимость курса: 2000 руб. 💵\nВаша скидка: {discount} руб. 🔖\nИтоговая сумма: {price} руб. 💳\n\n"
        f"💳 Переведите сумму на карту: 89236950304 (Яндекс Банк) 🏦\nПосле оплаты отправьте чек для проверки.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧾 Отправить чек", callback_data="send_receipt")]])
    )
    user_waiting_for_receipt[user_id] = True

async def handle_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_receipt[user_id] = True
    await query.message.reply_text("Пожалуйста, отправьте фото чека об оплате 📸.")

async def handle_paid_gender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "paid_gender_male":
        await query.message.reply_text("В разработке 🚧")
    elif query.data == "paid_gender_female":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏋️ В зале", callback_data="paid_program_gym")],
                                    [InlineKeyboardButton("🏠 Дома", callback_data="paid_program_home")]])
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
    user_waiting_for_video[user_id] = ("paid", paid_day)
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
