import datetime
import requests
import openai
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# === Clés API ===
TELEGRAM_TOKEN = "7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc"
OPENAI_API_KEY = "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"
API_FOOTBALL_KEY = "d537cf906846aee79d1608e6644e5283bfebfd9da3d6f8e9763c6be14832afb0"

openai.api_key = OPENAI_API_KEY
ADMIN_ID = 7295542974

# === Stockage utilisateurs ===
users = set()

# === Menus ===

def build_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("📩 Contacter RAZOR", callback_data="contact")],
        [InlineKeyboardButton("🔥 Matchs du jour", callback_data="matchs_du_jour")],
        [InlineKeyboardButton("🔥 Pronostic du jour", callback_data="pronostics")],
        [InlineKeyboardButton("ℹ️ Infos sur le bot", callback_data="infos")]
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("📊 Statistiques", callback_data="stats")])
    keyboard.append([InlineKeyboardButton("❌ Quitter", callback_data="quit")])
    return InlineKeyboardMarkup(keyboard)

def build_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour au menu", callback_data="back")]])

# === API Football ===

def get_today_date():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def fetch_matches_today():
    url = f"https://apiv3.apifootball.com/?action=get_events&from={get_today_date()}&to={get_today_date()}&APIkey={API_FOOTBALL_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

# === GPT Razor ===

async def generate_pronostic(match):
    prompt = (
        f"Donne un pronostic simple pour ce match :\n"
        f"{match['match_hometeam_name']} vs {match['match_awayteam_name']} "
        f"({match['match_date']} {match['match_time']}).\n"
        f"Format : 'Victoire domicile', 'Match nul', ou 'Victoire extérieur', avec un pourcentage de confiance."
    )
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erreur GPT : {e}"

# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)
    message = (
        "🔥 *RAZOR LE RUSSE* 🇷🇺💯 PRONOSTICS GRATUITS 💯\n\n"
        "PRONOSTIC 1XBET, BETWINNER\n\n"
        "On valide les gars 💪💰\n\n"
        "✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅\n\n"
        "AVANTAGES DU CODE PROMO 2980 👇\n"
        "👉 Paris gratuits\n👉 Bonus retirables\n👉 Couverture pertes\n👉 Cotes boostées, etc.\n\n"
        "Actualise ton compte maintenant 👇"
    )
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=build_menu(user_id))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    users.add(user_id)
    await query.answer()

    match query.data:
        case "matchs_du_jour":
            await show_matches(query)
        case "pronostics":
            await show_pronostics(query)
        case "infos":
            await query.edit_message_text(
                "🤖 Bot officiel de *RAZOR* 🇷🇺\n\n🔥 Codes promo :\n- 1xBet : 2980\n- BetWinner : Razor25\n\nPariez responsablement 🍀",
                parse_mode="Markdown",
                reply_markup=build_back_menu()
            )
        case "contact":
            await query.edit_message_text("📧 razor@example.com\n📱 @RazorContact", reply_markup=build_back_menu())
        case "stats":
            if user_id == ADMIN_ID:
                await query.edit_message_text(f"📊 Utilisateurs uniques : {len(users)}", reply_markup=build_back_menu())
            else:
                await query.edit_message_text("⛔ Accès réservé à l'admin.", reply_markup=build_back_menu())
        case "quit":
            await query.edit_message_text("👋 Merci d'avoir utilisé le bot !")
        case "back":
            await query.edit_message_text("Menu principal :", reply_markup=build_menu(user_id))
        case _:
            await query.edit_message_text("Commande inconnue.", reply_markup=build_menu(user_id))

async def show_matches(query):
    await query.edit_message_text("⏳ Chargement des matchs du jour...")
    matches = fetch_matches_today()
    if not matches:
        await query.edit_message_text("❌ Aucun match trouvé aujourd'hui.", reply_markup=build_back_menu())
        return

    message = "🔥 *Matchs du jour — Football*\n\n"
    for m in matches[:10]:
        message += f"⚽ {m['match_hometeam_name']} vs {m['match_awayteam_name']}\n🕒 {m['match_time']} 📅 {m['match_date']}\n\n"
    await query.edit_message_text(message, parse_mode="Markdown", reply_markup=build_back_menu())

async def show_pronostics(query):
    await query.edit_message_text("⏳ Razor génère les pronostics...")
    matches = fetch_matches_today()
    if not matches:
        await query.edit_message_text("❌ Aucun match pour aujourd'hui.", reply_markup=build_back_menu())
        return

    messages = []
    for m in matches[:5]:
        prono = await generate_pronostic(m)
        messages.append(f"⚽ {m['match_hometeam_name']} vs {m['match_awayteam_name']} — {prono}")

    full_message = "🔥 *Pronostics du jour*\n\n" + "\n\n".join(messages)
    await query.edit_message_text(full_message, parse_mode="Markdown", reply_markup=build_back_menu())

# === Main ===

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
