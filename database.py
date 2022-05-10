import pymysql
import pymysql.cursors
import bot_settings

# parsing data functions
def parameters(arr, gap=', '):
    return gap.join(arr)

def arguments(arr, gap=', '):
    return gap.join(map(lambda x: repr(x), arr))

def assignments(element, gap=', '):
    return gap.join(map(lambda x: f"{x} = {repr(element[x])}", element))

# database class
class database:
    def __init__(self):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:

                # create db if not exists

                # all users (debug or not)
                # id: self id | type: ???(debug or not) | session: current session
                # phase: current phase in current session
                command = 'CREATE TABLE IF NOT EXISTS users (\
                                                id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                                                type VARCHAR(255) NOT NULL,\
                                                session VARCHAR(255) NOT NULL,\
                                                phase INT NOT NULL)'
                cursor.execute(command)

                # vk users
                # vk_id: vk id (and self id) | user_id: common user id
                command = 'CREATE TABLE IF NOT EXISTS real_users (\
                                                vk_id INT PRIMARY KEY,\
                                                user_id INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
                cursor.execute(command)

                # debug users
                # name: usersname (unique!) | user_id: common user id
                command = 'CREATE TABLE IF NOT EXISTS debug_users (\
                                                name VARCHAR(255) PRIMARY KEY,\
                                                user_id INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
                cursor.execute(command)

                # id: self id | debug_user_name: debug user name | type: type of ??? |
                # text: content text | date: sending date
                command = 'CREATE TABLE IF NOT EXISTS debug_messages (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                debug_user_name VARCHAR(255),\
                                                type VARCHAR(255),\
                                                text TEXT,\
                                                date DATETIME,\
                                                FOREIGN KEY (debug_user_name) REFERENCES debug_users (name) ON DELETE CASCADE)'
                cursor.execute(command)

                # list with tmp values for session questionnaire
                # id: self id | user_id: id of vk user | type ('num' or 'text') |
                # text: content text | link for user (debug or not)
                command = 'CREATE TABLE IF NOT EXISTS list (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                user_id INT,\
                                                type VARCHAR(255),\
                                                num INT,\
                                                text TEXT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
                cursor.execute(command)

                # user accout data
                # id: self id | user_id: id of vk user |
                # name: owners name | age: owners age
                command = 'CREATE TABLE IF NOT EXISTS account (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                user_id INT,\
                                                name VARCHAR(255),\
                                                age INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
                cursor.execute(command)

                # storage for data (texts or numbers)
                # id: self id | type: 'num' or 'text' |
                # text: content text
                command = 'CREATE TABLE IF NOT EXISTS storage (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                type VARCHAR(255),\
                                                num INT,\
                                                text TEXT)'
                cursor.execute(command)

                # mailings (group of messages for mailing)
                # id: self id |  num: number in mailing list |
                # name: name of mailing | is_active: sending msgs or not
                command = 'CREATE TABLE IF NOT EXISTS mailings (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                num INT,\
                                                name VARCHAR(255),\
                                                is_active BOOL)'
                cursor.execute(command)

                # messages for mailing
                # id: self id | mailing_id: id for mailing | is_active: will be sended or not |
                # name: name of msg | text: text content | time: sending time
                command = 'CREATE TABLE IF NOT EXISTS mailing_messages (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                mailing_id INT,\
                                                is_active BOOL,\
                                                name VARCHAR(255), \
                                                text TEXT,\
                                                time DATETIME,\
                                                FOREIGN KEY (mailing_id) REFERENCES mailings (id) ON DELETE CASCADE)'
                cursor.execute(command)

                # double link for users and thier mailings
                # id: self id | user_id: id of vk user | mailing_id: id of mailing
                command = 'CREATE TABLE IF NOT EXISTS mailing_and_user (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                user_id INT,\
                                                mailing_id INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,\
                                                FOREIGN KEY (mailing_id) REFERENCES mailings (id) ON DELETE CASCADE)'
                cursor.execute(command)
            connection.commit()


    # try connect to db
    def get_connection(self):
        return pymysql.connect(
            host=bot_settings.DB_HOST,
            user=bot_settings.DB_USER,
            password=bot_settings.DB_PASSWORD,
            database=bot_settings.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor)

    # add one 'element' record in 'table_name' table
    def add_one(self, table_name, element={}):
        id = -1
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command = f"INSERT IGNORE INTO { table_name } ({ parameters(list(element.keys())) }) VALUES ({ arguments(list(element.values())) })"
                cursor.execute(command)
                id = cursor.lastrowid
            connection.commit()
        return id

    # get all records in 'table_name' table with 'element' template
    def get_all(self, table_name, element={}):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command = f"SELECT * FROM { table_name }"
                if len(element) != 0:
                    command += " WHERE "
                    command += assignments(element, " AND ")

                cursor.execute(command)
                return cursor.fetchall()
        return []

    # get one record in 'table_name' table with 'element' template
    def get_one(self, table_name, element={}):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command = f"SELECT * FROM { table_name }"
                if len(element) != 0:
                    command += " WHERE "
                    command += assignments(element, " AND ")
                command += " LIMIT 1"

                cursor.execute(command)
                return cursor.fetchone()
        return

    # check is any 'element' record in 'table_name' table
    def is_one(self, table_name, element={}):
        return self.get_one(table_name, element) != None

    # change 'value' values in all records in 'table_name' table with 'element' template
    def update_all(self, table_name, value, element={}):
        if len(value) == 0:
            return
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command = f"UPDATE { table_name } SET { assignments(value) }"
                if len(element) != 0:
                    command += " WHERE "
                    command += assignments(element, " AND ")

                cursor.execute(command)
            connection.commit()
        return

    # delete all records in 'table_name' table with 'element' template
    def delete_all(self, table_name, element={}):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command = f"DELETE FROM { table_name }"
                if len(element) != 0:
                    command += " WHERE "
                    command += assignments(element, " AND ")

                cursor.execute(command)
            connection.commit()
        return

    # fill 'field_name' field with numbers  0..n in 'element' template records
    def numerate_all(self, table_name, field_name='num', element={}):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command1 = f"SET @row_num := 0"
                command2 = f"UPDATE { table_name } SET { field_name } = (@row_num := @row_num + 1)"
                if len(element) != 0:
                    command2 += " WHERE "
                    command2 += assignments(element, " AND ")

                cursor.execute(command1)
                cursor.execute(command2)
            connection.commit()
        return


# create database instance
db = database()