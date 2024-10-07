import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
import random
from Sheet_auth import authenticate_sheets, result
from datetime import datetime
import re


# To be compatible with python output
def escape_markdown(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return ''.join([f'\\{char}' if char in escape_chars else char for char in text])

day_word_list = []

def send_message():
    print('Connected!')
    values = result.get('values', [])
    counter = 1
    randList = []
    checkList = []
    checkCounter = 0

    # Getting the "Uncheck" words (which has not sent to the channel yet) and put them in a list
    for value in values:
        if value[8] == 'uncheck':
            checkList.append(checkCounter)
        checkCounter += 1
    print(checkList)


    while True:
        if counter > 5:
            break

        randNum = random.choice(checkList)
        while randNum in randList: # Something is remaind UNSOLVED: What if checkList does not have enough number to be chosen for random number
            randNum = random.choice(checkList)

        randList.append(randNum)
        print(f'random number is: {randNum}')
        each_column = values[randNum]
        word = each_column[0].strip()
        meaningEng = each_column[1].strip()
        meaningFa = each_column[2].strip()
        pronunciation = each_column[3].strip()
        sampleSentence = each_column[4].strip()
        meaningSample = each_column[5].strip()
        bookName = each_column[6].strip()
        chapterNumber = each_column[7].strip()

        day_word_list.append(word.lower())

        message = (
            f"کلمه: `{escape_markdown(word)}`\n\n"
            f"ترجمه انگلیسی: ||{escape_markdown(meaningEng)}||\n"
            f"ترجمه فارسی: ||{escape_markdown(meaningFa)}||\n"
            #f"تلفظ: {escape_markdown(pronunciation)}\n\n"
            f"نمونه جمله: {escape_markdown(sampleSentence)}\n"
            f"معنی جمله: ||{escape_markdown(meaningSample)}||\n\n"
            f"کتاب {escape_markdown(bookName)} درس {escape_markdown(chapterNumber)}"
        )

        # Sending the word in Telegram Channel
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "MarkdownV2"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")

        url_audio = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
        word = re.sub(r'[<>:"/\\|?*]', '_', word)
        audio_local_address = f"C:\\Users\\hesam\\OneDrive\\Desktop\\Python2\\Random Project\\words_audio\\{word}.ogg"
        if audio_local_address:
            with open(audio_local_address, 'rb') as audio:
                files = {
                    'audio': audio
                }
                params = {
                    "chat_id": CHAT_ID,
                    #"text": r"C:\Users\hesam\OneDrive\Desktop\Python2\Random Project\Naurattaa.mp3",
                    "caption": f"تلفظ کلمه {word}"
                }
                try:
                    response = requests.get(url_audio, params=params, files=files)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"Error sending message: {e}")
            
        # Write "Check" for posted words to prevent repeating
        write_to_sheet(sheets, f'I{randNum}:J{randNum}', [['check', f'{datetime.now().date()}']])

        counter += 1

    print(randList)
    response = co.chat(
    model="command-r-plus",
    messages=[
        {
            "role": "user",
            "content": f"this is 5 finnish words: {day_word_list}. write a simple short story in finnish by them. dont write any furthur thing. just the story without title"
        }
    ]
    )
    story = response.message.content[0].text
    params={
        "chat_id": CHAT_ID,
        "text": story,
        "parse_mode": "HTML"
    }
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        send_story = requests.post(url, params=params)
        send_story.raise_for_status()
    except:
        pass
if __name__ == "__main__":
    send_message()
    print('All is Done')

