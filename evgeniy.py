import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Глобальные словари
evgeniy_user_scores = {}
evgeniy_user_status = {}
evgeniy_user_reports_sent = {}
evgeniy_user_waiting_for_video = {}
evgeniy_user_challenges = {}
evgeniy_user_waiting_for_receipt = {}

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

GROUP_ID = os.getenv("GROUP_ID")  # или импортируйте

######################
# Вспомогательные
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
async def evgeniy_free_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Логика похожа на anastasia_free_course, только используем evgeniy_* словари
    # ...

async def evgeniy_send_report_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

######################
# Челлендж
######################
async def evgeniy_challenge_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

######################
# Платный курс
######################
async def evgeniy_paid_course(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_send_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_handle_receipt(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_confirm_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_send_paid_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

async def evgeniy_paid_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    # Аналогично...
    ...

######################
# Мой кабинет
######################
async def evgeniy_my_cabinet(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    score = get_score(user_id)
    status = get_status(user_id)
    text = f"Ваш кабинет (Евгений)\nСтатус: {status}\nБаллы: {score}"
    await query.message.reply_text(text, reply_markup=evgeniy_main_menu())

######################
# Потратить баллы
######################
async def evgeniy_spend_points(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    score = get_score(user_id)
    text = f"Как потратить баллы (Евгений)? У вас {score} баллов..."
    await query.message.reply_text(text, reply_markup=evgeniy_main_menu())

######################
# КБЖУ
######################
async def evgeniy_kbju_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    ctx.user_data[user_id]["evgeniy_kbju_step"] = "gender"
    await query.message.reply_text("Введите пол (м/ж) [Евгений]:")

async def evgeniy_handle_kbju_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if "evgeniy_kbju_step" not in ctx.user_data[user_id]:
        return
    # Аналогичная логика
    ...

######################
# Назад
######################
async def evgeniy_back_to_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Меню Евгения", reply_markup=evgeniy_main_menu())
