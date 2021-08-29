# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request, json, render_template, session, flash
from flask.sessions import NullSession
import os

from database import db
from response_handler import response_handler

app = Flask(__name__)
app.secret_key = os.urandom(24)

res_hand = response_handler(db)

@app.route('/', methods=["POST", "GET"])
def bot_debug():

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

