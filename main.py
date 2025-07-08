import os
import asyncio
import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import openai
from aiohttp import web

# --- CONFIG ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "d537cf906846aee79d1608e6644e5283bfebfd9da3d6f8e9763c6be14832afb0")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # Ton ID Telegram

openai.api_key = OPENAI_API_KEY

# --- USERS ---
users = set()

# --- MENUS ---

def build_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("📩 Contacter RAZOR", callback_data='contact')],
        [InlineKeyboardButton("🔥 Matchs du jour", callback_data='matchs_du_jour')],
        [InlineKeyboardButton("🔥 Pronostic du jour", callback_data='pronostics')],
        [InlineKeyboardButton("ℹ️ Infos bot", callback_data='infos')],
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("📊 Statistiques", callback_data='stats')])
    keyboard.append([InlineKeyboardButton("❌ Quitter", callback_data='quit')])
    return InlineKeyboardMarkup(keyboard)

def build_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour au menu principal", callback_data='back')]])

# --- FOOTBALL API ---

def get_today_date():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def fetch_matches_today():
    url = f"https://apiv3.apifootball.com/?action=get_events&from={get_today_date()}&to={get_today_date()}&APIkey={API_FOOTBALL_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

# --- OPENAI PRONOSTICS ---

async def generate_pronostic(match):
    prompt = (
        f"Donne un pronostic simple pour ce match :\n"
        f"{match['match_hometeam_name']} vs {match['match_awayteam_name']} "
        f"({match['match_date']} {match['match_time']}).\n"
        "Format : 'Victoire domicile', 'Match nul', ou 'Victoire extérieur', avec un pourcentage de confiance."
    )
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erreur lors du pronostic : {str(e)}"

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)
    texte = (
        "🔥 RAZOR LE RUSSE. 🇷🇺💯 PRONOSTICS GRATUITS 💯\n\n"
        "PRONOSTIC 1XBET, BETWINNER\n\n"
        "On valide les gars 💪🤞🏾☘💰\n\n"
        "Avantages code promo 2980 👇\n"
        "👉 Paris gratuits\n"
        "👉 Remises sur pertes\n"
        "👉 Couverture sécurité\n"
        "👉 Bonus retirables\n"
        "👉 Retraits élevés\n"
        "👉 Bonus booster côtes, etc.\n\n"
        "ACTUALISE TON COMPTE ici 👈"
    )
    await update.message.reply_text(texte, reply_markup=build_menu(user_id))

async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("⏳ Chargement des matchs du jour...")
    matches = fetch_matches_today()
    if not matches:
        await update.callback_query.edit_message_text("❌ Aucun match trouvé pour aujourd'hui.", reply_markup=build_back_menu())
        return

    text = "🔥 *Matchs du jour - Football*\n\n"
    for m in matches[:10]:
        text += f"⚽ {m['match_hometeam_name']} vs {m['match_awayteam_name']}\n🕒 {m['match_time']} 📅 {m['match_date']}\n\n"

    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_back_menu())

async def show_pronostics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("⏳ Chargement des pronostics Razor...")
    matches = fetch_matches_today()
    if not matches:
        await update.callback_query.edit_message_text("❌ Aucun match trouvé aujourd'hui.", reply_markup=build_back_menu())
        return

    messages = []
    for match in matches[:5]:
        pronostic = await generate_pronostic(match)
        messages.append(
            f"⚽ {match['match_hometeam_name']} vs {match['match_awayteam_name']}\n"
            f"🕒 {match['match_time']} 📅 {match['match_date']}\n"
            f"🎯 Razor : {pronostic}\n\n"
        )

    full_message = "🔥 *Pronostics du jour — Football*\n\n" + "".join(messages)
    await update.callback_query.edit_message_text(full_message, parse_mode="Markdown", reply_markup=build_back_menu())

async def informations_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = (
        "🔥 Bienvenue sur le bot officiel de RAZOR ! 🔥\n\n"
        "Bot conçu par RAZOR 🇷🇺, pronostiqueur reconnu 🎯.\n\n"
        "✨ Codes promo exclusifs :\n"
        "- 1xBet : 2980\n"
        "- BetWinner : 2980 ou Razor25\n\n"
        "Pariez responsablement 🍀"
    )
    await update.callback_query.edit_message_text(texte, parse_mode='Markdown', reply_markup=build_back_menu())

async def contacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = (
        "📩 Pour contacter RAZOR :\n\n"
        "📧 Email : razor@example.com\n"
        "📱 Telegram : @RazorContact\n\n"
        "N'hésitez pas à poser vos questions !"
    )
    await update.callback_query.edit_message_text(texte, reply_markup=build_back_menu())

async def afficher_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    if user_id != ADMIN_ID:
        await update.callback_query.edit_message_text("❌ Statistiques réservées à l'administrateur.", reply_markup=build_back_menu())
        return
    text = f"📊 Nombre d'utilisateurs uniques : {len(users)}"
    await update.callback_query.edit_message_text(text, reply_markup=build_back_menu())

async def quitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Merci d'avoir utilisé le bot. À bientôt !")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    data = query.data

    users.add(user_id)

    if data == 'matchs_du_jour':
        await show_matches(update, context)
    elif data == 'pronostics':
        await show_pronostics(update, context)
    elif data == 'infos':
        await informations_bot(update, context)
    elif data == 'contact':
        await contacter(update, context)
    elif data == 'stats':
        await afficher_stats(update, context)
    elif data == 'quit':
        await quitter(update, context)
    elif data == 'back':
        await query.edit_message_text(
            "Bienvenue sur le bot de pronostics sportifs ! Que souhaitez-vous faire ?",
            reply_markup=build_menu(user_id)
        )
    else:
        await query.edit_message_text("Option inconnue. Réessayez.")

# --- Serveur Web (keep alive Render) ---

async def handle_web(request):
    return web.Response(text="Bot RAZOR est en ligne. ⚡️")

async def run_webserver():
    port = int(os.environ.get("PORT", 8000))
    app = web.Application()
    app.router.add_get('/', handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Serveur web lancé sur le port {port}")

# --- MAIN ---

async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot lancé.")
    # Ne jamais terminer pour que le bot reste actif
    await asyncio.Event().wait()

async def main():
    await asyncio.gather(run_bot(), run_webserver())

if __name__ == "__main__":
    asyncio.run(main())
