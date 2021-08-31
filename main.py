# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request, json, jsonify, render_template, session, flash, make_response
from flask.sessions import NullSession
from flask.wrappers import Response
import os

from database import db
from response_handler import response_handler

app = Flask(__name__)
app.secret_key = os.urandom(24)

res_hand = response_handler(db)

@app.route('/', methods=["POST", "GET"])

def bot_chat():

    if request.method == "POST":
        if not request.is_json:
            return ''

        data = json.loads(request.data)

        if 'type' not in data:
            return ''

        #print(data)

        if 'current_user' not in session:
            session['current_user'] = ''

        if data['type'] == 'update':
            debug_users = db.get_all('debug_users')
            messages = db.get_all('debug_messages', {'debug_user_name': session['current_user']})
            response = {'debug_users': debug_users, 'current_user': session['current_user'], 'messages': messages}
            #print(f'sending:\n{response}')
            return response

        if data['type'] == 'add_user':
            name = data['user_name'].strip()
            if not db.is_one('debug_users', {'name': name}):
                user_id = db.add_one('users', {'type': 'debug', 'session': 'default', 'phase': 0})
                db.add_one('debug_users', {'name': name, 'user_id': user_id})

            debug_users = db.get_all('debug_users')
            response = {'debug_users': debug_users}
            #print(f'sending: {response}')
            return response

        if data['type'] == 'delete_user':
            name = data['user_name'].strip()
            debug_user = db.get_one('debug_users', {'name': name})
            db.delete_all('users', {'id': debug_user['user_id']})
            
            debug_users = db.get_all('debug_users')
            response = {'debug_users': debug_users}
            #print(f'sending: {response}')
            return response

        if data['type'] == 'select_user':
            session['current_user'] = data['user_name']

            messages = db.get_all('debug_messages', {'debug_user_name': session['current_user']})
            response = {'current_user': session['current_user'], 'messages': messages}
            #print(f'sending: {response}')
            return response

        if data['type'] == 'message_new':
            if session['current_user'] == '':
                return {'current_user': ''}

            db.add_one('debug_messages', {'debug_user_name': session['current_user'], 'type': 'user', 'text': data['text']})
            user_id = db.get_one('debug_users', {'name': session['current_user']})['user_id']
            res_hand.run_session({'user_id': user_id, 'body': data['text']})
            messages = db.get_all('debug_messages', {'debug_user_name': session['current_user']})
            response = {'current_user': session['current_user'], 'messages': messages}
            #print(f'sending: {response}')
            return response

    return render_template('index.html')

    return render_template('index.html')

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
            debug_user = db.debug_user_get(user_name)
            db.debug_messages_add(user_name, 'user', message)
            res_hand.run_session({'user_id' : debug_user['user_id'], 'body' : message})

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

