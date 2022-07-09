from flask import session
import vk
import random
import bot_settings
from database import database
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from new_db import *


class response_handler:
    def __init__(self, db):
        self.session = vk.session
        self.api = vk.API(self.session, v='5.50')
        self.db = db
        self.mailing_scheduler = BackgroundScheduler()
        self.setup_mailing_scheduler()
        self.mailing_scheduler.start()


    # setup mailing scheduler
    def setup_mailing_scheduler(self):
        self.mailing_scheduler.remove_all_jobs()
        messages = self.db.get_all(MailingMessages)

        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for msg in messages:
            if msg['time'] != None and msg['time'] != '0000-00-00 00:00:00' and msg['time'] > datetime.now():
                self.mailing_scheduler.add_job(self.send_mailing_message, 'date', run_date=msg['time'], args=[msg])
        return

    # send mailing message
    def send_mailing_message(self, msg):

        if not self.db.is_one(Mailings, {'id': msg['mailing_id']}):
            return

        mailing = self.db.get_one(Mailings, {'id': msg['mailing_id']})

        if not mailing['is_active']:
            return

        links = self.db.get_all(MailingAndUser, {'mailing_id': msg['mailing_id']})

        for link in links:
            if not self.db.is_one(Users, {'id': link['user_id']}):
                continue

            user = self.db.get_one(Users, {'id': link['user_id']})

            self.send_message(user['id'], msg['text'])
        return

    # send message to user
    def send_message(self, user_id, text):
        debug_user = self.db.get_one(DebugUsers, {'user_id': user_id})
        if debug_user != None: # check is debug user
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

            self.db.add_one(DebugMessages, {'debug_user_name': debug_user['name'], 'type': 'bot', 'text': text, 'date': formatted_date})
        else:
            self.api.messages.send(access_token=bot_settings.ACCESS_TOKEN,
                user_id=str(user_id),
                message=text,
                random_id=random.getrandbits(64))
        return

    # run session process
    def run_session(self, data):
        if 'body' not in data.keys() or 'user_id' not in data.keys():
            return

        if self.db.get_one(Users, {'id': data['user_id']}) == None:
            return

        # get user
        user = self.db.get_one(Users, {'id': data['user_id']})

        # run current session
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

    # update session in database
    def update_session(self, user_id, session, phase):
        self.db.update_all(Users, {'session': session, 'phase': phase}, {'id': user_id})
        return

    # clear tmp list for user
    def list_erase(self, user_id):
        self.db.delete_all(List, {'user_id': user_id})
        return

    # add value to tmp list
    def list_push_back(self, user_id, type, value):
        element = {'user_id' : user_id, 'type': type, 'num': 0, 'text': ''}
        if type == 'text':
            element['text'] = value
        elif type == 'num':
            element['num'] = value
        self.db.add_one(List, element)
        return

    # get values from tmp list
    def list_get(self, user_id):
        elements = self.db.get_all(List, {'user_id': user_id})

        res = []
        for value in elements:
            if value['type'] == 'text':
                res.append(value['text'])
            elif value['type'] == 'num':
                res.append(value['num'])
        return res

    # default session
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
            if data['body'] in ['/mailing', '/mail']:
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

    # start session
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

    # info session
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

    # bonus session
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

    # mailing session
    def session_mailing(self, phase, data):
        # information
        if phase == 0:

            #self.db.numerate_all('mailings', 'num', {'is_active': 1})

            user_and_mail = self.db.get_all('mailing_and_user', {'user_id': data['user_id']})

            user_mailings = []
            for link in user_and_mail:
                user_mailings.append(self.db.get_one('mailings', {'id': link['mailing_id'], 'is_active': 1}))

            mailings = self.db.get_all('mailings', {'is_active': 1})

            available = []
            for ml in mailings:
                if ml not in user_mailings:
                    available.append(ml)

            message = '''--------------------------------------------------
Доступные рассылки:
--------------------------------------------------\n\n'''

            if len(available):
                for ml in available:
                    message += str(ml['num']) + ') ' + ml['name'] + '\n'
            else:
                message += "Нет доступных рассылок ¯\_(ツ)_/¯\n"

            message += '''\n--------------------------------------------------
Ваши подписки:
--------------------------------------------------\n\n'''
            if len(user_mailings):
                for ml in user_mailings:
                    message += str(ml['num']) + ') ' + ml['name'] + '\n'
            else:
                message += "У вас нет подписок ¯\_(ツ)_/¯\n"

            self.send_message(data['user_id'], message)
            message = \
''''/sub (номер рассылки)': подписаться на рассылку
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
                mailing = self.db.get_one('mailings', {'is_active': 1, 'num': cmd[1]})
                if mailing != None:
                    self.db.add_one('mailing_and_user', {'user_id': data['user_id'], 'mailing_id': mailing['id']})
                self.update_session(data['user_id'], 'mailing', 0)
                self.run_session(data)
                return

            if cmd[0] == "/unsub":
                mailing = self.db.get_one('mailings', {'is_active': 1, 'num': cmd[1]})
                if mailing != None:
                    self.db.delete_all('mailing_and_user', {'user_id': data['user_id'], 'mailing_id': mailing['id']})
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
- '/singout':
- '/quit': Выйти из раздела 'аккаунт'
'''
            self.send_message(data['user_id'], message)
            self.update_session(data['user_id'], 'account', 1)
            return

        if phase == 1:
            # handle response
            if data['body'] not in ['/singin', '/singup']:
                self.update_session(data['user_id'], 'account', 0)
                self.run_session()
                return

            if data['body'] == '/singup':
                self.update_session(data['user_id'], 'account', 2)
                self.run_session()
                return

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