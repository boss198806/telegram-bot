from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging
from common import main_menu, handle_send_report, handle_video, handle_receipt, confirm_payment
from common import handle_my_cabinet, handle_about_me, handle_earn_points, handle_spend_points, handle_back
from common import handle_nutrition_menu, handle_buy_nutrition_menu, handle_referral, handle_challenge_next_day

logger = logging.getLogger(__name__)

async def handle_challenges(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_challenges.get(user_id):
        await send_challenge_task(query.message, user_id)
    elif user_scores.get(user_id, 0) >= 300:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Купить доступ за 300 баллов", callback_data="buy_challenge")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ])
        await query.message.reply_text("Доступ к челленджам стоит 300 баллов. Хотите приобрести?", reply_markup=kb)
    else:
        await query.message.reply_text(f"⚠️ Для доступа к челленджам нужно 300 баллов.\nУ вас: {user_scores.get(user_id, 0)} баллов.\nПродолжайте тренировки!")

async def buy_challenge(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_scores.get(user_id, 0) >= 300:
        user_scores[user_id] -= 300
        user_challenges[user_id] = {"current_day": 1}
        await query.message.reply_text("✅ Доступ к челленджам открыт!", reply_markup=main_menu())
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("⚠️ Недостаточно баллов для покупки доступа!")

async def send_challenge_task(message, user_id: int):
    day = user_challenges[user_id]["current_day"]
    exercises = {
        1: ["1️⃣ Выпады назад 40 раз [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
            "3️⃣ Велосипед 30 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"],
        2: ["1️⃣ Присед со штангой 30 раз [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Отжимания с отрывом рук 25 раз [Видео](https://t.me/c/2241417709/393/394)",
            "3️⃣ Полные подъёмы корпуса 30 раз [Видео](https://t.me/c/2241417709/274/275)"],
        3: ["1️⃣ Планка 3 мин [Видео](https://t.me/c/2241417709/286/296)",
            "2️⃣ Подъёмы ног лёжа 3x15 [Видео](https://t.me/c/2241417709/367/368)"],
        4: ["1️⃣ Выпады назад 60 раз [Видео](https://t.me/c/2241417709/155/156)",
            "2️⃣ Лодочка + сгибание в локтях 50 раз [Видео](https://t.me/c/2241417709/183/184)",
            "3️⃣ Велосипед 50 на каждую ногу [Видео](https://t.me/c/2241417709/278/279)"],
        5: ["1️⃣ Присед со штангой 50 раз [Видео](https://t.me/c/2241417709/140/141)",
            "2️⃣ Отжимания с отрывом рук 40 раз [Видео](https://t.me/c/2241417709/393/394)",
            "3️⃣ Полные подъёмы корпуса 50 раз [Видео](https://t.me/c/2241417709/274/275)"],
    }.get(day, [])
    text = f"💪 **Челлендж: День {day}** 💪\n\n" + "\n".join(exercises)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Следующий день", callback_data="challenge_next")]]
                              if day < 5 else [[InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data="back")]])
    await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_challenge_next_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in user_challenges:
        return await query.answer("Сначала купите челлендж! 🚧")
    day = user_challenges[user_id]["current_day"]
    if day < 5:
        user_challenges[user_id]["current_day"] = day + 1
        await send_challenge_task(query.message, user_id)
    else:
        await query.message.reply_text("Поздравляем, вы завершили челлендж! 🎉", reply_markup=main_menu())
        del user_challenges[user_id]
