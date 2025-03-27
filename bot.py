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

# Токен бота и ID группы для отчетов
TOKEN = "7761949562:AAF-zTgYwd5rzETyr3OnAGCGxrSQefFuKZs"  # Замените на ваш токен
GROUP_ID = "-1002451371911"  # Замените на ID вашей группы

# Глобальные словари для хранения данных
user_scores = {}  # {user_id: {instructor: баллы}}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}
user_waiting_for_challenge_video = {}
user_waiting_for_paid_video = {}
user_waiting_for_receipt = {}
user_challenges = {}  # {user_id: {instructor: {"current_day": int}}}
user_paid_course = {}  # {user_id: {instructor: {"current_day": int}}}
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Вспомогательные функции
def main_menu():
    """Возвращает главное меню бота."""
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
    """Формирует текст кнопки отправки отчета в зависимости от пола и программы."""
    gender = context.user_data[user_id].get("gender", "male")
    program = context.user_data[user_id].get("program", "home")
    prefix = "👩" if gender == "female" else "👨"
    suffix = "🏠" if program == "home" else "🏋️"
    return f"{prefix}{suffix} Отправить отчет"

# Функции бесплатного курса
async def start_free_course(message, context: ContextTypes.DEFAULT_TYPE, user_id: int, instructor: str):
    """Запускает бесплатный курс для пользователя."""
    gender = context.user_data[user_id].get("gender")
    program = context.user_data[user_id].get("program")
    
    # Условие доступа: только для женщин
    if gender != "female":
        await message.reply_text("Бесплатный курс доступен только для женщин.", reply_markup=main_menu())
        return

    # Инициализация данных пользователя
    context.user_data[user_id].setdefault("free_course", {})
    context.user_data[user_id]["free_course"].setdefault(instructor, {})
    
    # Инициализация текущего дня для программы "дома" или "в зале"
    if program == "home":
        context.user_data[user_id]["free_course"][instructor].setdefault("current_day_home", 1)
        current_day = context.user_data[user_id]["free_course"][instructor]["current_day_home"]
    else:  # program == "gym"
        context.user_data[user_id]["free_course"][instructor].setdefault("current_day_gym", 1)
        current_day = context.user_data[user_id]["free_course"][instructor]["current_day_gym"]

    # Проверка завершения курса
    if current_day > 5:
        await message.reply_text(f"Вы завершили бесплатный курс у тренера {instructor} ({'дома' if program == 'home' else 'в зале'})! 🎉", reply_markup=main_menu())
        return

    # Программа для тренера Евгения (для дома)
    if instructor == "evgeniy" and program == "home":
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
    # Программа для тренера Анастасии (для дома)
    elif instructor == "anastasiya" and program == "home":
        course_program = {
            1: [
                "1. Приседания 20x3 [Видео](https://t.me/c/2334950288/2/17)",
                "2. Ягодичный мост 20х3 [Видео](https://t.me/c/2334950288/3/18)",
                "3. Планка 3х1 минута [Видео](https://t.me/c/2334950288/4/19)",
            ],
            2: [
                "1. Гиперэкстензия на полу 15х3 [Видео](https://t.me/c/2334950288/8/23)",
                "2. Отжимания с колен 12х3 [Видео](https://t.me/c/2334950288/9/24)",
                "3. Пресс «ножницы» 20х3 [Видео](https://t.me/c/2334950288/10/25)",
            ],
            3: [
                "1. Выпады на месте 15х3 [Видео](https://t.me/c/2334950288/5/20)",
                "2. Стульчик статика 3х1 мин [Видео](https://t.me/c/2334950288/6/21)",
                "3. Пресс «жук» 20х3 [Видео](https://t.me/c/2334950288/7/22)",
            ],
            4: [
                "1. Лодочка 20х3 [Видео](https://t.me/c/2334950288/11/26)",
                "2. Волна от Пола 15х3 [Видео](https://t.me/c/2334950288/12/27)",
                "3. Планка в динамике шаг 15х3 [Видео](https://t.me/c/2334950288/13/28)",
            ],
            5: [
                "1. Приседание плие 20х3 [Видео](https://t.me/c/2334950288/14/29)",
                "2. Румынская тяга на 1 ногу 20х3 [Видео](https://t.me/c/2334950288/15/303)",
                "3. Скалолаз 20х3 [Видео](https://t.me/c/2334950288/16/31)",
            ],
        }
    # Программа для тренера Анастасии (для зала)
    elif instructor == "anastasiya" and program == "gym":
        course_program = {
            1: [
                "1. Приседания с весом 20х3 [Видео](https://t.me/c/2478853360/2/5)",
                "2. Жим платформы ногами 15х3 [Видео](https://t.me/c/2478853360/6/8)",
                "3. Сведение рук в тренажере «бабочка» 15х3 [Видео](https://t.me/c/2478853360/7/9)",
            ],
            2: [
                "1. Горизонтальная тяга V-рукоятка 15х3 [Видео](https://t.me/c/2478853360/10/11)",
                "2. Отведение рук в тренажере «бабочка» 15х3 [Видео](https://t.me/c/2478853360/12/14)",
                "3. Жим штанги/бодибара сидя 15х3 [Видео](https://t.me/c/2478853360/13/18)",
            ],
            3: [
                "1. Выпад в шаге с весом 15х3 [Видео](https://t.me/c/2478853360/15/19)",
                "2. Разведение в тренажере 15х3 [Видео](https://t.me/c/2478853360/17/20)",
                "3. Сгибание рук с гантелями 12х3 [Видео](https://t.me/c/2478853360/21/22)",
            ],
            4: [
                "1. Вертикальная тяга широким хватом к груди 15х3 [Видео](https://t.me/c/2478853360/23/25)",
                "2. Гиперэкстензия в тренажере 15х3 [Видео](https://t.me/c/2478853360/24/26)",
                "3. Обратные отжимания 12х3 [Видео](https://t.me/c/2478853360/27/28)",
            ],
            5: [
                "1. Румынская тяга со штангой 15х3 [Видео](https://t.me/c/2478853360/29/30)",
                "2. Сгибание в тренажере лёжа 15х3 [Видео](https://t.me/c/2478853360/35/36)",
                "3. Подъём на носки стоя на возвышении 20х3 [Видео](https://t.me/c/2478853360/31/34)",
            ],
        }
    else:
        await message.reply_text("Программа для этого тренера и типа тренировки пока в разработке.", reply_markup=main_menu())
        return

    # Фотографии на каждый день
    photo_paths = {
        1: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9647.PNG?raw=true",
        2: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9648.PNG?raw=true",
        3: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9649.PNG?raw=true",
        4: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9650.PNG?raw=true",
        5: "https://github.com/boss198806/telegram-bot/blob/main/IMG_9651.PNG?raw=true",
    }

    # Формирование сообщения
    exercises = course_program.get(current_day, [])
    caption = f"🔥 **Бесплатный курс у {instructor}: День {current_day} ({'дома' if program == 'home' else 'в зале'})** 🔥\n\n" + "\n".join(exercises) + "\n\nОтправьте видео-отчет за день!"
    report_button_text = get_report_button_text(context, user_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(report_button_text, callback_data=f"send_report_day_{current_day}_{instructor}_{program}")]
    ])

    # Отправка программы с фото
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
        await message.reply_text(caption, parse_mode="Markdown", reply_markup=keyboard)

async def handle_send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запрос на отправку видео-отчета для бесплатного курса."""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split("_")
    current_day = int(data[3])
    instructor = data[4]
    program = data[5]  # "home" или "gym"
    report_key = f"{instructor}_free_{current_day}_{program}"
    if user_reports_sent.get(user_id, {}).get(report_key):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day} у тренера {instructor} ({'дома' if program == 'home' else 'в зале'}).")
        return
    user_waiting_for_video[user_id] = (current_day, instructor, "free", program)
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает отправку видео-отчетов для всех курсов."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in user_waiting_for_video:
        current_day, instructor, course_type, program = user_waiting_for_video[user_id]
        if course_type == "free":
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {current_day} бесплатного курса у тренера {instructor} ({'дома' if program == 'home' else 'в зале'})."
            )
            await context.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
            report_key = f"{instructor}_free_{current_day}_{program}"
            user_reports_sent.setdefault(user_id, {})[report_key] = True
            user_scores.setdefault(user_id, {}).setdefault(instructor, 0)
            user_scores[user_id][instructor] += 60
            del user_waiting_for_video[user_id]
            if current_day < 5:
                # Обновляем текущий день в зависимости от программы
                if program == "home":
                    context.user_data[user_id]["free_course"][instructor]["current_day_home"] += 1
                    new_day = context.user_data[user_id]["free_course"][instructor]["current_day_home"]
                else:  # program == "gym"
                    context.user_data[user_id]["free_course"][instructor]["current_day_gym"] += 1
                    new_day = context.user_data[user_id]["free_course"][instructor]["current_day_gym"]
                await update.message.reply_text(
                    f"Отчет за день {current_day} принят! 🎉\nВаши баллы у тренера {instructor}: {user_scores[user_id][instructor]}.\nГотовы к дню {new_day}?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"➡️ День {new_day}", callback_data=f"next_day_{instructor}_{program}")]
                    ]),
                )
            else:
                user_status[user_id] = statuses[1]
                await update.message.reply_text(
                    f"Поздравляем! Вы завершили бесплатный курс у тренера {instructor} ({'дома' if program == 'home' else 'в зале'})! 🎉\nВаши баллы: {user_scores[user_id][instructor]}.",
                    reply_markup=main_menu(),
                )
    elif user_id in user_waiting_for_challenge_video:
        current_day, instructor = user_waiting_for_challenge_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {current_day} челленджа у тренера {instructor}."
        )
        await context.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
        user_reports_sent.setdefault(user_id, {})[f"{instructor}_challenge_{current_day}"] = True
        user_scores.setdefault(user_id, {}).setdefault(instructor, 0)
        user_scores[user_id][instructor] += 60
        del user_waiting_for_challenge_video[user_id]
        if current_day < 5:
            user_challenges[user_id][instructor]["current_day"] += 1
            new_day = user_challenges[user_id][instructor]["current_day"]
            await update.message.reply_text(
                f"Отчет за день {current_day} принят! 🎉\nВаши баллы: {user_scores[user_id][instructor]}.\nГотовы к дню {new_day}?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {new_day}", callback_data=f"challenge_next_{instructor}")]
                ]),
            )
        else:
            await update.message.reply_text(
                f"Поздравляем! Вы завершили челлендж у тренера {instructor}! 🎉\nВаши баллы: {user_scores[user_id][instructor]}.",
                reply_markup=main_menu(),
            )
    elif user_id in user_waiting_for_paid_video:
        current_day, instructor = user_waiting_for_paid_video[user_id]
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"Видео-отчет от {user_name} (ID: {user_id}) за день {current_day} платного курса у тренера {instructor}."
        )
        await context.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)
        user_reports_sent.setdefault(user_id, {})[f"{instructor}_paid_{current_day}"] = True
        user_scores.setdefault(user_id, {}).setdefault(instructor, 0)
        user_scores[user_id][instructor] += 60
        del user_waiting_for_paid_video[user_id]
        if current_day < 5:
            user_paid_course[user_id][instructor]["current_day"] += 1
            new_day = user_paid_course[user_id][instructor]["current_day"]
            await update.message.reply_text(
                f"Отчет за день {current_day} принят! 🎉\nВаши баллы: {user_scores[user_id][instructor]}.\nГотовы к дню {new_day}?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"➡️ День {new_day}", callback_data=f"paid_next_day_{instructor}")]
                ]),
            )
        else:
            await update.message.reply_text(
                f"Поздравляем! Вы завершили платный курс у тренера {instructor}! 🎉\nВаши баллы: {user_scores[user_id][instructor]}.",
                reply_markup=main_menu(),
            )
    else:
        await update.message.reply_text("Я не жду видео. Выберите задание в меню.", reply_markup=main_menu())

# Обработчики выбора пола и программы
async def handle_free_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор бесплатного курса."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if not instructor:
        await query.message.reply_text("Сначала выберите тренера.", reply_markup=main_menu())
        return
    if "gender" not in context.user_data[user_id] or "program" not in context.user_data[user_id]:
        gender_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Мужчина", callback_data="gender_male"),
             InlineKeyboardButton("Женщина", callback_data="gender_female")]
        ])
        await query.message.reply_text("Ваш пол:", reply_markup=gender_keyboard)
        return
    await start_free_course(query.message, context, user_id, instructor)

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор пола."""
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data[user_id]["gender"] = "male" if query.data == "gender_male" else "female"
    program_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Дома", callback_data="program_home"),
         InlineKeyboardButton("🏋️ В зале", callback_data="program_gym")]
    ])
    await query.message.reply_text("Выберите программу:", reply_markup=program_keyboard)

async def handle_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор программы."""
    query = update.callback_query
    user_id = query.from_user.id
    context.user_data[user_id]["program"] = "home" if query.data == "program_home" else "gym"
    instructor = context.user_data[user_id].get("instructor")
    await start_free_course(query.message, context, user_id, instructor)

async def handle_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переходит к следующему дню бесплатного курса."""
    query = update.callback_query
    data = query.data.split("_")
    instructor = data[2]
    program = data[3]  # "home" или "gym"
    user_id = query.from_user.id
    if instructor not in context.user_data.get(user_id, {}).get("free_course", {}):
        await query.message.reply_text("Вы не начали курс у этого тренера.", reply_markup=main_menu())
        return
    await start_free_course(query.message, context, user_id, instructor)
    await query.answer()

# Функции для платного курса
async def start_paid_course(message, context: ContextTypes.DEFAULT_TYPE, user_id: int, instructor: str):
    """Запускает платный курс."""
    if instructor not in user_paid_course.get(user_id, {}):
        await message.reply_text("У вас нет доступа к платному курсу у этого тренера.", reply_markup=main_menu())
        return
    current_day = user_paid_course[user_id][instructor]["current_day"]
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
    await context.bot.send_message(chat_id=message.chat_id, text=caption, parse_mode="Markdown", reply_markup=keyboard)

async def handle_send_paid_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запрос на отправку отчета для платного курса."""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split("_")
    current_day = int(data[4])
    instructor = data[5]
    if user_reports_sent.get(user_id, {}).get(f"{instructor}_paid_{current_day}"):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day} у тренера {instructor}.")
        return
    user_waiting_for_paid_video[user_id] = (current_day, instructor)
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день платного курса.")

async def handle_paid_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переходит к следующему дню платного курса."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = query.data.split("_")[-1]
    if instructor not in user_paid_course.get(user_id, {}):
        await query.message.reply_text("У вас нет доступа к платному курсу у этого тренера.", reply_markup=main_menu())
        return
    await start_paid_course(query.message, context, user_id, instructor)
    await query.answer()

# Функции для челленджей
async def send_challenge_task(message: Update, user_id: int, context: ContextTypes.DEFAULT_TYPE, instructor: str):
    """Отправляет задание челленджа."""
    if instructor not in user_challenges.get(user_id, {}):
        await message.reply_text("У вас нет доступа к челленджу у этого тренера.", reply_markup=main_menu())
        return
    current_day = user_challenges[user_id][instructor].get("current_day", 1)
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
    buttons = [[InlineKeyboardButton("📹 Отправить отчет", callback_data=f"send_challenge_report_day_{current_day}_{instructor}")]]
    if current_day < 5:
        buttons.append([InlineKeyboardButton("➡️ Следующий день", callback_data=f"challenge_next_{instructor}")])
    else:
        buttons.append([InlineKeyboardButton("🔙 Главное меню", callback_data="back")])
    await message.reply_text(caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_send_challenge_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запрос на отправку отчета для челленджа."""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split("_")
    current_day = int(data[4])
    instructor = data[5]
    if user_reports_sent.get(user_id, {}).get(f"{instructor}_challenge_{current_day}"):
        await query.message.reply_text(f"Вы уже отправили отчет за день {current_day} у тренера {instructor}.")
        return
    user_waiting_for_challenge_video[user_id] = (current_day, instructor)
    await query.message.reply_text("Пожалуйста, отправьте видео-отчет за текущий день челленджа.")

async def handle_challenge_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переходит к следующему дню челленджа."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = query.data.split("_")[-1]
    if instructor not in user_challenges.get(user_id, {}):
        await query.answer("Сначала купите челлендж!")
        return
    current_day = user_challenges[user_id][instructor].get("current_day", 1)
    if current_day < 5:
        user_challenges[user_id][instructor]["current_day"] += 1
        await send_challenge_task(query.message, user_id, context, instructor)
    else:
        await query.message.reply_text(f"Поздравляем, вы завершили челлендж у тренера {instructor}!", reply_markup=main_menu())

# Команда /start и выбор тренера
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start и реферальную систему."""
    user_id = update.effective_user.id
    if context.args:
        referrer_id = int(context.args[0])
        if referrer_id != user_id:
            instructor = context.user_data.get(referrer_id, {}).get("instructor")
            if instructor:
                user_scores.setdefault(referrer_id, {}).setdefault(instructor, 0)
                user_scores[referrer_id][instructor] += 100
                await context.bot.send_message(referrer_id, f"Новый пользователь по вашей ссылке! +100 баллов у тренера {instructor}.")

    context.user_data.setdefault(user_id, {})
    user_scores.setdefault(user_id, {})
    user_status.setdefault(user_id, statuses[0])

    instructor_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Евгений Курочкин", callback_data="instructor_1")],
        [InlineKeyboardButton("АНАСТАСИЯ", callback_data="instructor_2")],
        [InlineKeyboardButton("Тренер 3", callback_data="instructor_3")],
    ])
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите тренера:", reply_markup=instructor_keyboard)

async def handle_instructor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор тренера."""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()
    if data == "instructor_1":
        context.user_data[user_id]["instructor"] = "evgeniy"
        await query.message.edit_text("Вы выбрали тренера: Евгений Курочкин")
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video="https://github.com/boss198806/telegram-bot/raw/refs/heads/main/IMG_1484.MOV",
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: Евгений Курочкин",
            reply_markup=main_menu(),
        )
    elif data == "instructor_2":
        context.user_data[user_id]["instructor"] = "anastasiya"
        await query.message.edit_text("Вы выбрали тренера: АНАСТАСИЯ")
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo="https://github.com/boss198806/telegram-bot/blob/main/photo_2025-02-08_22-08-36.jpg?raw=true",
            caption="Привет! Я твой фитнес-ассистент!\nВы выбрали тренера: АНАСТАСИЯ",
            reply_markup=main_menu(),
        )
    else:
        await query.message.edit_text("Функционал для этого тренера пока в разработке.", reply_markup=main_menu())

# Дополнительные функции
async def handle_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает меню питания."""
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Купить меню за 300 баллов", callback_data="buy_nutrition_menu")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
    await query.message.reply_text("Меню питания доступно для покупки:", reply_markup=keyboard)

async def handle_buy_nutrition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает покупку меню питания."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor and user_scores.get(user_id, {}).get(instructor, 0) >= 300:
        user_scores[user_id][instructor] -= 300
        await query.message.reply_text(
            f"Меню питания куплено у тренера {instructor}!\nСсылка: https://t.me/MENUKURO4KIN/2",
            reply_markup=main_menu(),
        )
    else:
        await query.message.reply_text(f"Недостаточно баллов у тренера {instructor}!")

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерирует реферальную ссылку."""
    query = update.callback_query
    user_id = query.from_user.id
    me = await context.bot.get_me()
    referral_link = f"https://t.me/{me.username}?start={user_id}"
    await query.message.reply_text(f"Ваша реферальная ссылка:\n{referral_link}\nПриглашайте друзей и получайте 100 баллов!")

async def handle_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает меню челленджей."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if user_challenges.get(user_id, {}).get(instructor):
        await send_challenge_task(query.message, user_id, context, instructor)
    elif user_scores.get(user_id, {}).get(instructor, 0) >= 300:
        await query.message.reply_text(
            f"Челлендж у тренера {instructor} стоит 300 баллов. Купить?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Купить", callback_data=f"buy_challenge_{instructor}")],
                [InlineKeyboardButton("Назад", callback_data="back")],
            ]),
        )
    else:
        await query.message.reply_text(f"Недостаточно баллов для челленджа у тренера {instructor}!")

async def buy_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Покупает доступ к челленджу."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = query.data.split("_")[-1]
    if user_scores.get(user_id, {}).get(instructor, 0) >= 300:
        user_scores[user_id][instructor] -= 300
        user_challenges.setdefault(user_id, {})[instructor] = {"current_day": 1}
        await query.message.reply_text(f"✅ Доступ к челленджу у тренера {instructor} открыт!")
        await send_challenge_task(query.message, user_id, context, instructor)
    else:
        await query.message.reply_text(f"Недостаточно баллов у тренера {instructor}!")

async def handle_paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает меню платного курса."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = context.user_data[user_id].get("instructor")
    if instructor not in user_paid_course.get(user_id, {}):
        discount = min(user_scores.get(user_id, {}).get(instructor, 0) * 2, 600)
        final_price = 2000 - discount
        await query.message.reply_text(
            f"Платный курс у тренера {instructor}: 2000 руб. Скидка: {discount} руб. Итог: {final_price} руб.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Оплатить", callback_data=f"pay_course_{instructor}")],
                [InlineKeyboardButton("Назад", callback_data="back")],
            ]),
        )
    else:
        await start_paid_course(query.message, context, user_id, instructor)

async def pay_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает оплату платного курса."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = query.data.split("_")[-1]
    await query.message.reply_text(
        f"Переведите 2000 руб. на карту 1234-5678-9012-3456 для тренера {instructor} и отправьте чек.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отправить чек", callback_data=f"send_receipt_{instructor}")]]),
    )

async def send_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает чек для оплаты."""
    query = update.callback_query
    user_id = query.from_user.id
    instructor = query.data.split("_")[-1]
    user_waiting_for_receipt[user_id] = instructor
    await query.message.reply_text("Отправьте фото чека.")

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает отправку чека."""
    user_id = update.message.from_user.id
    if user_id in user_waiting_for_receipt:
        instructor = user_waiting_for_receipt[user_id]
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"Чек от пользователя {user_id} для тренера {instructor}.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Подтвердить", callback_data=f"confirm_payment_{user_id}_{instructor}")]]),
        )
        del user_waiting_for_receipt[user_id]
        await update.message.reply_text("Чек отправлен на проверку.")
    else:
        await update.message.reply_text("Я не жду чек. Начните оплату заново.")

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждает оплату платного курса."""
    query = update.callback_query
    data = query.data.split("_")
    user_id = int(data[2])
    instructor = data[3]
    user_paid_course.setdefault(user_id, {})[instructor] = {"current_day": 1}
    await context.bot.send_message(GROUP_ID, f"Оплата для пользователя {user_id} и тренера {instructor} подтверждена.")
    await context.bot.send_message(user_id, f"Оплата подтверждена! Начните платный курс у тренера {instructor}.")
    await start_paid_course(query.message, context, user_id, instructor)
    await query.answer()

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает в главное меню."""
    query = update.callback_query
    await query.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu())
    await query.answer()

# Регистрация обработчиков
def main():
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    application.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern="^free_course$"))
    application.add_handler(CallbackQueryHandler(handle_next_day, pattern=r"^next_day_(\w+)_(\w+)$"))
    application.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    application.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    application.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)_(\w+)_(\w+)"))
    application.add_handler(CallbackQueryHandler(handle_send_paid_report, pattern=r"send_paid_report_day_(\d+)_(\w+)"))
    application.add_handler(CallbackQueryHandler(handle_paid_next_day, pattern=r"^paid_next_day_(\w+)$"))
    application.add_handler(CallbackQueryHandler(handle_send_challenge_report, pattern=r"send_challenge_report_day_(\d+)_(\w+)"))
    application.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    application.add_handler(CallbackQueryHandler(buy_challenge, pattern=r"^buy_challenge_(\w+)$"))
    application.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    application.add_handler(CallbackQueryHandler(pay_course, pattern=r"^pay_course_(\w+)$"))
    application.add_handler(CallbackQueryHandler(send_receipt, pattern=r"^send_receipt_(\w+)$"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern=r"^confirm_payment_\d+_\w+$"))
    application.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern="^buy_nutrition_menu$"))
    application.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))
    application.add_handler(CallbackQueryHandler(handle_challenge_next_day, pattern=r"^challenge_next_(\w+)$"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))

    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))

    print("Бот запущен.")
    application.run_polling()

if __name__ == "__main__":
    main()
