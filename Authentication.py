import telebot

bot = telebot.TeleBot("7647296938:AAHu57wEC48MYUiLce0uOLCSbTqxjuOez1I")

file = open(r"C:\Users\hesam\OneDrive\Desktop\Telegram Bot\userNames.txt", 'r')
user_names = [int(line.strip()) for line in file.readlines()]
print(user_names)
file.close()

@bot.message_handler(commands=['start'])
def authentication(message):
    global user_name
    user_name = message.from_user.id

    if user_name in user_names:
        return True
    else:
        bot.send_message(message.chat.id, "You must contact @HesamWahib")

print("read auth")

"""markup = telebot.types.InlineKeyboardMarkup()
first_button = telebot.types.InlineKeyboardButton(text="dumb_button", url = "https://google.com")
second_button = telebot.types.InlineKeyboardButton(text="asshole_button", callback_data="Hi")
markup.add(first_button, second_button)

key_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
key_markup.add("Register", "Two", "Three")

@bot.callback_query_handler(func=lambda call: call.data == "Hi")
def hi_button(call):
    bot.send_message(call.message.chat.id, "Aleike Hi")

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Hi", reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "how can I help you?", reply_markup= key_markup)

@bot.message_handler(func= lambda message: message.text == 'One')
def keyboard(message):
    if message.text == 'One':
        bot.send_message(message.chat.id, "you tapped on One dude")
    else:
        bot.send_message(message.chat.id, "nothing")
    print (message.text)

@bot.message_handler(func= lambda message: message.text == 'salam')
def info(message):
    bot.send_message(message.chat.id, "enter your name")
    bot.register_next_step_handler(message, name)

def name(message):
    global user_name
    user_name = message.text
    bot.send_message(message.chat.id, f"you are {user_name}")"""
