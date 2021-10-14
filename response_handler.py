from flask import session
import vk
import random
import bot_settings
from database import database
from datetime import datetime 

class response_handler:
    def __init__(self, db):
        self.session = vk.Session()
        self.api = vk.API(self.session, v='5.50')
        self.db = db

    def send_message(self, user_id, text):
        debug_user = self.db.get_one('debug_users', {'user_id': user_id})
        if debug_user != None:
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

            self.db.add_one('debug_messages', {'debug_user_name': debug_user['name'], 'type': 'bot', 'text': text, 'date': formatted_date})
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

        user = self.db.get_one('users', {'id': data['user_id']})

        if user['session'] == 'start':
            self.session_start(user['phase'], data)
        elif user['session'] == 'info':
            self.session_info(user['phase'], data)
        elif user['session'] == 'bonus':
            self.session_bonus(user['phase'], data)
        elif user['session'] == 'mailing':
            self.session_mailing(user['phase'], data)
        else:
            if user['session'] != 'default':
                self.update_session(user['id'], 'default', 0)
            self.session_default(user['phase'], data)
        return

    def update_session(self, user_id, session, phase):
        self.db.update_all('users', {'session': session, 'phase': phase}, {'id': user_id})
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

            # session with information and instructions ('/start', '/bot')
            if data['body'] in ['/start', '/bot']:
                self.update_session(data['user_id'], 'start', 0)
                self.run_session(data)
                return
            # session with information about servers
            if data['body'] in ['/info', '/servers']:
                self.update_session(data['user_id'], 'info', 0)
                self.run_session(data)
                return
            # session with information about bonus programms
            if data['body'] in ['/bonus']:
                self.update_session(data['user_id'], 'bonus', 0)
                self.run_session(data)
                return
            # session with mailing
            if data['body'] in ['/mailing']:
                self.update_session(data['user_id'], 'mailing', 0)
                self.run_session(data)
                return
            # session with account
            if data['body'] in ['/account', '/acc']:
                self.update_session(data['user_id'], 'mailing', 0)
                self.run_session(data)
            # invalide command
            else:
                self.send_message(data['user_id'], 'Напишите /start, чтобы узнать о возможностях бота')
                return

        return
    # end of 'session_default' function

    def session_start(self, phase, data):
        if phase == 0:
            message = \
'''Возможные команды:
- '/info' : информация о серверах
- '/bonus' : информация о бонусных программах
- '/mailing' : информация о рассылках
- '/account' : войти или создать аккаунт
- '/help' : задать вопрос админам'''

            self.send_message(data['user_id'], message)
            self.update_session(data['user_id'], 'default', 0)
            return

        return
    # end of 'session_start' function

    def session_info(self, phase, data):
        if phase == 0:

            # information of servers
            # TODO update information
            online = 666

            message = \
'''Информация о сервере:
- онлайн : {0}
- что-то еще: еще что-то
'''.format(online)

            self.send_message(data['user_id'], message)
            self.update_session(data['user_id'], 'default', 0)
            return

        return
    # end of 'session_info' function

    def session_bonus(self, phase, data):
        # information
        if phase == 0:

            # links for more information or discription
            link1 = 'https://en.wikipedia.org/wiki/Tyrannosaurus'

            message = \
'''Бонусные программы:
- бонусная программа 1 : {0}
- что-то еще: еще что-то
'''.format(link1)

            self.send_message(data['user_id'], message)
            self.update_session(data['user_id'], 'default', 0)
            return

        return
    # end of 'session_bonus' function

    def session_mailing(self, phase, data):
        # information
        if phase == 0:

            user_and_mail = self.db.get_all('mailing', {'user_id': data['user_id']})

            user_mailings = []
            for link in user_and_mail:
                user_mailings.append(self.db.get_one('storage', {'id': link['storage_id']}))

            mailings = self.db.get_all('storage', {'type': 'mailing'})

            available = []
            for ml in mailings:
                if ml not in user_mailings:
                    available.append(ml)

            message = "Доступные рассылки:\n"
            if len(available):
                for ml in available:
                    message += str(ml['num']) + ') ' + ml['text'] + '\n'
            else:
                message += "Нет доступных рассылок ¯\_(ツ)_/¯\n"

            message += "Ваши подписки:\n"

            if len(user_mailings):
                for ml in user_mailings:
                    message += str(ml['num']) + ') ' + ml['text'] + '\n'
            else:
                message += "У вас нет подписок ¯\_(ツ)_/¯\n"

            message += \
'''
'/sub (номер рассылки)': подписаться на рассылку
'/unsub (номер рассылки)': отписаться от рассылки
'/quit': выйти из раздела 'рассылки'
'''

            self.send_message(data['user_id'], message)
            self.update_session(data['user_id'], 'mailing', 1)
            return

        if phase == 1:
            # handle response

            cmd = data['body'].split()
            if len(cmd) < 1 or len(cmd) > 2 or cmd[0] not in ['/sub', '/unsub', '/quit']:
                self.update_session(data['user_id'], 'mailing', 0)
                self.run_session(data)
                return

            if  data['body'] == '/quit':
                self.update_session(data['user_id'], 'default', 0)
                return

            if len(cmd) != 2 or not cmd[1].isdigit():
                self.update_session(data['user_id'], 'mailing', 0)
                self.run_session(data)
                return


            if cmd[0] == "/sub":
                storage = self.db.get_one('storage', {'type': 'mailing', 'num': cmd[1]})
                if storage != None:
                    self.db.add_one('mailing', {'user_id': data['user_id'], 'storage_id': storage['id']})
                self.update_session(data['user_id'], 'mailing', 0)
                self.run_session(data)
                return

            if cmd[0] == "/unsub":
                storage = self.db.get_one('storage', {'type': 'mailing', 'num': cmd[1]})
                if storage != None:
                    self.db.delete_all('mailing', {'user_id': data['user_id'], 'storage_id': storage['id']})
                self.update_session(data['user_id'], 'mailing', 0)
                self.run_session(data)
                return

        return
    # end of 'session_mailing' function

    def session_account(self, phase, data):
        if phase == 0:
            # instructions
            message = \
'''Возможные команды:
- '/singin': Войти в аккаунт
- '/singup': Создать аккаунт
- '/quit': Выйти из раздела 'аккаунт'
'''
            self.send_message(data['user_id'], message)
            self.update_session(data['user_id'], 'account', 1)
            return
        
        if phase == 1:

            # handle response
            if data['body'] not in ['/singin', '/singout']:
                self.update_session(data['user_id'], 'account', 0)
                self.run_session()


        return
    # end of 'session_account' function
'''
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
        '''