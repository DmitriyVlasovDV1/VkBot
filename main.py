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
            if session['current_user'] == data['user_name']:
                session['current_user'] = ''

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


@app.route('/mailing', methods=["POST", "GET"])
def bot_mailing():
    if request.method == "POST":
        if not request.is_json:
            return ''

        # get data
        data = json.loads(request.data)

        if 'type' not in data:
            return ''

        # init current mailing id
        if 'current_mailing_id' not in session:
            session['current_mailing_id'] = -1

        # req for update (selector)
        if data['type'] == 'update':
            mailings = db.get_all('mailings')
            response = {'mailings': mailings, 'exeError': ''}
            return response

        # req for add new mailing
        if data['type'] == 'add_mailing':
            name = data['mailing_name'].strip()
            execution_error = ''
            if not db.is_one('mailings', {'name': name}):
                db.add_one('mailings', {'name': name, 'is_active': 0})
            else:
                execution_error = 'existing name'

            mailings = db.get_all('mailings')
            response = {'mailings': mailings, 'exeError': execution_error}
            return response

        # req for deleting mailing
        if data['type'] == 'delete_mailing':
            mailing = data['mailing']
            if db.is_one('mailings', {'id': mailing['id']}):
                db.delete_all('mailings', {'id': mailing['id']})

            mailings = db.get_all('mailings')
            response = {'mailings': mailings, 'exeError': ''}
            return response

        # req for update mailing
        if data['type'] == 'update_mailing':
            mailing = data['mailing']
            if db.is_one('mailings', {'id': mailing['id']}):
                db.update_all('mailings', {'is_active': mailing['is_active'], 'name': mailing['name']}, {'id': mailing['id']})

            mailings = db.get_all('mailings')
            response = {'mailings': mailings, 'exeError': ''}
            return response

        # req for selecting mailing
        if data['type'] == 'select_mailing':
            mailing = data['mailing']
            if db.is_one('mailings', {'id': mailing['id']}):
                session['current_mailing_id'] = mailing['id']
                messages = db.get_all('mailing_messages', {'mailing_id': mailing['id']})
                response = {'current_mailing': mailing, 'messages': messages, 'exeError':''}
                return response
            return {}

        # req for adding message
        if data['type'] == 'add_message':

            msg = data['message']
            name = msg['name']
            text = msg['text']
            is_active = msg['is_active']
            time = msg['time']

            execution_error = ''

            if session['current_mailing_id'] != -1 and db.is_one('mailings', {'id': session['current_mailing_id']}):
                mailing = db.get_one('mailings', {'id': session['current_mailing_id']})

                if db.is_one('mailing_messages', {'mailing_id': session['current_mailing_id'], 'name': name}):
                    execution_error = 'existing name'
                else:
                    if time != None:
                        db.add_one('mailing_messages', {'mailing_id': session['current_mailing_id'], 'name': name, 'text': text, 'is_active': is_active, 'time': time})
                    else:
                        db.add_one('mailing_messages', {'mailing_id': session['current_mailing_id'], 'name': name, 'text': text, 'is_active': is_active})

                messages = db.get_all('mailing_messages', {'mailing_id': mailing['id']})
                response = {'current_mailing': mailing, 'messages': messages, 'exeError': execution_error}
                res_hand.setup_mailing_scheduler()
                return response

        # req for update message
        if data['type'] == 'update_message':
            msg = data['message']
            name = msg['name']
            text = msg['text']
            is_active = msg['is_active']
            time = msg['time']

            execution_error = ''
            if session['current_mailing_id'] != -1 and db.is_one('mailings', {'id': session['current_mailing_id']}):
                mailing = db.get_one('mailings', {'id': session['current_mailing_id']})
                if db.is_one('mailing_messages', {'mailing_id': session['current_mailing_id'], 'name': name}) and \
                    (db.get_one('mailing_messages', {'mailing_id': session['current_mailing_id'], 'name': name}))['id'] != msg['id']:
                    execution_error = 'existing name'
                else:
                    db.update_all('mailing_messages', {'name': name, 'text': text, 'is_active': is_active, 'time': time}, {'id': msg['id']})
                messages = db.get_all('mailing_messages', {'mailing_id': mailing['id']})
                response = {'current_mailing': mailing, 'messages': messages, 'exeError': execution_error}
                res_hand.setup_mailing_scheduler()
                return response

        # req for deleting message
        if data['type'] == 'delete_message':
            msg = data['message']
            execution_error = ''

            if session['current_mailing_id'] != -1:
                mailing = db.get_one('mailings', {'id': session['current_mailing_id']})
                db.delete_all('mailing_messages', {'id': msg['id']})
                messages = db.get_all('mailing_messages', {'mailing_id':  mailing['id']})
                response = {'current_mailing': mailing, 'messages': messages, 'exeError': execution_error}
                res_hand.setup_mailing_scheduler()
                return response

        # req for sending message
        if data['type'] == 'send_message':
            res_hand.send_mailing_message(data['message'])
            return {}


    return render_template('mailing.html')