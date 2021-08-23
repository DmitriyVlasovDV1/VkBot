import pymysql
import bot_settings

class database:
    def __init__(self):
        self.connection = pymysql.connect(
            host=bot_settings.DB_HOST,
            user=bot_settings.DB_USER,
            password=bot_settings.DB_PASSWORD,
            database=bot_settings.DB_NAME)

        self.cursor = self.connection.cursor()
        command = 'CREATE TABLE IF NOT EXISTS users (\
                                        id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                                        type VARCHAR(255) NOT NULL,\
                                        session VARCHAR(255) NOT NULL,\
                                        phase INT NOT NULL)'
        self.cursor.execute(command)

        command = 'CREATE TABLE IF NOT EXISTS real_users (\
                                        vk_id INT PRIMARY KEY,\
                                        user_id INT,\
                                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'    
        self.cursor.execute(command)

        command = 'CREATE TABLE IF NOT EXISTS debug_users (\
                                        name VARCHAR(255) PRIMARY KEY,\
                                        user_id INT,\
                                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'    
        self.cursor.execute(command)

        command = 'CREATE TABLE IF NOT EXISTS debug_messages (\
                                        id INT PRIMARY KEY AUTO_INCREMENT,\
                                        debug_user_name VARCHAR(255),\
                                        type VARCHAR(255),\
                                        text VARCHAR(255),\
                                        FOREIGN KEY (debug_user_name) REFERENCES debug_users (name) ON DELETE CASCADE)'    
        self.cursor.execute(command)

        command = 'CREATE TABLE IF NOT EXISTS list (\
                                        id INT PRIMARY KEY AUTO_INCREMENT,\
                                        user_id INT,\
                                        type VARCHAR(255),\
                                        num INT,\
                                        text VARCHAR(255),\
                                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
        self.cursor.execute(command)

        command = 'CREATE TABLE IF NOT EXISTS account (\
                                        id INT PRIMARY KEY AUTO_INCREMENT,\
                                        user_id INT,\
                                        name VARCHAR(255),\
                                        age INT,\
                                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
        self.cursor.execute(command)

        command = 'CREATE TABLE IF NOT EXISTS storage (\
                                        id INT PRIMARY KEY AUTO_INCREMENT,\
                                        type VARCHAR(255),\
                                        num INT,\
                                        text VARCHAR(255))'
        self.cursor.execute(command)

        command = 'CREATE TABLE IF NOT EXISTS mailing (\
                                        id INT PRIMARY KEY AUTO_INCREMENT,\
                                        user_id INT,\
                                        storage_id INT,\
                                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,\
                                        FOREIGN KEY (storage_id) REFERENCES storage (id) ON DELETE CASCADE)'
        self.cursor.execute(command)

#Users tables
    def is_user(self, user_id):
        command = "SELECT * FROM users WHERE id = {0}".format(user_id)
        self.cursor.execute(command)

        data = self.cursor.fetchone()
        return data != None

    def users_get_session(self, user_id):
        command = 'SELECT session, phase FROM users WHERE id = {0}'.format(user_id)
        self.cursor.execute(command)

        data = self.cursor.fetchone()
        if data == None:
            return None
        return {'session' : data[0], 'phase' : data[1]}

    def users_update_session(self, user_id, session, phase):
        command = "UPDATE users SET session = '{0}', phase = {1} WHERE id = {2}".format(session, phase, user_id)
        self.cursor.execute(command)
        return

# Real users tables
    def real_users_add(self, vk_id):
        command = 'SELECT * FROM real_users WHERE vk_id = {0}'.format(vk_id)
        self.cursor.execute(command)

        data = self.cursor.fetchone()
        if data != None:
            return False

        command = "INSERT INTO users (type, session, phase) VALUES ('{0}', '{1}', {2})".format('real', 'default', 0)
        self.cursor.execute(command)
        user_id = self.cursor.lastrowid

        command = "INSERT INTO real_users (vk_id, user_id) VALUES ({0}, {1})".format(vk_id, user_id)
        self.cursor.execute(command)
        return True

#Debug users tables
    def is_debug_user(self, user_id):
        command = "SELECT name FROM debug_users WHERE user_id = {0}".format(user_id)
        self.cursor.execute(command)

        data = self.cursor.fetchone()
        if data != None:
            return data[0]
        else:
            return None

    def debug_user_get(self, name):
        command = "SELECT * FROM debug_users WHERE name = '{0}'".format(name)
        self.cursor.execute(command)

        data = self.cursor.fetchone()

        if data == None:
            return None
        return {'name' : data[0], 'user_id' : data[1]}

    def debug_users_get(self):
        command = "SELECT * FROM debug_users"
        self.cursor.execute(command)

        data = self.cursor.fetchall()

        res = []
        for item in data:
            res.append({'name' : item[0], 'user_id' : item[1]})
        return res

    def debug_users_add(self, name):
        command = "SELECT * FROM debug_users WHERE name = '{0}'".format(name)
        self.cursor.execute(command)

        data = self.cursor.fetchone()

        print("Adding debug user, data:", data)
        if data != None:
            return False
        print("Adding debug user, success:", name, type(name))
        
        command = "INSERT INTO users (type, session, phase) VALUES ('{0}', '{1}', {2})".format('debug', 'default', 0)
        print(self.cursor.execute(command))
        user_id = self.cursor.lastrowid
        print("id:", user_id)

        command = "INSERT INTO debug_users (user_id, name) VALUES ({0}, '{1}')".format(user_id, name)
        print(self.cursor.execute(command))
        return True

    def debug_messages_add(self, debug_user_name, type, text):
        command = "INSERT INTO debug_messages (debug_user_name, type, text) VALUES ('{0}', '{1}', '{2}')".format(debug_user_name, type, text)        
        self.cursor.execute(command)
        return

    def debug_messages_get(self, debug_user_name):
        command = "SELECT * FROM debug_messages WHERE debug_user_name = '{0}'".format(debug_user_name)
        self.cursor.execute(command)

        data = self.cursor.fetchall()
        res = []
        for item in data:
            res.append({'debug_user_name' : item[1],
                'type' : item[2],
                'text' : item[3]})
        return res

#List table
    def list_erase(self, user_id):
        command = 'DELETE FROM list WHERE user_id={0}'.format(user_id)
        self.cursor.execute(command)
        return

    def list_push_back(self, user_id, type, value):
        command = "INSERT INTO list (user_id, type, num, text) VALUES ({0}, '{1}', {2}, '{3}')"

        if type == 'num':
            command = command.format(user_id, type, value, '')
        elif type == 'text':
            command = command.format(user_id, type, 0, value)
        else:
            return

        self.cursor.execute(command)
        return

    def list_get(self, user_id):
        command = 'SELECT type, num, text FROM list WHERE user_id = {0} ORDER BY id'.format(user_id)
        self.cursor.execute(command)

        data = self.cursor.fetchall()
        res = []
        for value in data:
            if value[0] == 'num':
                res.append(value[1])
            elif value[0] == 'text':
                res.append(value[2])
        return res


