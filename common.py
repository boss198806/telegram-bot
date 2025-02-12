from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Глобальные словари для отслеживания состояния пользователей
user_scores = {}
user_status = {}
user_reports_sent = {}
user_waiting_for_video = {}
user_waiting_for_challenge_video = {}
user_waiting_for_receipt = {}
user_challenges = {}

statuses = ["Новичок", "Бывалый", "Чемпион", "Профи"]

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
        [InlineKeyboardButton("🔗 Реферальная ссылка", callback_data="referral")]
    ])

def get_report_button_text(ctx, user_id: int) -> str:
    """Возвращает текст кнопки для отправки отчета в зависимости от пола и программы пользователя."""
    gender = ctx.user_data[user_id].get("gender", "male")
    prog = ctx.user_data[user_id].get("program", "home")
    return (("👩" if gender == "female" else "👨") + ("🏠" if prog == "home" else "🏋️") + " Отправить отчет 📹")

def update_user_score(user_id: int, points: int):
    """Обновляет баллы пользователя в глобальном словаре."""
    if user_id not in user_scores:
        user_scores[user_id] = 0
    user_scores[user_id] += points

def update_user_status(user_id: int, status_index: int):
    """Обновляет статус пользователя в глобальном словаре."""
    if user_id not in user_status:
        user_status[user_id] = statuses[0]  # Начальный статус "Новичок"
    if status_index < len(statuses):
        user_status[user_id] = statuses[status_index]
