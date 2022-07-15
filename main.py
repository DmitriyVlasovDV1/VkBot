# Libraries
import os
import random
from datetime import datetime
import bcrypt

# Flask
from flask import Flask, request, json, jsonify, render_template, session, flash, make_response, url_for
from flask.sessions import NullSession
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

# My modules
import statistics
from statistics import components
import bot_settings

# App configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{bot_settings.DB_USER}:{bot_settings.DB_PASSWORD}@{bot_settings.DB_HOST}/{bot_settings.DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'vlasov.dima2004@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'vlasov.dima2004@gmail.com'
app.config['MAIL_PASSWORD'] = bot_settings.MAIL_PSWD
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)            


# db
db = SQLAlchemy(app)

# serializer
serializer = URLSafeTimedSerializer('Secrete')

# database tables
from response_handler import *


# tmp creation
db.create_all()

# response handler
dbw = DBWrapper(db)
res_hand = response_handler(dbw)

@app.route('/', methods=["POST", "GET"])
def bot_chat():

    if request.method == "POST":
        if not request.is_json:
            return ''

        data = json.loads(request.data)


        if 'type' not in data:
            return ''


        response = get_chat_response(data)
        if response != None:
            return response

        response = get_mailing_response(data)
        if response != None:
            return response

    return render_template('nd_index.html')

# get response for chat requests
def get_chat_response(data):

    if 'current_user' not in session:
        session['current_user'] = ''

    if data['type'] == 'chat_update':
        debug_users = dbw.get_all(DebugUsers)
        messages = dbw.get_all(DebugMessages, {'debug_user_name': session['current_user']})
        response = {'debug_users': debug_users, 'current_user': session['current_user'], 'messages': messages}
        #print(f'sending:\n{response}')
        return response

    if data['type'] == 'add_user':
        name = data['user_name'].strip()
        if not dbw.is_one(DebugUsers, {'name': name}):
            user_id = dbw.add_one(Users, {'type': 'debug', 'session': 'default', 'phase': 0})
            dbw.add_one(DebugUsers, {'name': name, 'user_id': user_id})

        debug_users = dbw.get_all(DebugUsers)
        response = {'debug_users': debug_users}
        #print(f'sending: {response}')
        return response

    if data['type'] == 'delete_user':
        if session['current_user'] == data['user_name']:
            session['current_user'] = ''

        name = data['user_name'].strip()
        debug_user = dbw.get_one(DebugUsers, {'name': name})
        dbw.delete_all(Users, {'id': debug_user['user_id']})

        debug_users = dbw.get_all(DebugUsers)
        response = {'debug_users': debug_users}
        #print(f'sending: {response}')
        return response

    if data['type'] == 'select_user':
        session['current_user'] = data['user_name']

        messages = dbw.get_all(DebugMessages, {'debug_user_name': session['current_user']})
        response = {'current_user': session['current_user'], 'messages': messages}
        #print(f'sending: {response}')
        return response

    if data['type'] == 'message_new':
        if session['current_user'] == '':
            return {'current_user': ''}

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        dbw.add_one(DebugMessages, {'debug_user_name': session['current_user'], 'type': 'user', 'text': data['text'], 'date': formatted_date})

        user_id = dbw.get_one(DebugUsers, {'name': session['current_user']})['user_id']
        res_hand.run_session({'user_id': user_id, 'body': data['text']})

        messages = dbw.get_all(DebugMessages, {'debug_user_name': session['current_user']})
        response = {'current_user': session['current_user'], 'messages': messages}
        #print(f'sending: {response}')
        return response

    # sing up
    if data['type'] == 'singup':

        name = data['name']
        password = data['password']
        email = data['email']

        response = {'is_unique_name': True, 'is_unique_email': True, 'is_correct_email': True}

        if dbw.get_one(Admins, {'email': email}) != None:
            response['is_unique_email'] = False
            return response

        if dbw.get_one(Admins, {'name': name}) != None:
            response['is_unique_name'] = False
            return response

        token_self = serializer.dumps({'type': 'self', 'email': email}, salt='dv1krasavchik')
        msg_self = Message("Confirm your email", recipients=[email])
        link_self = url_for('email_confirmation', token=token_self, _external=True)
        msg_self.html = f'To confirm your email follow the <a href={link_self}>link</a>'

        try:
            mail.send(msg_self)
        except:
            response['is_correct_email'] = False
            return response


        token_boss = serializer.dumps({'type': 'boss', 'email': email}, salt='dv1krasavchik')
        msg_boss = Message("Registration request", recipients=['vlasov.dima2004@gmail.com'])
        link_boss = url_for('email_confirmation', token=token_boss, _external=True)
        msg_boss.html = f'User with name: "{name}" and email: {email} wants to join admin club.<br>To confirm follow the <a href={link_boss}>link</a>'

        try:
            mail.send(msg_boss)
        except:
            pass

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        dbw.add_one(Admins, {'name': name, 'email': email, 'hashed_password': hashed_password, 'rank': 'zero',
            'boss_confirmation': False, 'self_confirmation': False})
        return response

    # sing in
    if data['type'] == 'singin':

        name = data['name']
        password = data['password']

        response = {'is_name_exists': True, 'is_correct_password': True,
            'is_confirmed_boss': True, 'is_confirmed_self': True}

        if dbw.get_one(Admins, {'name': name}) == None:
            response['is_name_exists'] = False
            return response

        admin = dbw.get_one(Admins, {'name': name})

        if admin['self_confirmation'] == False:
            response['is_confirmed_self'] = False
            return response

        if admin['boss_confirmation'] == False:
            response['is_confirmed_boss'] = False
            return response
        
        if not bcrypt.checkpw(password.encode('utf-8'), admin['hashed_password'].encode('utf-8')):
            response['is_correct_password'] = False
            return response


        return response

    return None


@app.route('/email_confirmation/<token>', methods=["GET"])
def email_confirmation(token):

    try:
        tmp = serializer.loads(token, salt='dv1krasavchik')
        type = tmp['type']
        email = tmp['email']

        if type == 'self':
            dbw.update_all(Admins, {'self_confirmation': True}, {'email': email})
        
        elif type == 'boss':
            dbw.update_all(Admins, {'boss_confirmation': True}, {'email': email})


        return render_template('email_confirmation.html', is_confirmed=True)
    except:
        return render_template('email_confirmation.html', is_confirmed=False)



    


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


# get response for mailing requests
def get_mailing_response(data):

    # init current mailing id
    if 'current_mailing_id' not in session:
        session['current_mailing_id'] = -1

    # req for update (selector)
    if data['type'] == 'mailing_update':
        mailings = dbw.get_all(Mailings)
        response = {'mailings': mailings, 'exeError': ''}
        return response

    # req for add new mailing
    if data['type'] == 'add_mailing':

        name = data['mailing_name'].strip()
        execution_error = ''
        if not dbw.is_one(Mailings, {'name': name}):
            dbw.add_one(Mailings, {'name': name, 'is_active': 0})
        else:
            execution_error = 'existing name'

        mailings = dbw.get_all(Mailings)
        response = {'mailings': mailings, 'exeError': execution_error}
        return response

    # req for deleting mailing
    if data['type'] == 'delete_mailing':
        mailing = data['mailing']
        if dbw.is_one(Mailings, {'id': mailing['id']}):
            dbw.delete_all(Mailings, {'id': mailing['id']})

        mailings = dbw.get_all(Mailings)
        response = {'mailings': mailings, 'exeError': ''}
        return response

    # req for update mailing
    if data['type'] == 'update_mailing':
        mailing = data['mailing']
        if dbw.is_one(Mailings, {'id': mailing['id']}):
            dbw.update_all(Mailings, {'is_active': mailing['is_active'], 'name': mailing['name']}, {'id': mailing['id']})

        mailings = dbw.get_all(Mailings)
        response = {'mailings': mailings, 'exeError': ''}
        return response

    # req for selecting mailing
    if data['type'] == 'select_mailing':
        mailing = data['mailing']
        if dbw.is_one(Mailings, {'id': mailing['id']}):
            session['current_mailing_id'] = mailing['id']
            messages = dbw.get_all(MailingMessages, {'mailing_id': mailing['id']})
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

        if session['current_mailing_id'] != -1 and dbw.is_one(Mailings, {'id': session['current_mailing_id']}):
            mailing = dbw.get_one(Mailings, {'id': session['current_mailing_id']})

            if dbw.is_one('mailing_messages', {'mailing_id': session['current_mailing_id'], 'name': name}):
                execution_error = 'existing name'
            else:
                if time != None:
                    dbw.add_one(MailingMessages, {'mailing_id': session['current_mailing_id'], 'name': name, 'text': text, 'is_active': is_active, 'time': time})
                else:
                    dbw.add_one(MailingMessages, {'mailing_id': session['current_mailing_id'], 'name': name, 'text': text, 'is_active': is_active})

            messages = dbw.get_all(MailingMessages, {'mailing_id': mailing['id']})
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
        if session['current_mailing_id'] != -1 and dbw.is_one(Mailings, {'id': session['current_mailing_id']}):
            mailing = dbw.get_one(Mailings, {'id': session['current_mailing_id']})
            if dbw.is_one(MailingMessages, {'mailing_id': session['current_mailing_id'], 'name': name}) and \
                (dbw.get_one(MailingMessages, {'mailing_id': session['current_mailing_id'], 'name': name}))['id'] != msg['id']:
                execution_error = 'existing name'
            else:
                dbw.update_all(MailingMessages, {'name': name, 'text': text, 'is_active': is_active, 'time': time}, {'id': msg['id']})
            messages = dbw.get_all(MailingMessages, {'mailing_id': mailing['id']})
            response = {'current_mailing': mailing, 'messages': messages, 'exeError': execution_error}
            res_hand.setup_mailing_scheduler()
            return response

    # req for deleting message
    if data['type'] == 'delete_message':
        msg = data['message']
        execution_error = ''

        if session['current_mailing_id'] != -1:
            mailing = dbw.get_one(Mailings, {'id': session['current_mailing_id']})
            dbw.delete_all(MailingMessages, {'id': msg['id']})
            messages = dbw.get_all(MailingMessages, {'mailing_id':  mailing['id']})
            response = {'current_mailing': mailing, 'messages': messages, 'exeError': execution_error}
            res_hand.setup_mailing_scheduler()
            return response

    # req for sending message
    if data['type'] == 'send_message':
        print('!!!!!!!!!!!!!!!!!')
        res_hand.send_mailing_message(data['message'])
        return {}


    return None




