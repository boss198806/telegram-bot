import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from common import main_menu, start_free_course, handle_send_report, handle_video, handle_receipt, confirm_payment
from common import handle_my_cabinet, handle_about_me, handle_earn_points, handle_spend_points, handle_back
from common import handle_nutrition_menu, handle_buy_nutrition_menu, handle_referral, handle_challenge_next_day
from evgeniy import handle_instructor_selection, handle_free_course_callback, handle_gender, handle_program
from evgeniy import handle_paid_course, handle_send_receipt, handle_paid_gender, handle_paid_program_gym, handle_paid_program_home
from evgeniy import handle_send_paid_report, handle_paid_next_day
from anastasia import handle_challenges, buy_challenge, send_challenge_task

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Retrieve environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

if not TOKEN or not GROUP_ID:
    logger.error("Environment variables TOKEN or GROUP_ID are not set.")
    raise ValueError("Environment variables TOKEN or GROUP_ID are not set.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_instructor_selection, pattern="^instructor_"))
    app.add_handler(CallbackQueryHandler(handle_free_course_callback, pattern="^(free_course|next_day)$"))
    app.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    app.add_handler(CallbackQueryHandler(handle_send_report, pattern=r"send_report_day_(\d+)"))
    app.add_handler(CallbackQueryHandler(handle_challenges, pattern="^challenge_menu$"))
    app.add_handler(CallbackQueryHandler(buy_challenge, pattern="^buy_challenge$"))
    app.add_handler(CallbackQueryHandler(handle_paid_course, pattern="^paid_course$"))
    app.add_handler(CallbackQueryHandler(handle_send_receipt, pattern="^send_receipt$"))
    app.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment_"))
    app.add_handler(CallbackQueryHandler(handle_send_paid_report, pattern=r"^paid_video_day_(\d+)$"))
    app.add_handler(CallbackQueryHandler(handle_paid_next_day, pattern="^paid_next_day$"))
    app.add_handler(CallbackQueryHandler(handle_paid_gender, pattern="^paid_gender_"))
    app.add_handler(CallbackQueryHandler(handle_paid_program_gym, pattern="^paid_program_gym$"))
    app.add_handler(CallbackQueryHandler(handle_paid_program_home, pattern="^paid_program_home$"))
    app.add_handler(CallbackQueryHandler(handle_my_cabinet, pattern="^my_cabinet$"))
    app.add_handler(CallbackQueryHandler(handle_about_me, pattern="^about_me$"))
    app.add_handler(CallbackQueryHandler(handle_earn_points, pattern="^earn_points$"))
    app.add_handler(CallbackQueryHandler(handle_spend_points, pattern="^spend_points$"))
    app.add_handler(CallbackQueryHandler(handle_nutrition_menu, pattern="^nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_buy_nutrition_menu, pattern="^buy_nutrition_menu$"))
    app.add_handler(CallbackQueryHandler(handle_referral, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(handle_challenge_next_day, pattern="^challenge_next$"))
    app.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    print("Бот запущен и готов к работе. 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
