# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request, json, render_template, session, flash
import os

from flask.sessions import NullSession

from response_handler import response_handler
from database import database


app = Flask(__name__)
app.secret_key = os.urandom(24)

db = database()
reshand = response_handler(db)

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
        if 'selected_user' in request.form:
            session['current_user'] = request.form['selected_user']
        elif 'add_user' in request.form:
            if db.debug_users_add(request.form['add_user']):
                flash('User added!', 'success')
            else:
                flash('User already exists!', 'error')
            
        elif 'message_new' in request.form and 'current_user' in session:
            user_name = session['current_user']
            message = request.form['message_new']
            db.debug_messages_add(user_name, 'user', message)
            #response_handler({'user_id' : user_id, 'body' : message})

    debug_users = db.debug_users_get()
    if 'current_user' in session:
        current_user = db.debug_user_get(session['current_user'])
        messages = db.debug_messages_get(session['current_user'])
    else:
        current_user = None
        messages = []

    return render_template('bot_debug.html',
        title='Bot debug', messages = messages,
        debug_users=debug_users,
        current_user=current_user)

@app.route('/')
def main_get():
    db = database()
    reshand = response_handler()

    if request.method == 'POST':
        return 'ok'
    return render_template('index.html', title='Index', links = links)

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
