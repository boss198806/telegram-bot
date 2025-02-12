from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Функция для создания главного меню
def main_menu() -> InlineKeyboardMarkup:
    """Создает главное меню для бота."""
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

# Функция для получения текста кнопки отправки отчета
def get_report_button_text(ctx: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    """Возвращает текст кнопки для отправки отчета в зависимости от пола и программы пользователя."""
    gender = ctx.user_data[user_id].get("gender", "male")
    prog = ctx.user_data[user_id].get("program", "home")
    return (("👩" if gender == "female" else "👨") + ("🏠" if prog == "home" else "🏋️") + " Отправить отчет 📹")
