from word_fetcher import fetch_word
from Authentication import authentication
from Bot_auth import *
from datetime import datetime, timedelta
from db_interaction import *
from buttons import *
from expressions import *

bot = bot_auth()
bot_lang = 'en' # for now you can by changing the lanuage here change the bot language. ('fa': Farsi, 'en': English, 'ru': Russian)
time_now = datetime.now()
def date_time_now():
    date_time = time_now.strftime("%Y-%m-%d %H:%M:%S")
    return date_time
word_review_limit = 20

""" REGISTRATION """

@bot.message_handler(commands=['start'])
def welcoming(message):
    is_authenticated = authentication(message)
    print(is_authenticated)

    if is_authenticated:
        first_name = [name[0] for name in user_name(message.from_user.id)][0]
        bot.send_message(message.chat.id, communication_expression(bot_lang, first_name, 0)[0], reply_markup=main_menu(bot_lang))

@bot.message_handler(commands=['register'])
def register(message):
    registered_users = [user[0] for user in users()] #what if the user_id registered string wise?

    global user_id
    user_id = message.from_user.id

    if user_id in registered_users:
        first_name = [name[0] for name in user_name(message.from_user.id)][0]
        bot.send_message(message.chat.id, communication_expression(bot_lang, first_name, 0)[1], reply_markup=main_menu(bot_lang))
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        letsgo_button = telebot.types.InlineKeyboardButton(communication_expression(bot_lang, " ", 0)[10], callback_data="letsgo")
        markup.add(letsgo_button)
        bot.send_message(message.chat.id, communication_expression(bot_lang, " ", 0)[2], reply_markup=markup)

@bot.callback_query_handler(func= lambda call: call.data == 'letsgo')
def registration_start(call):
    global user_data_registeration
    user_data_registeration = [] #how to handle sudden click on this buttons (user_id is not defined)
    user_data_registeration.append(user_id)
    bot.send_message(call.message.chat.id, communication_expression(bot_lang, " ", 0)[3])
    bot.register_next_step_handler(call.message, set_name)

def set_name(message):
    global first_name
    first_name = message.text
    user_data_registeration.append(message.text)
    markup = telebot.types.InlineKeyboardMarkup()
    english_button = telebot.types.InlineKeyboardButton("English", callback_data="en")
    farsi_button = telebot.types.InlineKeyboardButton("فارسی", callback_data="fa")
    russian_button = telebot.types.InlineKeyboardButton("русский", callback_data="ru")
    markup.add(english_button, farsi_button, russian_button)
    bot.send_message(message.chat.id, communication_expression(bot_lang, " ", 0)[4], reply_markup=markup)

@bot.callback_query_handler(func= lambda call: call.data in['en', 'fa', 'ru'])
def language(call):
    language = call.data
    registeration_date_time = date_time_now()
    valid_to_freemium = (time_now + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")

    register_new_user(user_id, first_name, language, registeration_date_time, validation= 'active', valid_to= valid_to_freemium)
    bot.send_message(call.message.chat.id, communication_expression(bot_lang, first_name, 0)[5], reply_markup=main_menu(bot_lang))
    print(f"user by id {user_id} is registered!")

""" DISPLAY WORD """

@bot.message_handler(func= lambda message: message.text in ['منو', 'Menu', 'Меню'])
def menu(message):
    bot.send_message(message.chat.id, communication_expression(bot_lang, " ", 0)[7], reply_markup=menu_buttons(bot_lang))

@bot.message_handler(func= lambda message: message.text in ['گزارش عملکرد', 'Performance Report', 'Отчет о результатах'])
def record_report(message):
    user_id = message.from_user.id
    date_time = date_time_now()
    bot.send_message(message.chat.id, user_record(user_id, date_time, bot_lang), reply_markup=menu_buttons(bot_lang))

@bot.message_handler(func= lambda message: message.text in ['مرور کلمات گذشته', 'Review Past Words', 'Просмотр пройденных слов'])
def words_review(message):
    date_time = date_time_now()
    user_id = message.from_user.id
    bot.send_message(message.chat.id, word_review(user_id, date_time, bot_lang), reply_markup=menu_buttons(bot_lang))

@bot.message_handler(func= lambda message: message.text in ['بازگشت', 'Back', 'Назад'])
def back_to_frontpage(message):
    bot.send_message(message.chat.id, communication_expression(bot_lang, " ", 0)[8], reply_markup=main_menu(bot_lang))

@bot.message_handler(func= lambda message: message.text in ['تمرین کلمات', 'Practice Words', 'Тренировать слова'])
@bot.message_handler(commands=['learning', 'reset_counter']) # reset_counter for test mode
def show_word(message):
    # Counter to limit

    global word
    is_authenticated = authentication(message)
    user_id = message.from_user.id
    word_counter = user_word_counter(user_id, date_time_now()) if message.text != '/reset_counter' else 0 # if for test mode

    word = fetch_word(user_id)

    if is_authenticated == True and word_counter < word_review_limit:
         # here I had to authorize the bot itself because when it sends a callback bot regocnizes it as thebot not the user.
        bot.send_message(message.chat.id, word[0], reply_markup=word_keys())
    else:
        bot.send_message(message.chat.id, communication_expression(bot_lang, " ", word_counter)[9], reply_markup= main_menu(bot_lang))

@bot.callback_query_handler(func= lambda call: True)
def callback_handler(call):
    response = call.data
    if response in ['remember', 'forget', 'gotit']:
        user_id = call.message.chat.id
        shown_word= call.message.text
        print (f"shown word: {shown_word}")
        is_remembered = True if response == 'remember' else False

        review_time = date_time_now()

        word_counter = user_word_counter(user_id, review_time)
        if response == 'remember' or response == 'forget':

            user_tracker(user_id, shown_word, is_remembered, review_time)
            #Counter += 1

        if (response == "remember" or response == "gotit") and word_counter < word_review_limit:
            bot.send_message(call.message.chat.id, get_motivation(bot_lang))
            show_word(call.message)
            print(f"{user_id}: number of {word_counter}")

        elif word_counter >= word_review_limit:
            bot.send_message(call.message.chat.id,  communication_expression(bot_lang, " ", word_counter)[9], reply_markup= main_menu(bot_lang))
        else:
            try:
                # different meanings based on database architecture
                if bot_lang == 'fa':
                    meaning = word[3]
                elif bot_lang == 'en':
                    meaning = word[2]
                elif bot_lang == 'ru':
                    meaning = word[4]    #if user starts with FORGET button it cannot recognize the word
            except:
                meaning = "Not Exist" #with cohere ????
            bot.send_message(call.message.chat.id, meaning, reply_markup=meaning_key(bot_lang))

bot.infinity_polling()