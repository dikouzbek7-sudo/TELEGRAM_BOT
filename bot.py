import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== SOZLAMALAR ==================
BOT_TOKEN = "8410700261:AAHr997ntSujjgECJdWTCxZPziLAhMxuY7I"
ADMIN_ID = 6417772942  # <-- o'zingning telegram ID

CARD_NUMBER = "9860 6067 5181 1385"
CARD_OWNER = "A/D"

# ================== DATA ==================
balances = {}          # user_id: balance
pending_topups = {}    # user_id: {"amount": int, "photo": file_id}

PRODUCTS = {
    "root": {
        "name": "ROOT UCHUN PANEL ☠️",
        "price": 20000,
        "ban": "50/50 tenovay ban",
        "desc": "Bu chit 100% hedshot beradi.\n95% bezban.\nO‘rnatish videosi mavjud.",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "wallhack": {
        "name": "Odam ko‘rsatadigan🕵️‍♂️",
        "price": 15000,
        "ban": "50/50 tenovay ban",
        "desc": "Bu chit odamlarni ko‘rsatadi.\n60% bezban.",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "panel40": {
        "name": "40% Panel🏆",
        "price": 10000,
        "ban": "0% ban",
        "desc": "30% hedshot.\nArzon va yengil.",
        "channel": "https://t.me/+FSu_4yZ1CRplNWEy",
    },
    "vzlom": {
        "name": "Free Fire Vzlom💎",
        "price": 25000,
        "ban": "Xavfsiz 50/50",
        "desc": "Almaz VIP bo‘ladi asosiy akk uchun tavsiya qilinmaydi xohlaganizcha almaz soladigan va xohlagan setingizni qoyadigan va olib tashlaydigan sayt manzili bilan qoshib beriladi akkountingizga xohlagan narsanigizni qoshishingiz yoki olib tashalashingiz mumkin.\n100% ishlaydi.",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "skin": {
        "name": "Skin Hack🛒",
        "price": 10000,
        "ban": "0% ban",
        "desc": "Skinlar ochiladi chitlar obozri kanaliga joylashtirilgan i.\nXavfsiz.",
        "channel": "https://t.me/+Kx14tGtORjxlMzdi",
    },
}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balances.setdefault(user_id, 0)

    text = (
        "👋 Assalomu alaykum!\n\n"
        "Bu bot orqali siz Free Fire uchun "
        "arzon va sifatli chitlarni sotib olishingiz mumkin.\n\n"
        "⬇️ Quyidagi menyudan foydalaning:"
    )

    keyboard = [
        [InlineKeyboardButton("🛒 Mahsulotlar", callback_data="products")],
        [InlineKeyboardButton("💰 Hisobim", callback_data="balance")],
        [InlineKeyboardButton("➕ Hisob to‘ldirish", callback_data="topup")],
    ]

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ================== BUTTONS ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = q.from_user.id
    balances.setdefault(user_id, 0)

    # -------- PRODUCTS LIST --------
    if data == "products":
        keyboard = []
        for key, p in PRODUCTS.items():
            keyboard.append([InlineKeyboardButton(p["name"], callback_data=f"prod_{key}")])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back")])

        await q.message.reply_text("🛒 Mahsulotlar:", reply_markup=InlineKeyboardMarkup(keyboard))

    # -------- PRODUCT INFO --------
    elif data.startswith("prod_"):
        key = data.replace("prod_", "")
        p = PRODUCTS[key]

        text = (
            f"📦 {p['name']}\n\n"
            f"{p['desc']}\n\n"
            f"🚫 Ban ehtimoli: {p['ban']}\n"
            f"💰 Narx: {p['price']} so‘m"
        )

        keyboard = [
            [InlineKeyboardButton("🛒 Sotib olish", callback_data=f"buy_{key}")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="products")],
        ]

        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # -------- BUY --------
    elif data.startswith("buy_"):
        key = data.replace("buy_", "")
        p = PRODUCTS[key]

        if balances[user_id] < p["price"]:
            await q.message.reply_text("❌ Mablag‘ yetarli emas")
            return

        balances[user_id] -= p["price"]

        await q.message.reply_text(
            f"✅ Sotib olindi!\n\n"
            f"📢 Chit shu kanalda:\n{p['channel']}"
        )

    # -------- BALANCE --------
    elif data == "balance":
        await q.message.reply_text(f"💰 Balansingiz: {balances[user_id]} so‘m")

    # -------- TOPUP --------
    elif data == "topup":
        context.user_data["await_amount"] = True
        await q.message.reply_text("💳 Qancha summa to‘ldirmoqchisiz?")

    # -------- BACK --------
    elif data == "back":
        await start(update, context)

    # -------- ADMIN CONFIRM --------
    elif data.startswith("confirm_"):
        uid = int(data.replace("confirm_", ""))
        if uid in pending_topups:
            balances[uid] += pending_topups[uid]["amount"]
            del pending_topups[uid]
            await q.message.reply_text("✅ To‘lov tasdiqlandi")
            await context.bot.send_message(uid, "✅ Hisobingiz to‘ldirildi")

    elif data.startswith("reject_"):
        uid = int(data.replace("reject_", ""))
        pending_topups.pop(uid, None)
        await q.message.reply_text("❌ To‘lov rad etildi")

# ================== TEXT HANDLER ==================
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get("await_amount"):
        amount = int(update.message.text)
        context.user_data["await_amount"] = False
        context.user_data["await_photo"] = True
        context.user_data["amount"] = amount

        await update.message.reply_text(
            f"💳 Karta:\n{CARD_NUMBER}\n{CARD_OWNER}\n\n"
            f"{amount} so‘m to‘lang va chek rasmini yuboring"
        )

# ================== PHOTO HANDLER ==================
async def photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get("await_photo"):
        context.user_data["await_photo"] = False
        amount = context.user_data["amount"]
        photo = update.message.photo[-1].file_id

        pending_topups[user_id] = {"amount": amount, "photo": photo}

        keyboard = [
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}"),
            ]
        ]

        await context.bot.send_photo(
            ADMIN_ID,
            photo,
            caption=f"💰 To‘lov so‘rovi\nUser: {user_id}\nSumma: {amount}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        await update.message.reply_text("⏳ To‘lov admin tomonidan tekshirilmoqda")

# ================== MAIN ==================
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texts))
    app.add_handler(MessageHandler(filters.PHOTO, photos))

    print("✅ Bot ishga tushdi")
    app.run_polling()

if __name__ == "__main__":
    main()




