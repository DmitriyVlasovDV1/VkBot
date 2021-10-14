# Libraries
import os
import random
from datetime import datetime

# Flask
from flask import Flask, request, json, jsonify, render_template, session, flash, make_response
from flask.sessions import NullSession
from flask.wrappers import Response

# My modules
from database import db
from response_handler import response_handler
import statistics
from statistics import components

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

            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

            db.add_one('debug_messages', {'debug_user_name': session['current_user'], 'type': 'user', 'text': data['text'], 'date': formatted_date})

            user_id = db.get_one('debug_users', {'name': session['current_user']})['user_id']
            res_hand.run_session({'user_id': user_id, 'body': data['text']})

            messages = db.get_all('debug_messages', {'debug_user_name': session['current_user']})
            response = {'current_user': session['current_user'], 'messages': messages}
            #print(f'sending: {response}')
            return response

    return render_template('index.html')

@app.route('/statistics')
def bot_statistics():
    statistics.initialize_plots()

    plot = statistics.create_line_plot([1, 2, 3], [1, 3, 2])

    comp = components(plot)
    plot_script, plot_div = components(plot, "Title")

    return render_template('statistics.html',
        plot_div=plot_div,
        plot_script=plot_script,
        js_resources=statistics.INLINE.render_js(),
        css_resources=statistics.INLINE.render_css())