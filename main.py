import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bonjour 👋")

async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot lancé.")

async def handle(request):
    return web.Response(text="Bot en ligne.")

async def run_webserver():
    port = int(os.environ.get("PORT", 8000))
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Serveur web lancé sur le port {port}")

async def main():
    await asyncio.gather(run_bot(), run_webserver())
    # On ne sortira jamais de cette attente
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
