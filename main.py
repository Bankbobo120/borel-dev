import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bbonjour 👋")

async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot lancé.")
    # Attendre que le bot tourne
    await asyncio.Event().wait()  # Boucle infinie propre

# Obtenir la bonne boucle d’événement (compatibilité Android)
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

loop.run_until_complete(run_bot())
