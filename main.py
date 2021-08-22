# A very simple Flask Hello World app for you to get started with...
from database import database
from flask import Flask, request, json, render_template, session
import os

from flask.sessions import NullSession

import response_handler
import database


app = Flask(__name__)
app.secret_key = os.urandom(24)

session['db'] = database

reshand = response_handler()

#@app.route('/', methods=['POST'])
'''
@app.route('/', methods=['GET'])
def processing():
    #Распаковываем json из пришедшего POST-запроса
    data = json.loads(request.data)

    if 'type' not in data.keys():
        return 'not ok'
    if data['type'] == 'confirmation':
        return bot_settings.CONFIRMATION_TOKEN
    if 'object' not in data.keys():
        return 'not ok'

    #if data['type'] == 'message_new':
        #reshand.run_session(data['object'])

    return 'ok'
'''
links = [{'path' : '/bot_debug', 'text' : 'Bot debug'},
         {'path' : '/information', 'text' : 'Information'},
         {'path' : '/statistics', 'text' : 'Statistics'}
]


messages = [{'author' : 'bot', 'text': 'Im Bot'},
{'author' : 'user', 'text': 'Im User'},
{'author' : 'bot', 'text': 'Hello\nHello!!!!'},
{'author' : 'user', 'text': 'Hiffffffffff, bot'},
] * 5

debug_users = [{'name' : 'Anton', 'id' : 23123},
               {'name' : 'Anton4', 'id' : 23123},
               {'name' : 'Antdfso5n', 'id' : 23123},
               {'name' : 'Adsfnto5n', 'id' : 23123},
               {'name' : 'Anasasdto5n', 'id' : 23123}]


@app.route('/bot_debug', methods=["POST", "GET"])
def bot_debug():
    if request.method == 'POST':
        if 'user' in request.form:
            session['current_user'] = request.form['user']
            print("Updated")
        elif 'message_new' in request.form:
            print("New message:", request.form['new_message'])
        print(dict(request.form))
    if 'current_user' in session:
        print("User:", session['current_user'])
    else:
        print("No user")
    return render_template('bot_debug.html',
        title='Bot debug', messages = messages,
        debug_users=debug_users,
        current_user=(session['current_user'] if 'current_user' in session else None))

@app.route('/')
def main_get():
    if request.method == 'POST':
        return 'ok'
    return render_template('index.html', title='Index', links = links)

