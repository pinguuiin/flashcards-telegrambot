from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from expressions import *



def main_menu(language):

    markup = ReplyKeyboardMarkup(row_width= 2, resize_keyboard= True)

    if language == 'fa':
        learning_button = KeyboardButton("تمرین کلمات")
        menu_button = KeyboardButton("منو")
    if language == 'en':
        learning_button = KeyboardButton("Practice Words")
        menu_button = KeyboardButton("Menu")
    if language == 'ru':
        learning_button = KeyboardButton("Тренировать слова")
        menu_button = KeyboardButton("Меню")

    markup.add(menu_button, learning_button)

    return markup

def menu_buttons(language):

    markup = ReplyKeyboardMarkup(row_width= 2, resize_keyboard= True)

    if language == 'fa':
        setting_button = KeyboardButton("مرور کلمات گذشته")
        record_button = KeyboardButton("گزارش عملکرد")
        back_button = KeyboardButton("بازگشت")
    elif language == 'en':
        setting_button = KeyboardButton("Review Past Words")
        record_button = KeyboardButton("Performance Report")
        back_button = KeyboardButton("Back")
    elif language == 'ru':
        setting_button = KeyboardButton("Просмотр пройденных слов")
        record_button = KeyboardButton("Отчет о результатах")
        back_button = KeyboardButton("Назад")
    markup.add(setting_button, record_button, back_button)

    return markup

def meaning_key(language):
    markup = InlineKeyboardMarkup()
    got_it_button = InlineKeyboardButton(communication_expression(language, " ", 0)[6], callback_data="gotit")
    markup.add(got_it_button)
    return markup


def word_keys():
    markup = InlineKeyboardMarkup()
    remember_button = InlineKeyboardButton("✅", callback_data="remember")
    forget_button = InlineKeyboardButton("❌", callback_data="forget")
    markup.add(remember_button, forget_button)
    return markup