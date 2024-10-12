import telebot

def bot_auth():
    BOT_TOKEN = 'YOUR_BOT_TOKEN'
    bot = telebot.TeleBot(BOT_TOKEN)
    return bot