import logging
import os
from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# Импортируем функции-хендлеры
from handlers.common import start, handle_instructor_selection, handle_instructor_back
from handlers.anastasia import (
    anastasia_free_course, anastasia_send_report_callback, anastasia_handle_video,
    anastasia_challenge_menu, anastasia_buy_challenge, anastasia_challenge_next_day,
    anastasia_paid_course, anastasia_send_receipt, anastasia_handle_receipt,
    anastasia_confirm_payment, anastasia_send_paid_report, anastasia_paid_next_day,
    anastasia_my_cabinet, anastasia_spend_points, anastasia_kbju_start,
    anastasia_handle_kbju_text, anastasia_back_to_menu
)
from handlers.evgeniy import (
    evgeniy_free_course, evgeniy_send_report_callback, evgeniy_handle_video,
    evgeniy_challenge_menu, evgeniy_buy_challenge, evgeniy_challenge_next_day,
    evgeniy_paid_course, evgeniy_send_receipt, evgeniy_handle_receipt,
    evgeniy_confirm_payment, evgeniy_send_paid_report, evgeniy_paid_next_day,
    evgeniy_my_cabinet, evgeniy_spend_points, evgeniy_kbju_start,
    evgeniy_handle_kbju_text, evgeniy_back_to_menu
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

    level=logging.INFO
)

    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv(\"TELEGRAM_TOKEN\")
GROUP_ID = os.getenv(\"GROUP_ID\")

def run_bot() -> None:
    app = Application.builder().token(TOKEN).build()

    # /start
    app.add_handler(CommandHandler(\"start\", start))

    # Общие
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern=\"^instructor_\"))
    app.add_handler(CallbackQueryHandler(handle_instructor_back, pattern=\"^choose_instructor_back$\"))

    # Анастасия
    app.add_handler(CallbackQueryHandler(anastasia_free_course, pattern=\"^anastasia_free_course$\"))
    app.add_handler(CallbackQueryHandler(anastasia_send_report_callback, pattern=r\"^anastasia_send_report_\\d+$\"))
    app.add_handler(MessageHandler(filters.VIDEO, anastasia_handle_video))
    app.add_handler(CallbackQueryHandler(anastasia_challenge_menu, pattern=\"^anastasia_challenge_menu$\"))
    app.add_handler(CallbackQueryHandler(anastasia_buy_challenge, pattern=\"^anastasia_buy_challenge$\"))
    app.add_handler(CallbackQueryHandler(anastasia_challenge_next_day, pattern=\"^anastasia_challenge_next$\"))
    app.add_handler(CallbackQueryHandler(anastasia_paid_course, pattern=\"^anastasia_paid_course$\"))
    app.add_handler(CallbackQueryHandler(anastasia_send_receipt, pattern=\"^anastasia_send_receipt$\"))
    app.add_handler(MessageHandler(filters.PHOTO, anastasia_handle_receipt))
    app.add_handler(CallbackQueryHandler(anastasia_confirm_payment, pattern=\"^anastasia_confirm_payment_\"))
    app.add_handler(CallbackQueryHandler(anastasia_send_paid_report, pattern=r\"^anastasia_paid_send_report_\\d+$\"))
    app.add_handler(CallbackQueryHandler(anastasia_paid_next_day, pattern=\"^anastasia_paid_next_day$\"))
    app.add_handler(CallbackQueryHandler(anastasia_my_cabinet, pattern=\"^anastasia_my_cabinet$\"))
    app.add_handler(CallbackQueryHandler(anastasia_spend_points, pattern=\"^anastasia_spend_points$\"))
    app.add_handler(CallbackQueryHandler(anastasia_kbju_start, pattern=\"^anastasia_kbju$\"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anastasia_handle_kbju_text))
    app.add_handler(CallbackQueryHandler(anastasia_back_to_menu, pattern=\"^anastasia_back_to_menu$\"))
    
    # Евгений
    app.add_handler(CallbackQueryHandler(evgeniy_free_course, pattern=\"^evgeniy_free_course$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_send_report_callback, pattern=r\"^evgeniy_send_report_\\d+$\"))
    app.add_handler(MessageHandler(filters.VIDEO, evgeniy_handle_video))
    app.add_handler(CallbackQueryHandler(evgeniy_challenge_menu, pattern=\"^evgeniy_challenge_menu$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_buy_challenge, pattern=\"^evgeniy_buy_challenge$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_challenge_next_day, pattern=\"^evgeniy_challenge_next$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_paid_course, pattern=\"^evgeniy_paid_course$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_send_receipt, pattern=\"^evgeniy_send_receipt$\"))
    app.add_handler(MessageHandler(filters.PHOTO, evgeniy_handle_receipt))
    app.add_handler(CallbackQueryHandler(evgeniy_confirm_payment, pattern=\"^evgeniy_confirm_payment_\"))
    app.add_handler(CallbackQueryHandler(evgeniy_send_paid_report, pattern=r\"^evgeniy_paid_send_report_\\d+$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_paid_next_day, pattern=\"^evgeniy_paid_next_day$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_my_cabinet, pattern=\"^evgeniy_my_cabinet$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_spend_points, pattern=\"^evgeniy_spend_points$\"))
    app.add_handler(CallbackQueryHandler(evgeniy_kbju_start, pattern=\"^evgeniy_kbju$\"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, evgeniy_handle_kbju_text))
    app.add_handler(CallbackQueryHandler(evgeniy_back_to_menu, pattern=\"^evgeniy_back_to_menu$\"))
    
    logger.info(\"Бот запущен и готов к работе. 🚀\")
    app.run_polling()

if __name__ == \"__main__\":
    run_bot()

