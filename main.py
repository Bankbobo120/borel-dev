import requests
import datetime
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
import openai

# Clés API (remplace avec les tiennes)
TELEGRAM_TOKEN = "TON_TOKEN_TELEGRAM"
OPENAI_API_KEY = "TA_CLE_OPENAI"
API_FOOTBALL_KEY = "TA_CLE_API_FOOTBALL"

openai.api_key = OPENAI_API_KEY
ADMIN_ID = 123456789  # Ton ID Telegram ici
users = set()  # Stockage des utilisateurs


# === UI ===
def build_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("📩 Contacter RAZOR", callback_data='contact')],
        [InlineKeyboardButton("🔥 Matchs du jour", callback_data='matchs_du_jour')],
        [InlineKeyboardButton("🔥 Pronostic du jour", callback_data='pronostics')],
        [InlineKeyboardButton("ℹ️ Informations sur le bot", callback_data='infos')],
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("📊 Statistiques du bot", callback_data='stats')])
    keyboard.append([InlineKeyboardButton("❌ Quitter", callback_data='quit')])
    return InlineKeyboardMarkup(keyboard)

def build_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data='back')]])


# === API FOOTBALL ===
def get_today_date():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def fetch_matches_today():
    url = f"https://apiv3.apifootball.com/?action=get_events&from={get_today_date()}&to={get_today_date()}&APIkey={API_FOOTBALL_KEY}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []


# === OPENAI ===
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
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erreur lors du pronostic : {str(e)}"


# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)
    texte = (
        "🔥 RAZOR LE RUSSE. 🇷🇺 PRONOSTICS GRATUITS 💯\n\n"
        "PRONOSTIC 1XBET, BETWINNER\n\n"
        "Code promo 2980 pour bonus exclusifs 👇"
    )
    await update.message.reply_text(texte, reply_markup=build_menu(user_id))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()
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
        await query.edit_message_text("Menu principal :", reply_markup=build_menu(user_id))
    else:
        await query.edit_message_text("Option inconnue. Réessayez.")

async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("⏳ Chargement des matchs...")
    matches = fetch_matches_today()
    if not matches:
        await update.callback_query.edit_message_text("❌ Aucun match aujourd'hui.", reply_markup=build_back_menu())
        return

    text = "🔥 *Matchs du jour - Football*\n\n"
    for m in matches[:10]:
        text += f"⚽ {m['match_hometeam_name']} vs {m['match_awayteam_name']}\n🕒 {m['match_time']} 📅 {m['match_date']}\n\n"

    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_back_menu())

async def show_pronostics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("⏳ Génération des pronostics...")
    matches = fetch_matches_today()
    if not matches:
        await update.callback_query.edit_message_text("❌ Aucun match aujourd'hui.", reply_markup=build_back_menu())
        return

    messages = []
    for match in matches[:5]:
        pronostic = await generate_pronostic(match)
        messages.append(
            f"⚽ {match['match_hometeam_name']} vs {match['match_awayteam_name']}\n"
            f"🕒 {match['match_time']} 📅 {match['match_date']}\n"
            f"🎯 Razor : {pronostic}\n\n"
        )

    final_text = "🔥 *Pronostics du jour*\n\n" + "".join(messages)
    await update.callback_query.edit_message_text(final_text, parse_mode="Markdown", reply_markup=build_back_menu())

async def informations_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = (
        "🔥 Bienvenue sur le bot RAZOR !\n\n"
        "📢 Pronostics gratuits tous les jours\n"
        "🎯 Contact : @RazorContact\n"
        "💸 Codes promo : 2980"
    )
    await update.callback_query.edit_message_text(texte, parse_mode="Markdown", reply_markup=build_back_menu())

async def contacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = "📩 Contact :\n\n📱 Telegram : @RazorContact\n📧 Email : razor@example.com"
    await update.callback_query.edit_message_text(texte, reply_markup=build_back_menu())

async def afficher_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.from_user.id != ADMIN_ID:
        await update.callback_query.edit_message_text("❌ Accès réservé à l'administrateur.", reply_markup=build_back_menu())
        return
    await update.callback_query.edit_message_text(f"📊 Utilisateurs uniques : {len(users)}", reply_markup=build_back_menu())

async def quitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Merci d’avoir utilisé le bot. À bientôt !")

# === MAIN ===

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
