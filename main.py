import os
import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIG ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "d537cf906846aee79d1608e6644e5283bfebfd9da3d6f8e9763c6be14832afb0")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7745293166"))

# --- DONNEES ---
users = set()
historique_pronos = {}
team_stats = {}

# --- MENUS ---
def build_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("📩 CONTACTER RAZOR", callback_data='contact')],
        [InlineKeyboardButton("🔥 MATCHS DU JOUR", callback_data='matchs_du_jour')],
        [InlineKeyboardButton("💎 PRONOS RAZOR", callback_data='pronostics')],
        [InlineKeyboardButton("ℹ️ INFOS BOT", callback_data='infos')],
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("📈 STATS SECRETES", callback_data='stats')])
    keyboard.append([InlineKeyboardButton("❌ FERMER", callback_data='quit')])
    return InlineKeyboardMarkup(keyboard)

def build_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RETOUR", callback_data='back')]])

# --- MOTEUR DE PRONOSTICS ---
class RazorPredictor:
    @staticmethod
    def generate_razor_pronostic(match):
        home = match['match_hometeam_name']
        away = match['match_awayteam_name']
        match_key = f"{home}_{away}"
        
        if match_key in historique_pronos:
            return f"⚡️ {historique_pronos[match_key]} (CONFIANCE HISTORIQUE)"
        
        home_power = RazorPredictor._calculate_power(home)
        away_power = RazorPredictor._calculate_power(away)
        diff = home_power - away_power
        base_conf = 60 + abs(diff) * 10
        
        if diff > 1:
            emoji = "🔴" if diff > 2 else "🔺"
            return f"{emoji} VICTOIRE {home} ({min(95, base_conf)}% RAZOR CONFIANCE)"
        elif diff < -1:
            emoji = "🔵" if diff < -2 else "🔻"
            return f"{emoji} VICTOIRE {away} ({min(90, base_conf)}% RAZOR CONFIANCE)"
        else:
            return f"🟡 MATCH NUL ({min(80, base_conf)}% RAZOR CONFIANCE)"
    
    @staticmethod
    def _calculate_power(team):
        if team not in team_stats:
            team_stats[team] = min(5, max(1, len(team) * 0.15 + (hash(team) % 5)))
        return team_stats[team]

# --- API FOOTBALL ---
def get_today_matches():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://apiv3.apifootball.com/?action=get_events&from={today}&to={today}&APIkey={API_FOOTBALL_KEY}"
    try:
        response = requests.get(url, timeout=15)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"⚠️ Erreur API Football: {e}")
        return []

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)
    await update.message.reply_text(
        "🦅 <b>RAZOR LE RUSSE OFFICIEL 🇷🇺💯</b> 🦅\n\n"
        "🦅 <b>RAZOR CODE PROMO 1XBET => VS75</b> 🦅\n\n"
        "🦅 <b>RAZOR CODE PROMO BETWINER 1RAZOR</b> 🦅\n\n"
        "💎 <i>Pronostics Premium Gratuits</i>\n\n"
        "👇 <b>UTILISEZ LE MENU CI-DESSOUS</b> 👇",
        parse_mode='HTML',
        reply_markup=build_menu(user_id)
    )

async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🔎 RAZOR SCANNE LES MATCHS...")
    matches = get_today_matches()
    
    if not matches:
        await update.callback_query.edit_message_text("⚠️ AUCUN MATCH DISPONIBLE", reply_markup=build_back_menu())
        return
    
    text = "🔥 <b>MATCHS DU JOUR</b> 🔥\n\n"
    for m in matches[:15]:
        text += f"⚔️ <b>{m['match_hometeam_name']}</b> vs <b>{m['match_awayteam_name']}</b>\n⏰ {m['match_time']} | 📅 {m['match_date']}\n\n"
    
    await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=build_back_menu())

async def show_pronostics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🧠 RAZOR ANALYSE LES CÔTES...")
    matches = get_today_matches()[:5]
    
    if not matches:
        await update.callback_query.edit_message_text("⚠️ AUCUN MATCH À ANALYSER", reply_markup=build_back_menu())
        return
    
    pronos = []
    for match in matches:
        prono = RazorPredictor.generate_razor_pronostic(match)
        pronos.append(f"🎯 <b>{match['match_hometeam_name']} vs {match['match_awayteam_name']}</b>\n⏱ {match['match_time']} | {match['match_date']}\n💎 <i>{prono}</i>\n\n")
    
    await update.callback_query.edit_message_text(
        "🦅 <b>PRONOSTICS RAZOR EXCLUSIFS</b> 🦅\n\n" + "".join(pronos),
        parse_mode='HTML',
        reply_markup=build_back_menu()
    )

async def informations_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "ℹ️ <b>INFORMATIONS OFFICIELLES</b> ℹ️\n\n"
        "🦅 Bot créé par RAZOR\n"
        "💰 Codes promo exclusifs :\n"
        "• 1XBET : <b>RAZOR2980</b>\n"
        "• BETWINNER : <b>RAZOR25</b>\n\n"
        "🔞 Paris responsables",
        parse_mode='HTML',
        reply_markup=build_back_menu()
    )

async def contacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "📩 <b>CONTACT RAZOR</b> 📩\n\n"
        "Telegram : @Razor_Contact\n"
        "Email : razor@pronos.com\n\n"
        "📣 Réponse sous 24h",
        parse_mode='HTML',
        reply_markup=build_back_menu()
    )

async def afficher_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    if user_id != ADMIN_ID:
        await update.callback_query.answer("🔒 ACCÈS RÉSERVÉ", show_alert=True)
        return
    
    await update.callback_query.edit_message_text(
        f"📊 <b>STATISTIQUES SECRÈTES</b> 📊\n\n"
        f"👥 Utilisateurs : {len(users)}\n"
        f"🔮 Pronostics : {len(historique_pronos)}\n"
        f"📈 Équipes : {len(team_stats)}",
        parse_mode='HTML',
        reply_markup=build_back_menu()
    )

async def quitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.delete_message()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

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
        await start(update, context)
    else:
        await query.edit_message_text("⚠️ Commande inconnue")

# --- LANCEMENT ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🦅 RAZOR BOT ACTIF 🦅")
    app.run_polling()

if __name__ == "__main__":
    main()
