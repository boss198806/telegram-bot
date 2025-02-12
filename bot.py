import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from common import user_data, main_menu, logger
from instructors import *
from dotenv import load_dotenv
load_dotenv()  # Загружает переменные окружения из файла .env

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if ctx.args:
            try:
                ref = int(ctx.args[0])
                if ref != user_id:
                    # Начисляем баллы рефереру
                    for instructor in user_data:
                        if ref in user_data[instructor]['scores']:
                            user_data[instructor]['scores'][ref] += 100
                            break
            except ValueError:
                pass
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Евгений Курочкин", callback_data="instructor_evgeniy"),
             InlineKeyboardButton("💫 АНАСТАСИЯ", callback_data="instructor_anastasiya")]
        ])
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Выберите инструктора:", reply_markup=kb)
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")

async def handle_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    instructor = ctx.user_data.get(user_id, {}).get('instructor')
    
    if not instructor or user_id not in user_data[instructor]['waiting_for_video']:
        return await update.message.reply_text("Я не жду видео. Выберите задание в меню.")
    
    # Обработка видео
    data = user_data[instructor]['waiting_for_video'][user_id]
    if isinstance(data, int):  # Бесплатный курс
        day = data
        await ctx.bot.send_message(
            chat_id=os.getenv("TELEGRAM_GROUP_ID"),
            text=f"Видео-отчет от пользователя {update.message.from_user.first_name} (ID: {user_id}) за день {day}."
        )
        await ctx.bot.send_video(chat_id=os.getenv("TELEGRAM_GROUP_ID"), video=update.message.video.file_id)
        user_data[instructor]['scores'][user_id] = user_data[instructor]['scores'].get(user_id, 0) + 60
        del user_data[instructor]['waiting_for_video'][user_id]
        
        if day < 5:
            user_data[instructor]['current_day'][user_id] += 1
            await update.message.reply_text(
                f"Отчет принят! 🎉\nВаши баллы: {user_data[instructor]['scores'][user_id]}.\nГотовы к следующему дню?",
                reply_markup=main_menu()
            )
        else:
            user_data[instructor]['status'][user_id] = statuses[1]
            await update.message.reply_text("Поздравляем! Вы завершили курс! 🎉", reply_markup=main_menu())

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(
        lambda update, ctx: handle_instructor_selection(update, ctx, 'evgeniy'), 
        pattern="^instructor_evgeniy$"
    ))
    app.add_handler(CallbackQueryHandler(
        lambda update, ctx: handle_instructor_selection(update, ctx, 'anastasiya'), 
        pattern="^instructor_anastasiya$"
    ))
    app.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(handle_program, pattern="^program_"))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    app.run_polling()

if __name__ == "__main__":
    main()
