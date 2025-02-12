import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import ContextTypes, CallbackContext

logger = logging.getLogger(__name__)

# Глобальные словари
anastasia_user_scores = {}
anastasia_user_status = {}
anastasia_user_reports_sent = {}
anastasia_user_waiting_for_video = {}
anastasia_user_challenges = {}
anastasia_user_waiting_for_receipt = {}

# Статусы
statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

# Пример group_id - можно импортировать из bot.py или из .env
# Но здесь оставим заглушку
GROUP_ID = os.getenv("GROUP_ID")  # Если хотите, импортируйте os.getenv("GROUP_ID")

###########################
# Вспомогательные функции
###########################
def get_instructor(user_id: int, ctx: ContextTypes.DEFAULT_TYPE) -> str:
    """Какой тренер выбран?"""
    return ctx.user_data.get(user_id, {}).get("instructor", "anastasia")

def get_score(user_id: int) -> int:
    return anastasia_user_scores.get(user_id, 0)

def add_score(user_id: int, amount: int) -> None:
    anastasia_user_scores[user_id] = anastasia_user_scores.get(user_id, 0) + amount

def get_status(user_id: int) -> str:
    return anastasia_user_status.get(user_id, statuses[0])

def set_status(user_id: int, new_status: str) -> None:
    anastasia_user_status[user_id] = new_status

def anastasia_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔥 Пройти бесплатный курс (АНАСТАСИЯ)", callback_data="anastasia_free_course")],
        [InlineKeyboardButton("💪 Челлендж (АНАСТАСИЯ)", callback_data="anastasia_challenge_menu")],
        [InlineKeyboardButton("📚 Платный курс (АНАСТАСИЯ)", callback_data="anastasia_paid_course")],
        [InlineKeyboardButton("👤 Мой кабинет (АНАСТАСИЯ)", callback_data="anastasia_my_cabinet")],
        [InlineKeyboardButton("💰 Как потратить баллы (АНАСТАСИЯ)", callback_data="anastasia_spend_points")],
        [InlineKeyboardButton("🍽 КБЖУ (АНАСТАСИЯ)", callback_data="anastasia_kbju")],
        [InlineKeyboardButton("🔙 Вернуться к выбору тренера", callback_data="choose_instructor_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

###########################
#       БЕСПЛАТНЫЙ КУРС
###########################
async def anastasia_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Текущее значение дня, если нет - ставим 1
    if "anastasia_free_day" not in ctx.user_data[user_id]:
        ctx.user_data[user_id]["anastasia_free_day"] = 1
    day = ctx.user_data[user_id]["anastasia_free_day"]
    if day > 5:
        await query.message.reply_text(
            "Вы уже прошли бесплатный курс Анастасии!",
            reply_markup=anastasia_main_menu()
        )
        return

    # Пример упражнений
    exercises = {
        1: ["Упражнение 1 (день 1)", "Упражнение 2 (день 1)"],
        2: ["Упражнение 1 (день 2)", "Упражнение 2 (день 2)"],
        3: ["Упражнение 1 (день 3)", "Упражнение 2 (день 3)"],
        4: ["Упражнение 1 (день 4)", "Упражнение 2 (день 4)"],
        5: ["Упражнение 1 (день 5)", "Упражнение 2 (день 5)"],
    }
    text = f"Бесплатный курс Анастасии, день {day}:\n\n" + "\n".join(exercises[day])
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Отправить видео-отчет (День {day})", callback_data=f"anastasia_send_report_{day}")]
    ])
    await query.message.reply_text(text, reply_markup=kb)

###########################
#       ОБРАБОТКА ВИДЕО
###########################
async def anastasia_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Ловим видео. Если бот ждет от пользователя видео (бесплатный курс / платный), обрабатываем.
    """
    user_id = update.message.from_user.id
    if user_id in anastasia_user_waiting_for_video:
        data = anastasia_user_waiting_for_video[user_id]
        if isinstance(data, int):
            # Бесплатный курс
            day = data
            # Отправляем в группу
            user_name = update.message.from_user.first_name
            if GROUP_ID:
                await ctx.bot.send_message(chat_id=GROUP_ID,
                    text=f"Видео-отчет от {user_name} (ID: {user_id}), день {day} (Анастасия)."
                )
                await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

            # Сохраняем, что отчет отправлен
            anastasia_user_reports_sent.setdefault(user_id, {})[day] = True
            add_score(user_id, 60)
            del anastasia_user_waiting_for_video[user_id]

            # Следующий день
            if "anastasia_free_day" not in ctx.user_data[user_id]:
                ctx.user_data[user_id]["anastasia_free_day"] = day
            ctx.user_data[user_id]["anastasia_free_day"] += 1
            if ctx.user_data[user_id]["anastasia_free_day"] <= 5:
                await update.message.reply_text(
                    f"Отчет за день {day} принят! Ваши баллы: {get_score(user_id)}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Следующий день", callback_data="anastasia_free_course")]
                    ])
                )
            else:
                set_status(user_id, statuses[1])  # «Бывалый»
                await update.message.reply_text(
                    f"Поздравляем! Вы завершили бесплатный курс Анастасии!\nБаллы: {get_score(user_id)}",
                    reply_markup=anastasia_main_menu()
                )
        elif isinstance(data, tuple) and data[0] == "paid":
            # Платный курс
            paid_day = data[1]
            user_name = update.message.from_user.first_name
            if GROUP_ID:
                await ctx.bot.send_message(chat_id=GROUP_ID,
                    text=f"[Платный] Видео-отчет от {user_name} (ID: {user_id}), день {paid_day} (Анастасия)."
                )
                await ctx.bot.send_video(chat_id=GROUP_ID, video=update.message.video.file_id)

            # Начисляем, удаляем из ожидания
            add_score(user_id, 30)
            del anastasia_user_waiting_for_video[user_id]

            # Переход к след. дню
            if ctx.user_data[user_id].get("anastasia_paid_day", 1) < 5:
                ctx.user_data[user_id]["anastasia_paid_day"] += 1
                await update.message.reply_text(
                    f"Отчет за платный день {paid_day} принят!\nБаллы: {get_score(user_id)}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Следующий день платного курса", callback_data="anastasia_paid_next_day")]
                    ])
                )
            else:
                set_status(user_id, statuses[3])  # «Профи»
                await update.message.reply_text(
                    f"Вы завершили платный курс Анастасии!\nБаллы: {get_score(user_id)}",
                    reply_markup=anastasia_main_menu()
                )
        else:
            await update.message.reply_text("Неизвестный формат данных ожидания (Анастасия).")
    else:
        # Видео пришло, но мы не ждем
        await update.message.reply_text("Я не жду видео-отчет от вас (Анастасия).")
