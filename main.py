from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

import asyncio

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello from the bot!")

async def main():
    app = ApplicationBuilder().token("TON_TOKEN_ICI").build()

    app.add_handler(CommandHandler("start", start))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
