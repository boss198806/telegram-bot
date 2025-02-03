import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes


# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"
GROUP_ID = "-1002451371911"
PHOTO_PATH = "https://github.com/boss198806/telegram-bot/blob/main/Photo.jpg"  # Укажите правильный путь к фото


# Словари для хранения данных
user_scores = {}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}  # Для бесплатного курса
user_waiting_for_challenge_video = {}  # Для челленджей
user_waiting_for_receipt = {}
user_challenges = {}


# Статусы
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        args = context.args  # Получаем аргументы (если пользователь пришел по реферальной ссылке)

        # Проверяем, есть ли реферальный код в ссылке
        if args and args[0].startswith("ref_"):
            referrer_id = int(args[0].split("_")[1])  # Получаем ID пригласившего

            # Проверяем, чтобы пользователь не получал бонус дважды и не сам себе
            if referrer_id != user_id and user_id not in user_scores:
                user_scores[referrer_id] = user_scores.get(referrer_id, 0) + 300  # Начисляем 300 баллов

                # Уведомляем пригласившего о начислении баллов
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 Вы пригласили нового участника! Вам начислено 300 баллов. Всего у вас: {user_scores[referrer_id]} баллов."
                )

        # Инициализируем данные нового пользователя
        context.chat_data[user_id] = {"current_day": 1}
        user_scores[user_id] = user_scores.get(user_id, 0)  # Обнуляем баллы, если новый пользователь
        user_status[user_id] = statuses[0]

        # Отправляем приветственное сообщение
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(PHOTO_PATH, 'rb'),
            caption="Привет! Я твой фитнес-ассистент! Помогу с тренировками, мотивацией и достижением целей.\n\n"
                    "Приглашай друзей и получай 300 баллов за каждого! 🎉\n\n"
                    f"Твоя реферальная ссылка:\nhttps://t.me/{context.bot.username}?start=ref_{user_id}",
            reply_markup=main_menu()
        )

    except FileNotFoundError:
        logger.error(f"Файл {PHOTO_PATH} не найден.")
        await update.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
# Главное меню
def main_menu():
    buttons = [
        [InlineKeyboardButton("🔥 Пройти бесплатный курс", callback_data="free_course")],
        [InlineKeyboardButton("💪 Челленджи", callback_data="start_challenge")],
        [InlineKeyboardButton("📚 Платный курс", callback_data="paid_course")],
        [InlineKeyboardButton("🍽 Меню питания", callback_data="nutrition_menu")],  # Новая кнопка
        [InlineKeyboardButton("👤 Мой кабинет", callback_data="my_cabinet")],
        [InlineKeyboardButton("💡 Как заработать баллы", callback_data="earn_points")],
        [InlineKeyboardButton("💰 Как потратить баллы", callback_data="spend_points")],
        [InlineKeyboardButton("ℹ️ Обо мне", callback_data="about_me")],
    ]
    return InlineKeyboardMarkup(buttons)




# Обработка кнопки "Меню питания"
async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_score = user_scores.get(user_id, 0)


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
    current_day = context.user_data[user_id]["current_day"]

    if current_day > 5:
        await query.message.reply_text(
            "Вы завершили бесплатный курс! Поздравляем! 🎉",
            reply_markup=main_menu()
        )
        return

    # Пути к фото (остаются привязаны к своим дням)
    photo_paths = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG",  
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG",  
        3: "Dhttps://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG",  
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG",  
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG"  
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


    # Обработка отчетов для челленджей
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
            f"Отчет за челлендж принят! 🎉\n"
            f"Ваши баллы: {user_scores[user_id]}."
        )


    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.")


# Челленджи
async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id


    if user_challenges.get(user_id):
        # Если доступ уже куплен, показываем задание и просим отправить отчет
        await query.message.reply_text(
            "Ваше задание на сегодня:\n"
            "1️⃣ Бег 5 км\n"
            "2️⃣ Планка 3 минуты\n"
            "3️⃣ Подтягивания 3x10\n\n"
            "Отправьте видео-отчет, чтобы получить 60 баллов!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Отправить отчет", callback_data="send_challenge_report")]]
            )
        )
    else:
        if user_scores.get(user_id, 0) >= 300:
            buttons = [
                [InlineKeyboardButton("Купить доступ за 300 баллов", callback_data="buy_challenge")],
                [InlineKeyboardButton("Назад", callback_data="back")]
            ]
            await query.message.reply_text(
                "Доступ к челленджам стоит 300 баллов. Хотите приобрести?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await query.message.reply_text(
                "Для доступа к челленджам нужно 300 баллов. "
                f"У вас {user_scores.get(user_id, 0)} баллов. "
                "Продолжайте тренировки!"
            )


# Покупка челленджа
async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id


    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id] = True


        # После покупки сразу выдаем задание и просим отправить отчет
        await query.message.reply_text(
            "✅ Доступ к челленджам открыт!\n\n"
            "Ваше задание на сегодня:\n"
            "1️⃣ Бег 5 км\n"
            "2️⃣ Планка 3 минуты\n"
            "3️⃣ Подтягивания 3x10\n\n"
            "Отправьте видео-отчет, чтобы получить 60 баллов!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Отправить отчет", callback_data="send_challenge_report")]]
            )
        )
    else:
        await query.message.reply_text("Недостаточно баллов для покупки доступа!")


# Обработка отправки отчета для челленджа
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    if user_id in user_waiting_for_video:
        current_day = user_waiting_for_video[user_id]

        # Отправляем видео в группу
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"📹 Видео-отчет от {user_name} (ID: {user_id}) за день {current_day}."
        )
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id
        )

        user_reports_sent.setdefault(user_id, {})[current_day] = True
        user_scores[user_id] += 60

        # Удаляем user_waiting_for_video (но день не увеличиваем здесь!)
        del user_waiting_for_video[user_id]

        # Проверяем, не последний ли день
        if current_day < 5:
            await update.message.reply_text(
                f"✅ Отчет за день {current_day} принят!\n"
                f"🎉 Ваши баллы: {user_scores[user_id]}.\n"
                f"🔜 Готовы к следующему дню ({current_day + 1})?",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f"➡ Перейти ко дню {current_day + 1}", callback_data="next_day")]]
                )
            )
        else:
            user_status[user_id] = statuses[1]
            await update.message.reply_text(
                f"🎉 Поздравляем! Вы завершили бесплатный курс!\n"
                f"🏆 Ваши баллы: {user_scores[user_id]}.",
                reply_markup=main_menu()
            )
    else:
        await update.message.reply_text("❌ Я не жду видео. Выберите задание в меню.")
# Покупка челленджа
async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id


    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id] = True
        await query.message.reply_text(
            "✅ Доступ к челленджам открыт!\n"
            "Теперь вы можете отправлять отчеты и получать баллы!"
        )
    else:
        await query.message.reply_text("Недостаточно баллов для покупки доступа!")


# Обработка отправки отчета для челленджа
async def send_challenge_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_waiting_for_challenge_video[user_id] = True
    await query.message.reply_text("Отправьте видео-отчет для челленджа:")


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
            photo=open("https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG", 'rb'),
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://github.com/boss198806/telegram-bot/blob/main/IMG_9695.PNG.")
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
            photo=open("https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg", 'rb'),  # Фото для "Обо мне" в формате jpg
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://github.com/boss198806/telegram-bot/blob/main/photo_2025.jpg не найден.")
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
            photo=open("https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG", 'rb'),
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://github.com/boss198806/telegram-bot/blob/main/IMG_9699.PNG не найден.")
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
            photo=open("https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG", 'rb'),
            caption=caption  # Это описание, которое будет под фото
        )
    except FileNotFoundError:
        logger.error(f"Файл https://github.com/boss198806/telegram-bot/blob/main/IMG_9692.PNG не найден.")
        await update.message.reply_text("Произошла ошибка при загрузке фотографии. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в /spend_points: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_free_course, pattern="^free_course|next_day$"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="start_challenge"))
    application.add_handler(CallbackQueryHandler(buy_challenge, pattern="buy_challenge"))
    application.add_handler(CallbackQueryHandler(send_challenge_report, pattern="send_challenge_report"))
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
    application.run_polling()


if __name__ == "__main__":
    main()

