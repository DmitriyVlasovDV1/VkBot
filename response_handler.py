from flask import session
import vk
import random
import bot_settings
from database import database

class response_handler:
    def __init__(self, db):
        self.session = vk.Session()
        self.api = vk.API(self.session, v='5.50')
        self.db = db

    def send_message(self, user_id, text):
        debug_user = self.db.get_one('debug_users', {'user_id': user_id})
        if debug_user != None:
            self.db.add_one('debug_messages', {'debug_user_name': debug_user.name, 'type': 'bot', 'text': text})
        else:
            self.api.messages.send(access_token=bot_settings.ACCESS_TOKEN,
                user_id=str(user_id),
                message=text,
                random_id=random.getrandbits(64))
        return

    def run_session(self, data):
        if 'body' not in data.keys() or 'user_id' not in data.keys():
            return

        if self.db.get_one('users', {'id': data['user_id']}) == None:
            return

        session = self.database.users_get_session(data['user_id'])

        if session['session'] == 'default':
            self.session_default(session['phase'], data)
        elif session['session'] == 'help':
            self.session_help(session['phase'], data)
        return

    def update_session(self, user_id, session, phase):
        self.db.update_all('users', {'id': user_id, 'session': session, 'phase': phase})
        return

    def list_erase(self, user_id):
        self.db.delete_all('list', {'user_id': user_id})
        return

    def list_push_back(self, user_id, type, value):
        element = {'user_id' : user_id, 'type': type, 'num': 0, 'text': ''}
        if type == 'text':
            element['text'] = value
        elif type == 'num':
            element['num'] = value
        self.db.add_one('list', element)
        return

    def list_get(self, user_id):
        elements = self.db.get_all('list', {'user_id': user_id})
        
        res = []
        for value in elements:
            if value['type'] == 'text':
                res.append(value['text'])
            elif value['type'] == 'num':
                res.append(value['num'])
        return res

    def list_erase(self, user_id):
        self.db.delete_all('list', {'user_id': user_id})
        return

    def session_default(self, phase, data):
        if phase == 0:
            if data['body'] not in ['/help']:
                self.send_message(data['user_id'], 'Такой команды нет(')
                return

            if data['body'] == '/help':
                self.update_session(data['user_id'], 'help', 0)
                self.run_session(data)
                return
        return

    def session_help(self, phase, data):
        if phase == 0:
            self.send_message(data['user_id'], 'Напишите Y/N')
            self.update_session(data['user_id'], 'help', 1)
            return

        if phase == 1:
            if data['body'] not in ['Y', 'N', '/quit']:
                self.send_message(data['user_id'], 'Напишите Y/N или /quit чтобы выйти')
                return

            if  data['body'] == '/quit':
                self.update_session(data['user_id'], 'default', 0)
                return

            self.list_erase(data['user_id'])
            self.list_push_back(data['user_id'], 'text', data['body'])

            self.update_session(data['user_id'], 'help', 2)

            self.send_message(data['user_id'], 'Напишите число от 1 до 10')

        if phase == 2:
            if data['body'] != '/quit' and (not data['body'].isdigit() or not 1 <= int(data['body']) <= 10):
                self.send_message(data['user_id'], 'Напишите число от 1 до 10 или /quit чтобы выйти')
                return

            if  data['body'] == '/quit':
                self.update_session(data['user_id'], 'default', 0)
                return

            self.list_push_back(data['user_id'], 'num', data['body'])
            list = self.list_get(data['user_id'])
            self.list_erase(data['user_id'])

            self.update_session(data['user_id'], 'default', 0)

            self.send_message(data['user_id'], f'Ваши ответы: {list[0]}, {list[1]}')

        return