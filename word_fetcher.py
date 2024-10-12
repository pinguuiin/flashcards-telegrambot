from db_interaction import get_new_word, user_rem_word_list

def fetch_word(user_id):
    remembered_words = user_rem_word_list(user_id)

    word = get_new_word()
    if word in remembered_words:
        word = get_new_word()
    return word

if __name__ == "__main__":
    user_id = 123456789
    print(fetch_word(user_id= user_id))

