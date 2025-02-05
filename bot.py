import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.ext import CallbackContext
# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"
PHOTO_PATH = "https://t.me/pichersssd/5?raw=true"  # Укажите правильный путь к фото




# Словари для хранения данных
user_scores = {}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}
user_waiting_for_challenge_video = {}
user_waiting_for_receipt = {}
user_challenges = {}

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        context.user_data.setdefault(user_id, {"current_day": 1})
        user_scores[user_id] = user_scores.get(user_id, 0)
        user_status[user_id] = user_status.get(user_id, statuses[0])

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(PHOTO_PATH, 'rb'),
            caption="Привет! Я твой фитнес-ассистент!",
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")




# Главное меню
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
    ])

# Обработка кнопки "Меню питания"
async def handle_free_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id




    if user_score >= 300:
        # Списываем баллы
        user_scores[user_id] -= 300




        # Отправляем ссылку
        await query.message.reply_text(
            "✅ Вы успешно приобрели меню питания!\n"
            "Перейдите по ссылке, чтобы получить доступ: https://t.me/+Vp37EiVi_S0zN2Ji"
        )
    else:
        await query.message.reply_text(
            "Недостаточно баллов для покупки меню питания. "
            f"У вас {user_score} баллов, а нужно 300."
        )








# Бесплатный курс с фото и видео-ссылками
async def handle_free_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id


    # Проверяем, есть ли данные пользователя
    if user_id not in context.user_data:
        context.user_data[user_id] = {"current_day": 1}


    # Если пользователь нажал "Следующий день", увеличиваем current_day
    if query.data == "next_day":
        context.user_data[user_id]["current_day"] += 1


    # Теперь получаем обновленный current_day
    current_day = context.user_data[user_id].get("current_day", 1)


    if current_day > 5:
        await query.message.reply_text("Вы завершили курс! 🎉", reply_markup=main_menu())
        return


    # Пути к фото (остаются привязаны к своим дням)
    photo_paths = {
        1: "https://t.me/pichersssd/7?raw=true",  
        2: "https://t.me/pichersssd/8?raw=true",  
        3: "https://t.me/pichersssd/9?raw=true",  
        4: "https://t.me/pichersssd/10?raw=true",  
        5: "https://t.me/pichersssd/11?raw=true"
    }


    # Программа тренировок (переставлены только дни 4 и 5)
    course_program = {
        1: [
            "1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
            "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
            "3️⃣ Велосипед 3x15 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"
        ],
        2: [
            "1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/c/2241417709/167/168)",
            "2️⃣ Лодочка прямые руки 3x30 [Видео](https://t.me/c/2241417709/395/396)",
            "3️⃣ Полные подъёмы корпуса 3x20 [Видео](https://t.me/c/2241417709/274/275)"
        ],
        3: [
            "1️⃣ Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Махи в бок с колен 3x20 (можно без резинки) [Видео](https://t.me/c/2241417709/385/386)",
            "3️⃣ Косые с касанием пяток 3x15 на каждую [Видео](https://t.me/c/2241417709/282/283)"
        ],
        4: [  # Теперь тут упражнения с 5-го дня, но фото остается от 4-го дня
            "1️⃣ Поочередные подъемы с гантелями в развороте 4x20 [Видео](https://t.me/c/2241417709/226/227)",
            "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
            "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)"
        ],
        5: [  # Теперь тут упражнения с 4-го дня, но фото остается от 5-го дня
            "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Махи под 45 с резинкой (можно без нее) 3x20 [Видео](https://t.me/c/2241417709/339/340)",
            "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"
        ]
    }


    exercises = course_program.get(current_day, [])
    caption = f"🔥 **Бесплатный курс: День {current_day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день, чтобы получить баллы!"


    # Проверяем, существует ли фото
    photo_path = photo_paths.get(current_day)
    try:
        with open(photo_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Отправить отчет", callback_data=f"send_report_day_{current_day}")]]
                )
            )
    except FileNotFoundError:
        logger.error(f"Файл {photo_path} не найден.")
        await query.message.reply_text(
            "Ошибка: изображение не найдено. Продолжайте без фото.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Отправить отчет", callback_data=f"send_report_day_{current_day}")]]
            )
        )
# Обработка кнопки "Отправить отчет" для бесплатного курса
async def handle_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    current_day = int(query.data.split("_")[-1])  # Извлекаем день из callback_data




    if user_reports_sent.get(user_id, {}).get(current_day):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day}.")
        return




    user_waiting_for_video[user_id] = current_day
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")




# Обработка видео
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name




    # Обработка отчетов для бесплатного курса
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
            context.chat_data[user_id]["current_day"] += 1
            await update.message.reply_text(
                f"Отчет за день {current_day} принят! 🎉\n"
                f"Ваши баллы: {user_scores[user_id]}.\n"
                "Переход к следующему дню.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Следующий день", callback_data="free_course")]]
                )
            )
        else:
            user_status[user_id] = statuses[1]
            await update.message.reply_text(
                f"Поздравляем! Вы завершили бесплатный курс! 🎉\n"
                f"Ваши баллы: {user_scores[user_id]}.",
                reply_markup=main_menu()
            )




    # Словарь с программой челленджа
challenge_program = {
    1: [
        "1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
        "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"
    ],
    2: [
        "1️⃣ Присед со штангой (можно без) 30 раз [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Отжимания с отрывом рук 25 раз [Видео](https://t.me/c/2241417709/393/394)",
        "3️⃣ Полные подъёмы корпуса 30 раз [Видео](https://t.me/c/2241417709/274/275)"
    ],
    3: [
        "1️⃣ Планка 3 мин [Видео](https://t.me/c/2241417709/286/296)",
        "2️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"
    ],
    4: [
        "1️⃣ Выпады назад 60 раз [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
        "3️⃣ Велосипед 50 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"
    ],
    5: [
        "1️⃣ Присед со штангой (можно без) 50 раз [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
        "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)"
    ]
}

# Покупка челленджа
async def buy_challenge(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300  # Списываем баллы
        user_challenges[user_id] = {"current_day": 1}  # Записываем 1-й день челленджа

        await query.message.reply_text(
            "✅ Доступ к челленджу открыт!\n"
            "Вы начинаете с **1-го дня**. Отправьте видео-отчет, чтобы перейти дальше."
        )

        await send_challenge_task(query.message, user_id)  # Отправляем 1-й день
    else:
        await query.message.reply_text(
            f"❌ Недостаточно баллов! Вам нужно 300, а у вас {user_scores.get(user_id, 0)}."
        )

# Отправка задания челленджа
async def send_challenge_task(message, user_id):
    current_day = user_challenges[user_id]["current_day"]
    exercises = challenge_program.get(current_day, [])

    caption = f"🔥 **Челлендж: День {current_day}** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет!"

    await message.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📹 Отправить отчет", callback_data="send_challenge_report")]]
        )
    )

# Обработка видео-отчета челленджа
async def handle_challenge_video(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id in user_challenges:
        current_day = user_challenges[user_id]["current_day"]

        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"📹 Видео-отчет от {user_name} (ID: {user_id}) за день {current_day} челленджа."
        )
        await context.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

        user_scores[user_id] += 60  # Начисляем баллы

        if current_day < 5:
            user_challenges[user_id]["current_day"] += 1  # Переход к следующему дню
            await update.message.reply_text(
                f"✅ Отчет за день {current_day} принят!\n"
                f"🎉 Ваши баллы: {user_scores[user_id]}.\n"
                f"🔜 Завтра у вас {current_day + 1}-й день челленджа!",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f"➡ Перейти ко дню {current_day + 1}", callback_data="start_challenge")]]
                )
            )
        else:
            await update.message.reply_text(
                f"🎉 Поздравляем! Вы завершили челлендж!\n"
                f"🏆 Ваши баллы: {user_scores[user_id]}.\n"
                "Вы теперь настоящий Чемпион!",
                reply_markup=main_menu()
            )
            del user_challenges[user_id]  # Удаляем из списка челленджа
    else:
        await update.message.reply_text("❌ Я не жду видео. Выберите задание в меню.")

# Обработчик кнопки "Челленджи"
async def handle_challenges(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in user_challenges:
        await send_challenge_task(query.message, user_id)
    else:
        buttons = [
            [InlineKeyboardButton("🔥 Купить за 300 баллов", callback_data="buy_challenge")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        await query.message.reply_text(
            "Челлендж длится **5 дней**.\n"
            "Вы будете получать **упражнения и баллы за отчеты**.\n"
            "Стоимость участия — **300 баллов**.\n\n"
            "Хотите присоединиться?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Платный курс
async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    discount = min(user_scores.get(user_id, 0) * 2, 600)  # Максимальная скидка 30% от 2000
    final_price = 2000 - discount




    await query.message.reply_text(
        f"Платный курс стоит 2000 рублей.\n"
        f"Ваша скидка: {discount} рублей.\n"
        f"Итоговая сумма: {final_price} рублей.\n\n"
        f"Переведите сумму на карту: 89236950304 (Яндекс Банк).\n"
        f"После оплаты отправьте чек для проверки."
    )
    user_waiting_for_receipt[user_id] = True




# Обработка чека
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name




    if user_id not in user_waiting_for_receipt:
        await update.message.reply_text("Я не жду чек от вас. Пожалуйста, выберите платный курс и отправьте чек.")
        return




    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фото чека.")
        return




    # Отправляем чек в группу
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"Чек от {user_name} (ID: {user_id}). Подтвердите оплату."
    )
    photo_file_id = update.message.photo[-1].file_id
    await context.bot.send_photo(
        chat_id=GROUP_ID,
        photo=photo_file_id,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Подтвердить", callback_data=f"confirm_payment_{user_id}")]]
        )
    )




    await update.message.reply_text("Чек отправлен на проверку. Ожидайте подтверждения.")




# Подтверждение оплаты
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = int(query.data.split("_")[-1])
    user_status[user_id] = statuses[2]  # Чемпион
    del user_waiting_for_receipt[user_id]  # Очищаем данные




    # Отправляем сообщение пользователю
    await context.bot.send_message(
        chat_id=user_id,
        text="Оплата подтверждена! Вам открыт доступ к платному курсу. 🎉"
    )




# Обработка кнопки "Мой кабинет"
async def handle_my_cabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)
    status = user_status.get(user_id, statuses[0])




    try:
        # Отправляем изображение для "Мой кабинет" с описанием (caption)
        caption = f"👤 Ваш кабинет:\n\nСтатус: {status}\nБаллы: {score}\nПродолжайте тренироваться, чтобы улучшить статус и заработать больше баллов!"
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("https://t.me/pichersssd/3?raw=true", 'rb'),
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://t.me/pichersssd/3?raw=true не найден.")
        await update.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в /my_cabinet: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")




# Обработка кнопки "Обо мне"
async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        # Отправляем изображение для "Обо мне" с описанием (caption)
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
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("https://t.me/pichersssd/6?raw=true", 'rb'),  # Фото для "Обо мне" в формате jpg
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://t.me/pichersssd/6?raw=true не найден.")
        await update.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в /about_me: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
# Обработка кнопки "Как заработать баллы"
async def handle_earn_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query




    try:
        # Отправляем изображение для "Как заработать баллы" с описанием (caption)
        caption = (
            "💡 Как заработать баллы:\n\n"
            "1. Проходите бесплатный курс и отправляйте видео-отчеты.\n"
            "2. Участвуйте в челленджах и отправляйте видео-отчеты.\n"
            "3. Приглашайте друзей и получаете баллы за их активность.\n"
            "4. Покупайте платный курс и получаете дополнительные баллы."
        )
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("https://t.me/pichersssd/4?raw=true", 'rb'),
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://t.me/pichersssd/4?raw=true не найден.")
        await update.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в /earn_points: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")




   




# Обработка кнопки "Как потратить баллы"
async def handle_spend_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = user_scores.get(user_id, 0)




    try:
        # Отправляем изображение для "Как потратить баллы" с описанием (caption)
        caption = (
            f"💰 Как потратить баллы:\n\n"
            f"У вас есть {score} баллов.\n"
            "Вы можете потратить баллы на скидку при покупке платного курса.\n"
            "1 балл = 2 рубля скидки.\n"
            "Максимальная скидка - 600 рублей."
        )
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open("https://t.me/pichersssd/12?raw=true", 'rb'),
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://t.me/pichersssd/12?raw=true не найден.")
        await update.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в /spend_points: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")



# Главная функция
async def handle_nutrition_menu(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📋 Раздел 'Меню питания' пока в разработке.")
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    await update.message.reply_text(f"Ваш file_id: {photo_id}")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_free_course, pattern="^free_course|next_day$"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="start_challenge"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="challenge_menu"))
    application.add_handler(CallbackQueryHandler(buy_challenge, pattern="buy_challenge"))
    application.add_handler(CallbackQueryHandler(send_challenge_task, pattern="next_challenge_day"))
    application.add_handler(CallbackQueryHandler(handle_paid_course, pattern="paid_course"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="confirm_payment_.*"))
    application.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="my_cabinet"))
    application.add_handler(CallbackQueryHandler(handle_about_me, pattern="about_me"))
    application.add_handler(CallbackQueryHandler(handle_earn_points, pattern="earn_points"))
    application.add_handler(CallbackQueryHandler(handle_spend_points, pattern="spend_points"))
    application.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="nutrition_menu"))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))

    print("Бот запущен и готов к работе.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()




