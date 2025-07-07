from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import requests

SPORTMONKS_TOKEN = "7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc"  # Mets ta clé ici

# --- Fonctions pour chaque option du menu ---

def build_menu():
    keyboard = [
        [InlineKeyboardButton(" 📩 Contacter RAZOR", callback_data='contact')],
        [InlineKeyboardButton("🔥 Pronostic du jour", callback_data='pronostic_du_jour')],
        [InlineKeyboardButton("ℹ️ Informations sur le bot", callback_data='infos')],
        [InlineKeyboardButton("❌ Quitter", callback_data='quit')],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_back_menu():
    keyboard = [
        [InlineKeyboardButton("⬅️ Retour au menu principal", callback_data='back')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def obtenir_pronostic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "Fonction à développer : Obtenir un pronostic personnalisé.",
        reply_markup=build_back_menu()
    )

async def pronostic_du_jour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url1 = f"https://api.sportmonks.com/v3/football/fixtures?filter[upcoming]=true&sort=starting_at&api_token={SPORTMONKS_TOKEN}&per_page=1"
    res1 = requests.get(url1)
    if res1.status_code != 200 or not res1.json().get('data'):
        await update.callback_query.edit_message_text("❌ Impossible de récupérer les fixtures à venir.", reply_markup=build_back_menu())
        return

    fixture = res1.json()['data'][0]
    fixture_id = fixture['id']
    match_name = fixture.get('name', "Match à venir")

    await update.callback_query.edit_message_text(f"🔄 Chargement du pronostic IA pour :\n⚽ {match_name}")

    url2 = f"https://api.sportmonks.com/v3/football/predictions/probabilities/fixtures/{fixture_id}?api_token={SPORTMONKS_TOKEN}"
    res2 = requests.get(url2)

    if res2.status_code == 200 and res2.json().get('data'):
        p = res2.json()['data']['predictions']
        pronostic = (
            f"🎯 *Pronostic IA — {match_name} :*\n\n"
            f"🏠 Domicile : *{p['winner_home']*100:.1f}%*\n"
            f"🤝 Nul : *{p['winner_draw']*100:.1f}%*\n"
            f"🚨 Extérieur : *{p['winner_away']*100:.1f}%*\n\n"
            "_Powered by Sportmonks_"
        )
        await update.callback_query.edit_message_text(pronostic, parse_mode="Markdown", reply_markup=build_back_menu())
    else:
        await update.callback_query.edit_message_text("❌ Pronostic IA non disponible.", reply_markup=build_back_menu())
async def informations_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = (
        "🔥 Bienvenue sur le bot officiel de RAZOR ! 🔥\n\n"
        "Ce bot de pronostics sportifs a été conçu en Russie 🇷🇺 par RAZOR, "
        "un très grand pronostiqueur reconnu pour ses analyses précises et ses conseils gagnants 🎯⚽️🏀.\n\n"
        "✨ Profitez des meilleurs codes promo exclusifs :\n"
        "- 1xBet : 2980 🎰\n"
        "- BetWinner : 2980 ou Razor25 🎲\n\n"
        "N’hésitez pas à utiliser ces codes pour maximiser vos gains et booster votre expérience de jeu !\n\n"
        "⚠️ Attention, pariez toujours de manière responsable. Bonne chance et que la chance soit avec vous ! 🍀"
    )
    await update.callback_query.edit_message_text(texte, parse_mode='Markdown', reply_markup=build_back_menu())

async def quitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "Merci d'avoir utilisé le bot. À bientôt !"
    )

# --- Handler du /start qui affiche le menu ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texte = (
        "🔥 RAZOR LE RUSSE. 🇷🇺🇷🇺💯💯 PRONOSTICS GRATUIT 💯\n\n"
        "PRONOSTIC 1XBET, BETWINER\n\n"
        "On valide les gars 💪🤞🏾☘💰💰💰💰\n"
        "✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅\n\n"
        "AVANTAGES DU CODE PROMO 2980 meilleur d’Afrique 👇\n\n"
        "👉 Paris gratuits\n"
        "👉 Remises sur tes pertes\n"
        "👉 Couverture sécurité\n"
        "👉 Bonus retirables\n"
        "👉 Retraits élevés {⁵⁰⁰ ⁰⁰⁰ ⁰⁰⁰f}\n"
        "👉 Bonus booster côtes, etc.\n\n"
        "ACTUALISE TON COMPTE ici 👈"
    )
    await update.message.reply_text(texte, reply_markup=build_menu())
# --- Handler pour gérer les clics sur les boutons ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'pronostic_du_jour':
        await pronostic_du_jour(update, context)
    elif data == 'infos':
        await informations_bot(update, context)
    elif data == 'quit':
        await quitter(update, context)
    elif data == 'back':
        await query.edit_message_text(
            "Bienvenue sur le bot de pronostics sportifs ! Que souhaitez-vous faire ?",
            reply_markup=build_menu()
        )
    elif data == 'contact':
        await update.callback_query.edit_message_text(
            "📩 Pour contacter RAZOR, envoyez un message ici :\n\n"
            "📧 Email : razor@example.com\n"
            "📱 Telegram : @RazorContact\n\n"
            "N'hésitez pas à poser vos questions ou demander de l'aide !",
            reply_markup=build_back_menu()
        )
    else:
        await query.edit_message_text("Option inconnue, veuillez réessayer.")
# --- Fonction principale ---

def main():
    app = ApplicationBuilder().token("7295542974:AAGIjBZjzktAHBIz0QPlvE-aD3QYUca7yEc").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
