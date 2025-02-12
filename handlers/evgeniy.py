import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# Логирование
logger = logging.getLogger(__name__)

# Глобальные словари для Евгения
evgeniy_user_scores = {}
evgeniy_user_status = {}
evgeniy_user_reports_sent = {}
evgeniy_user_waiting_for_video = {}
evgeniy_user_challenges = {}
evgeniy_user_waiting_for_receipt = {}

# Статусы
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Загрузка переменных окружения
GROUP_ID = os.getenv("GROUP_ID")  # или импортируйте через load_dotenv()

######################
# Вспомогательные функции
######################
def get_score(user_id: int) -> int:
    return evgeniy_user_scores.get(user_id, 0)

def add_score(user_id: int, amount: int) -> None:
    evgeniy_user_scores[user_id] = evgeniy_user_scores.get(user_id, 0) + amount

def get_status(user_id: int) -> str:
    return evgeniy_user_status.get(user_id, statuses[0])

def set_status(user_id: int, new_status: str) -> None:
    evgeniy_user_status[user_id] = new_status

def evgeniy_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔥 Бесплатный курс (ЕВГЕНИЙ)", callback_data="evgeniy_free_course")],
        [InlineKeyboardButton("💪 Челлендж (ЕВГЕНИЙ)", callback_data="evgeniy_challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс (ЕВГЕНИЙ)", callback_data="evgeniy_paid_course")],
        [InlineKeyboardButton("👤 Мой кабинет (ЕВГЕНИЙ)", callback_data="evgeniy_my_cabinet")],
        [InlineKeyboardButton("💰 Как потратить баллы (ЕВГЕНИЙ)", callback_data="evgeniy_spend_points")],
        [InlineKeyboardButton("🍽 КБЖУ (ЕВГЕНИЙ)", callback_data="evgeniy_kbju")],
        [InlineKeyboardButton("🔙 Вернуться к выбору тренера", callback_data="choose_instructor_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

######################
# Бесплатный курс
######################
course = {
    1: [
        "1️⃣ Присед с махом 3x20 [Видео](https://t.me/c/2241417709/363/364)",
        "2️⃣ Ягодичный мост 3x30 [Видео](https://t.me/c/2241417709/381/382)",
        "3️⃣ Велосипед 3x15 [Видео](https://t.me/c/2241417709/278/279)"
    ],
    2: [
        "1️⃣ Отжимания от пола 3x15 [Видео](https://t.me/c/2241417709/167/168)",
        "2️⃣ Лодочка прямые руки 3x30 [Видео](https://t.me/c/2241417709/395/396)",
        "3️⃣ Полные подъёмы корпуса 3x20 [Видео](https://t.me/c/2241417709/274/275)"
    ],
    3: [
        "1️⃣ Выпады назад 3x15 [Видео](https://t.me/c/2241417709/155/156)",
        "2️⃣ Махи в бок с колен 3x20 [Видео](https://t.me/c/2241417709/385/386)",
        "3️⃣ Косые с касанием пяток 3x15 [Видео](https://t.me/c/2241417709/282/283)"
    ],
    4: [
        "1️⃣ Поочередные подъемы с гантелями 4x20 [Видео](https://t.me/c/2241417709/226/227)",
        "2️⃣ Узкие отжимания 3x15 [Видео](https://t.me/c/2241417709/256/257)",
        "3️⃣ Планка 3x1 мин [Видео](https://t.me/c/2241417709/286/296)"
    ],
    5: [
        "1️⃣ Присед со штангой (без штанги) 3x20 [Видео](https://t.me/c/2241417709/140/141)",
        "2️⃣ Махи под 45 с резинкой 3x20 [Видео](https://t.me/c/2241417709/339/340)",
        "3️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"
    ]
}

async def evgeniy_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Логика для бесплатного курса
    if "evgeniy_free_day" not in ctx.user_data[user_id]:
        ctx.user_data[user_id]["evgeniy_free_day"] = 1
    day = ctx.user_data[user_id]["evgeniy_free_day"]
    if day > 5:
        await query.message.reply_text(
            "Вы уже прошли бесплатный курс Евгения!",
            reply_markup=evgeniy_main_menu()
        )
        return

    # Упражнения для курса
    text = f"Бесплатный курс Евгения, день {day}:\n\n" + "\n".join(course[day])
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Отправить видео-отчет (День {day})", callback_data=f"evgeniy_send_report_{day}")]
    ])
    await query.message.reply_text(text, reply_markup=kb)

######################
# Видео отчеты и начисление баллов
######################
async def evgeniy_send_report_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data  # evgeniy_send_report_1
    day = int(data.split("_")[-1])

    # Проверим, не отправлял ли уже
    if evgeniy_user_reports_sent.get(user_id, {}).get(day):
        await query.message.reply_text("Вы уже отправляли отчет за этот день!")
        return

    evgeniy_user_waiting_for_video[user_id] = day
    await query.message.reply_text(f"Пришлите видео-отчет за день {day} (Евгений).")

async def evgeniy_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Ловим видео. Если бот ждет от пользователя видео (бесплатный курс), обрабатываем.
    """
    user_id = update.message.from_user.id
    if user_id in evgeniy_user_waiting_for_video:
        data = evgeniy_user_waiting_for_video[user_id]
        if isinstance(data, int):
            # Бесплатный курс
            day = data
            # Отправляем в группу
            user_name = update.message.from_user.first_name
            if GROUP_ID:
                await ctx.bot.send_message(chat_id=GROUP_ID,
                    text=f"Видео-отчет от {user_name} (ID: {user_id}), день {day} (Евгений)."
                )
                await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

            # Сохраняем, что отчет отправлен
            evgeniy_user_reports_sent.setdefault(user_id, {})[day] = True
            add_score(user_id, 60)  # Начисляем баллы за отчет
            del evgeniy_user_waiting_for_video[user_id]

            # Следующий день
            if "evgeniy_free_day" not in ctx.user_data[user_id]:
                ctx.user_data[user_id]["evgeniy_free_day"] = day
            ctx.user_data[user_id]["evgeniy_free_day"] += 1
            if ctx.user_data[user_id]["evgeniy_free_day"] <= 5:
                await update.message.reply_text(
                    f"Отчет за день {day} принят! Ваши баллы: {get_score(user_id)}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Следующий день (бесплатный курс)", callback_data="evgeniy_free_course")]
                    ])
                )
            else:
                set_status(user_id, statuses[1])  # «Бывалый»
                await update.message.reply_text(
                    f"Вы завершили бесплатный курс Евгения!\nБаллы: {get_score(user_id)}",
                    reply_markup=evgeniy_main_menu()
                )
        else:
            await update.message.reply_text("Неизвестный формат данных ожидания (Евгений).")
    else:
        # Видео пришло, но мы не ждем
        await update.message.reply_text("Я не жду видео-отчет от вас (Евгений).")

######################
# Назад
######################
async def evgeniy_back_to_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Меню Евгения", reply_markup=evgeniy_main_menu())
