from Bot_auth import bot_auth
from db_interaction import *

bot = bot_auth()

user_id = None
def authentication(message):
    global user_id
    user_id = message.from_user.id
    is_valid = {user[0]: user[1] for user in user_validation(user_id)}

    if is_valid.get(user_id) == 'active':
        print(f"{user_id} is interacting and authorized")
        return True
        
    else:
        contact_support = '@HesamWahib'
        bot.send_message(message.chat.id, """You are not registered. Please use /register command to compelete your registration.
                                            \nIf you've already done please contact (%s)""" % contact_support)
        
        print(f"{user_id} is interacting and NOT authorized")