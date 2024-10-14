import pandas as pd
import random
import gspread
import unicodedata
from typing import Final
from datetime import datetime
from deep_translator import GoogleTranslator
from google.oauth2.service_account import Credentials
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '' # Your bot token
BOT_USERNAME: Final = '' # Your bot username
spreadsheet_url = '' # Your google spreadsheet url
credentials_file = 'flashcard-thunderbot-8b4f42dca2ae.json' # Your credentials file

# Set up the scope and authorize
scopes = ["https://www.googleapis.com/auth/spreadsheets", 
          "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
client = gspread.authorize(creds)

# Open the spreadsheet by URL or title
sheet = client.open_by_url(spreadsheet_url).sheet1

# Get a random word from vocabulary sheet. Probability based on familarity level (0-5). 
# With new word added in.
async def get_a_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    try:
        vocabulary = pd.DataFrame(sheet.get_all_records())
        user_records = get_user_spreadsheet(context.user_data.get('file_path'))

        index_list = []
        repeat_count = 0
        word_count = len(vocabulary)
        user_count = len(user_records)
        repeat_table = [1, 2, 4, 7, 15, 30, 90, 180]

        # Add probability to each word (new word: 30%, review word: 70%)
        p_new = 0.3 / (word_count - user_count) * 10000  # Pay attention to zero divider (later)
        df = pd.merge(vocabulary, user_records, how='left', on='Word')
        df['Familarity'] = df['Familarity'].fillna(0)
        df['P'] = p_new
        df.loc[df['Familarity'] == 5, 'P'] = 0  # Pass remembered word

        today = datetime.now().date()
        for index, record in df.iterrows():
            # In prgress words that need to be but not yet reviewed today
            if pd.notna(record['Date']) and record['Familarity'] < 5:
                # Convert pandas.Timestamp to datetime.date
                record_date = record['Date'].date() if isinstance(record['Date'], pd.Timestamp) else record['Date']
                if (today - record_date).days in repeat_table \
                and record['LatestAccessDate'] != today:
                    repeat_count += 1
                    index_list.append(index)
                else:
                    df.loc[index, 'P'] = 0  # Pass word no need for review today
        if repeat_count > 0:
            p_repeat = 0.7 / repeat_count * 10000
            df.loc[index_list, 'P'] = p_repeat

        word = random.choices(df['Word'], weights=df['P'], k=1)[0]

        return word
    
    except Exception as e:
        return f"Error reading sheet 0: {e}"

# To be compatible with python output
def escape_markdown(text) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return ''.join([f'\\{char}' if char in escape_chars else char for char in text])

def clean_text(text) -> str:
    return unicodedata.normalize('NFKC', text).strip().lower()

# Get the word meaning from vocabulary sheet
def get_word_meaning(word) -> str:
    try:
        records = sheet.get_all_records()
        for record in records:
            if clean_text(record['Word']) == clean_text(word):
                name = record['Word'].strip()
                meaningEng = record['Eng Meaning'].strip()
                meaningFa = record['Fa Meaning'].strip()
                sampleSentence = record['Sentence'].strip()
                sampleMeaningEng = GoogleTranslator(source='fi', \
                                                    target='en').translate(sampleSentence)
                sampleMeaningFa = record['Fa Sentence Meaning'].strip()
                bookName = record['Book'].strip()
                chapterNumber = str(record['Chapter']).strip()
                
                message = (
                    f"{escape_markdown(name)}\n\n"
                    f"\[En\] *{escape_markdown(meaningEng)}*\n"
                    f"\[Fa\] *{escape_markdown(meaningFa)}*\n\n"
                    f"• _{escape_markdown(sampleSentence)}_\n"
                    f"_\[En\] {escape_markdown(sampleMeaningEng)}_\n"
                    f"_\[Fa\] {escape_markdown(sampleMeaningFa)}_\n\n"
                    f"From {escape_markdown(bookName)} Chapter {escape_markdown(chapterNumber)}"
                )
                return message
        return "Sorry, word not found in Suomen Mestari 1."
    except Exception as e:
        return f"Error reading sheet 1: {e}"

# Read the user's spreadsheet into a dataframe. If not exist, create a new dataframe
def get_user_spreadsheet(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Word','Familarity','Date', 'LatestAccessDate'])

# Save the new word into user's spreadsheet
def save_word(file_path, word, know_bool):
    try:
        df = get_user_spreadsheet(file_path)
        # new word
        if word not in df['Word'].values:
            df = pd.concat([df, pd.DataFrame([{'Word': word, 'Familarity': know_bool*5, \
                    'Date': datetime.now().date(), 'LatestAccessDate': datetime.now().date()}])], \
                        ignore_index=True)
        # old word
        else:
            if know_bool == 0:
                df.loc[df['Word'] == word, 'Familarity'] = 0
                df.loc[df['Word'] == word, 'Date'] = datetime.now().date()  # Back to first day
            else:
                familarity = df.loc[df['Word'] == word, 'Familarity'].values[0]
                df.loc[df['Word'] == word, 'Familarity'] = familarity + 1
            df.loc[df['Word'] == word, 'LatestAccessDate'] = datetime.now().date()
        df.to_excel(file_path, index=False)
    except Exception as e:
        print(f"Error saving word {word}: {e}")

# Generate a random word from the vocabulary spreadsheet and make a flashcard
async def flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.message.from_user.first_name
    user_username = update.message.from_user.username
    user_id = update.message.from_user.id
    excel_file_path = f"User_{user_id}_flashcards.xlsx"
    context.user_data['file_path']= excel_file_path  # Save user file path

    new_word = await get_a_word(update, context)  # Get word
    context.user_data['word'] = new_word  # Save word to user data
    keyboard = [['Remember', 'Forget', 'Quit']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    print(f"User {user_first_name} (@{user_username}) is learning word *{new_word}*.")
    await update.message.reply_text(f"{new_word}", reply_markup=reply_markup)

# If the user forgets, show the meaning and save the word to the user's spreadsheet
async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_word = context.user_data.get('word')  # Extract word
    know_bool = 0
    save_word(context.user_data.get('file_path'), new_word, know_bool)
    meaning = get_word_meaning(new_word)
    keyboard = [['OK! Next','Quit']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(f"{meaning}", parse_mode='MarkdownV2', reply_markup=reply_markup)

# Go to next word after checking the meaning
async def nextword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("qoq!")
    await flashcard(update, context)

# If the user remembers, save the word to the user's spreadsheet
async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_word = context.user_data.get('word')  # Extract word
    know_bool = 1
    save_word(context.user_data.get('file_path'), new_word, know_bool)
    await update.message.reply_text("qoq!")
    await flashcard(update, context)

# Quit flashcard process
async def quit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("You have quit the process. If you want to start again, type /start",
            reply_markup=ReplyKeyboardRemove())

# Handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':

    app = Application.builder().token(TOKEN).build()
    # Commands
    app.add_handler(CommandHandler("start", flashcard))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Forget$'), forget))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^OK! Next$'), nextword))    
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Remember$'), remember))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Quit$'), quit))
    # Errors
    app.add_error_handler(error)

    print('Polling...')
    # Start polling updates
    app.run_polling(poll_interval=3)