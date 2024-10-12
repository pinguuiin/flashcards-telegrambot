import pymysql
from expressions import generate_user_record_text, generate_word_review_text

cnx = pymysql.connect(
    host="",
    user="",
    password="",
    database="",
)
cursor = cnx.cursor()

""" Tables = {
                user: user_id bigint(20) PRI, name VARCHAR(100), language VARCHAR(10), created_at datetime, validation VARCHAR(20), calid_to datetime/
                record: id int(11) PRI AUTO_INCREMENT, user_id bigint(20), word VARCHAR(500), is_remembered BOOL, created_at datetime/
                word: word VARCHAR(100) PRI, word_type VARCHAR(20), en_meaning VARCHAR(100), fa_meaning VARCHAR(100), ru_meaning VARCHAR(100), source int(11)/
                source: code int(11) PRI, name VARCHAR(100)/
                } """

""" USER'S FUNCTIONS """

def register_new_user(user_id, name= None, language= None, created_at= None, validation= None, valid_to= None):
    query = """ INSERT INTO user (user_id, name, language, created_at, validation, valid_to)
            VALUES (%s, %s, %s, %s, %s, %s) """
    data = (user_id, name[:100], language, created_at, validation, valid_to)
    try:
        cursor.execute(query, data)
    except Exception as e:
        print("User has already been registered. DUPLICATE")
    cnx.commit()

def users():
    query = """ SELECT user_id from user"""
    cursor.execute(query)
    users = cursor.fetchall()
    return users

def user_validation(user_id):
    query = f""" SELECT user_id, validation FROM user
            WHERE user_id = {user_id}"""
    cursor.execute(query)
    validation = cursor.fetchall()
    return validation

def user_tracker(user_id: int, shown_word: str= None, is_remembered: bool= None, created_at= None):
    query = """ INSERT INTO record (user_id, word, is_remembered, created_at)
            VALUES (%s, %s, %s, %s) """
    data = (user_id, shown_word[:500], is_remembered, created_at)
    cursor.execute(query, data)
    cnx.commit()

def user_name(user_id: int):
    query = f""" SELECT name from user
                WHERE user_id = {user_id} """
    cursor.execute(query)
    name = cursor.fetchall()
    return name

def user_word_counter(user_id, date_time):
    query = f""" SELECT count(1)
                FROM record
                WHERE user_id = {user_id} and '{date_time}' >= created_at """
    cursor.execute(query)
    today_word_count = cursor.fetchall()[0][0]
    return today_word_count

def user_record(user_id, date_time, language):
    query = f""" SELECT 
                SUM(CASE WHEN is_remembered = 1 THEN 1 ELSE 0 END) as rem,
                SUM(CASE WHEN is_remembered = 0 THEN 1 ELSE 0 END) as not_rem
                FROM record
                WHERE user_id = {user_id} AND ('{date_time}'-created_at <= 7); """
    cursor.execute(query)
    result = cursor.fetchall()
    remember = result[0][0] if result[0][0] != None else 0
    not_remember = result[0][1] if result[0][1] != None else 0
    text = generate_user_record_text(remember, not_remember, language)
    return text

""" WORD'S FUNCTIONS """

def get_new_word():
    query = """ SELECT * FROM word 
                ORDER BY RAND()
                LIMIT 1; """
    cursor.execute(query)
    word = cursor.fetchall()[0]
    return word

def new_word_insert(word, word_type, en_meaning, fa_meaning, ru_meaning, source: int):
    try:
        query = """ INSERT INTO word (word, word_type, en_meaning, fa_meaning, ru_meaning, source)
                VALUES (%s, %s, %s, %s, %s, %s) """
        data = (word, word_type, en_meaning, fa_meaning, ru_meaning, source)
        cursor.execute(query, data)
        cnx.commit()
        print(f"{word} is inserted.")
    except:
        print("DUPLICATE")
        pass

def word_review(user_id, date_time, language):
    query = f""" SELECT DISTINCT(word), count(*)
                FROM record
                WHERE user_id = {user_id} AND ('{date_time}'-created_at <= 7) AND is_remembered = 1
                GROUP BY word; """
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        words = '\n'.join([f'{word[0]} : {word[1]}' for word in result])
        text  = generate_word_review_text(words, language)[0]
    else:
        text = generate_word_review_text(" ", language)[1]
    return text

def user_rem_word_list(user_id):
    query = f""" SELECT DISTINCT(word)
                FROM record
                WHERE user_id = {user_id} AND is_remembered = 1 """
    cursor.execute(query)
    result = cursor.fetchall()
    words_list = [word[0] for word in result]
    return words_list

if __name__ == "__main__":

    #Registring the BOT itself to response to the call_back's
    try:
        register_new_user(7717230198, 'BOT', None, None, 'active', None)
    except:
        pass

