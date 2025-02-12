from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Глобальные переменные для хранения данных
user_data = {
    'evgeniy': {
        'scores': {},  # Баллы пользователей
        'status': {},  # Статусы пользователей
        'reports_sent': {},  # Отправленные отчеты
        'waiting_for_video': {},  # Ожидание видео
        'challenges': {},  # Челленджи
        'current_day': {}  # Текущий день курса
    },
    'anastasiya': {
        'scores': {},
        'status': {},
        'reports_sent': {},
        'waiting_for_video': {},
        'challenges': {},
        'current_day': {}
    }
}

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

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
        [InlineKeyboardButton("🔗 Реферальная ссылка", callback_data="referral")],
    ])

def get_report_button_text(ctx: ContextTypes.DEFAULT_TYPE, user_id: int):
    gender = ctx.user_data.get(user_id, {}).get("gender", "male")
    prog = ctx.user_data.get(user_id, {}).get("program", "home")
    return (("👩" if gender == "female" else "👨") + ("🏠" if prog == "home" else "🏋️") + " Отправить отчет 📹")
