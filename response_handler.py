from flask import session
import vk
import random
import bot_settings
from database import database

class response_handler:
    def __init__(self, db):
        self.session = vk.Session()
        self.api = vk.API(self.session, v='5.50')
        self.database = db

    def send_message(self, user_id, text):
        debug_user_id = self.database.is_debug_user(user_id)
        if debug_user_id != None:
            self.database.debug_messages_add(debug_user_id, 'bot', text)
        else:
            self.api.messages.send(access_token=bot_settings.ACCESS_TOKEN,
                user_id=str(user_id),
                message=text,
                random_id=random.getrandbits(64))
        return

    def run_session(self, data):
        if 'body' not in data.keys() or 'user_id' not in data.keys():
            return

        if not self.database.is_user(data['user_id']):
            return

        session = self.database.users_get_session(data['user_id'])

        if session['session'] == 'default':
            self.session_default(session['phase'], data)
        elif session['session'] == 'help':
            self.session_help(session['phase'], data)
        return


    def session_default(self, phase, data):
        if phase == 0:
            if data['body'] not in ['/help']:
                self.send_message(data['user_id'], 'Такой команды нет(')
                return

            if data['body'] == '/help':
                self.database.users_update_session(data['user_id'], 'help', 0)
                self.run_session(data)
                return
        return


    def session_help(self, phase, data):
        if phase == 0:
            self.send_message(data['user_id'], 'Напишите Y/N')
            self.database.users_update_session(data['user_id'], 'help', 1)
            return

        if phase == 1:
            if data['body'] not in ['Y', 'N', '/quit']:
                self.send_message(data['user_id'], 'Напишите Y/N или /quit чтобы выйти')

            if  data['body'] == '/quit':
                self.database.users_update_session(data['user_id'], 'default', 0)
                return

            self.database.list_erase(data['user_id'])
            self.database.list_push_back(data['user_id'], 1, data['body'])

            self.database.users_update_session(data['user_id'], 'help', 2)

            self.send_message(data['user_id'], 'Напишите число от 1 до 10')

        if phase == 2:
            if data['body'] != '/quit' and (not data['body'].isdigit() or not 1 <= int(data['body']) <= 10):
                self.send_message(data['user_id'], 'Напишите число от 1 до 10 или /quit чтобы выйти')
                return

            if  data['body'] == '/quit':
                self.database.users_update_session(data['user_id'], 'default', 0)
                return

            self.database.list_push_back(data['user_id'], 0, data['body'])
            list = self.database.list_get(data['user_id'])
            self.database.list_erase(data['user_id'])

            self.database.users_update_session(data['user_id'], 'default', 0)

            self.send_message(data['user_id'], 'Ваши ответы:' + str(list))

        return

