import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Команда /start.
    Показываем кнопки выбора тренера.
    """
    user_id = update.effective_user.id

    # Реферальная ссылка (если передаётся /start <args>)
    if ctx.args:
        try:
            ref = int(ctx.args[0])
            if ref != user_id:
                # здесь можно начислить реферальный бонус рефереру
                pass
        except ValueError:
            pass

    await update.message.reply_text(
        "Выбери для себя фитнес-инструктора:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_evgeniy"),
                InlineKeyboardButton("💫 Анастасия", callback_data="instructor_anastasia"),
            ],
            [InlineKeyboardButton("🏋️ Тренер 3", callback_data="instructor_3")],
            [InlineKeyboardButton("🤼 Тренер 4", callback_data="instructor_4")],
            [InlineKeyboardButton("🤸 Тренер 5", callback_data="instructor_5")]
        ])
    )

async def handle_instructor_selection(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Пользователь выбрал тренера (instructor_evgeniy / instructor_anastasia / instructor_3...).
    Сохраняем это в ctx.user_data[user_id].
    """
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data  # например 'instructor_evgeniy'
    if data == "instructor_evgeniy":
        ctx.user_data[user_id] = {"instructor": "evgeniy"}
        await query.message.reply_text(
            "Вы выбрали: Евгений Курочкин!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Меню Евгения", callback_data="evgeniy_free_course")]
            ])
        )
    elif data == "instructor_anastasia":
        ctx.user_data[user_id] = {"instructor": "anastasia"}
        await query.message.reply_text(
            "Вы выбрали: Анастасия!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Меню Анастасии", callback_data="anastasia_free_course")]
            ])
        )
    else:
        # Тренеры 3,4,5 - placeholder
        ctx.user_data[user_id] = {"instructor": data}
        await query.message.reply_text(
            "Функционал для этого тренера ещё не реализован.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="choose_instructor_back")]
            ])
        )

async def handle_instructor_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Возврат к начальному выбору тренера.
    """
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "Вы вернулись к выбору тренера. Нажмите /start или перезапустите бота."
    )
