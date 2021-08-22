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
        command = 'CREATE TABLE IF NOT EXISTS sessions (\
                                        user_id INT PRIMARY KEY,\
                                        session VARCHAR(255) NOT NULL,\
                                        phase INT NOT NULL)'
        self.cursor.execute(command)
        command = 'CREATE TABLE IF NOT EXISTS list (\
                                        id INT PRIMARY KEY AUTO_INCREMENT,\
                                        user_id INT NOT NULL,\
                                        type INT NOT NULL,\
                                        intgr INT NOT NULL,\
                                        strng VARCHAR(255) NOT NULL\
                                        )'
        self.cursor.execute(command)

    def get_session(self, user_id):
        command = 'SELECT session, phase FROM sessions WHERE user_id = {0}'.format(user_id)

        self.cursor.execute(command)

        data = self.cursor.fetchone()
        if data == None:
            command = "INSERT INTO sessions (user_id, session, phase) VALUES ({0}, '{1}', {2})".format(user_id, 'default', 0)
            self.cursor.execute(command)
            return ('default', 0)
        return (data[0], data[1])

    def update_session(self, user_id, session, phase):
        command = "UPDATE sessions SET session = '{0}', phase = {1} WHERE user_id = {2}".format(session, phase, user_id)

        self.cursor.execute(command)

    def list_erase(self, user_id):
        command = 'DELETE FROM list WHERE user_id = {0}'.format(user_id)
        self.cursor.execute(command)

    def list_push_back(self, user_id, type, value):
        command = "INSERT INTO list (user_id, type, intgr, strng) VALUES ({0}, {1}, {2}, '{3}')"

        if type == 0:
            command = command.format(user_id, type, value, '')
        else:
            command = command.format(user_id, type, 0, value)

        self.cursor.execute(command)

    def list_get(self, user_id):
        command = 'SELECT type, intgr, strng FROM list WHERE user_id = {0} ORDER BY id'.format(user_id)

        self.cursor.execute(command)
        data = self.cursor.fetchall()

        res = []
        for value in data:
            if value[0] == 0:
                res.append(value[1])
            else:
                res.append(value[2])
        return res


