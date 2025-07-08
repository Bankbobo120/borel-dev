import os
import datetime
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from aiohttp import web

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "d537cf906846aee79d1608e6644e5283bfebfd9da3d6f8e9763c6be14832afb0")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7745293166"))
PORT = int(os.getenv("PORT", 10000))  # Port spécifique pour Render

# --- BASE DE DONNÉES ---
users = set()
historique_pronos = {}
team_stats = {}

# --- DESIGN DES INTERFACES ---
def build_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("🌟 CONTACTER RAZOR", callback_data='contact')],
        [InlineKeyboardButton("🔥 MATCHS DU JOUR", callback_data='matchs_du_jour')],
        [InlineKeyboardButton("💎 PRONOS VIP", callback_data='pronostics')],
        [InlineKeyboardButton("ℹ️ INFOS BOT", callback_data='infos')],
        [InlineKeyboardButton("ℹ️ STATS", callback_data='stats')],
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("🔐 STATS SECRETES", callback_data='stats')])
    keyboard.append([InlineKeyboardButton("🚪 QUITTER", callback_data='quit')])
    return InlineKeyboardMarkup(keyboard)

def build_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RETOUR", callback_data='back')]])

# --- MOTEUR INTELLIGENT RAZOR ---
class RazorEngine:
    @staticmethod
    def generate_prediction(match):
        home = match['match_hometeam_name']
        away = match['match_awayteam_name']
        match_key = f"{home}_{away}"
        
        if match_key in historique_pronos:
            return f"⚡️ {historique_pronos[match_key]} (BASÉ SUR L'HISTORIQUE)"
        
        home_power = RazorEngine._team_strength(home)
        away_power = RazorEngine._team_strength(away)
        diff = home_power - away_power
        
        if diff > 1.5:
            return f"🔴 VICTOIRE {home} (CONFIANCE: {min(95, 70 + diff*10)}%)"
        elif diff < -1.5:
            return f"🔵 VICTOIRE {away} (CONFIANCE: {min(90, 70 + abs(diff)*10)}%)"
        else:
            return f"🟡 MATCH NUL (CONFIANCE: {min(85, 65 + abs(diff)*5)}%)"
    
    @staticmethod
    def _team_strength(team):
        if team not in team_stats:
            # Algorithme propriétaire Razor
            team_stats[team] = min(10, max(1, 
                len(team) * 0.2 + 
                (hash(team) % 7) * 0.3 +
                datetime.datetime.now().weekday()
            ))
        return team_stats[team]

# --- CONNEXION API FOOTBALL ---
def get_daily_matches():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://apiv3.apifootball.com/?action=get_events&from={today}&to={today}&APIkey={API_FOOTBALL_KEY}"
    try:
        response = requests.get(url, timeout=20)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"⚠️ ERREUR API: {str(e)}")
        return []

# --- SERVEUR WEB POUR RENDER ---
async def health_check(request):
    return web.Response(
        text="🟢 RAZOR BOT OPERATIONNEL - HEALTH CHECK OK",
        status=200
    )

async def run_webserver():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Serveur web actif sur le port {PORT}")

# --- GESTION DES COMMANDES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)
    
    promo_design = """
🎰 <b>CODES PROMO EXCLUSIFS</b> 🎰

┏━━━━━━━━━━━━━━━━━━┓
┃  <b>1XBET</b> ┃ <code>VS75</code> ┃
┃   <i>Bonus 130€</i>   ┃
┗━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━┓
┃ <b>BETWINNER</b> ┃ <code>1RAZOR</code> ┃
┃  <i>Bonus 100€</i>   ┃
┗━━━━━━━━━━━━━━━━━━┛
"""
    
    await update.message.reply_text(
        f"""
🦅 <b>RAZOR PRONOSTICS VIP</b> 🦅
🇷🇺 <i>Le spécialiste des paris gagnants</i>

{promo_design}

👇 <b>MENU PRINCIPAL</b> 👇
        """,
        parse_mode='HTML',
        reply_markup=build_menu(user_id)
    )

async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🔍 RAZOR ANALYSE LES MATCHS...")
    matches = get_daily_matches()
    
    if not matches:
        await update.callback_query.edit_message_text(
            "⚠️ AUCUN MATCH DISPONIBLE AUJOURD'HUI",
            reply_markup=build_back_menu()
        )
        return
    
    matches_list = "\n".join(
        f"⚽ <b>{m['match_hometeam_name']}</b> vs <b>{m['match_awayteam_name']}</b>\n"
        f"⏰ {m['match_time']} | 📅 {m['match_date']}\n"
        for m in matches[:10]
    )
    
    await update.callback_query.edit_message_text(
        f"🔥 <b>MATCHS DU JOUR</b> 🔥\n\n{matches_list}",
        parse_mode='HTML',
        reply_markup=build_back_menu()
    )

async def show_predictions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🧠 RAZOR CALCULE LES PRONOSTICS...")
    matches = get_daily_matches()[:5]
    
    if not matches:
        await update.callback_query.edit_message_text(
            "⚠️ AUCUN MATCH À ANALYSER",
            reply_markup=build_back_menu()
        )
        return
    
    predictions = [
        f"🎯 <b>{m['match_hometeam_name']} vs {m['match_awayteam_name']}</b>\n"
        f"⏱ {m['match_time']} | 📅 {m['match_date']}\n"
        f"💎 <i>{RazorEngine.generate_prediction(m)}</i>\n\n"
        for m in matches
    ]
    
    await update.callback_query.edit_message_text(
        "🦅 <b>PRONOSTICS VIP RAZOR</b> 🦅\n\n" + "".join(predictions),
        parse_mode='HTML',
        reply_markup=build_back_menu()
    )

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    if user_id != ADMIN_ID:
        await update.callback_query.answer(
            "🔐 ACCÈS RÉSERVÉ À L'ADMINISTRATEUR",
            show_alert=True
        )
        return
    
    stats_msg = f"""
📊 <b>STATISTIQUES PRIVÉES</b> 📊

👥 Utilisateurs: <b>{len(users)}</b>
🔮 Pronostics: <b>{len(historique_pronos)}</b>
📈 Équipes analysées: <b>{len(team_stats)}</b>

🔄 Dernière mise à jour: {datetime.datetime.now().strftime('%H:%M:%S')}
"""
    
    await update.callback_query.edit_message_text(
        stats_msg,
        parse_mode='HTML',
        reply_markup=build_back_menu()
    )

# ... (autres handlers comme précédemment)

async def main():
    # Démarrer le serveur web
    await run_webserver()
    
    # Configurer le bot Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🦅 RAZOR BOT OPÉRATIONNEL 🦅")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
