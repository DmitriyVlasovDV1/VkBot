import pymysql
import pymysql.cursors
import bot_settings

def parameters(arr, gap=', '):
    return gap.join(arr)

def arguments(arr, gap=', '):
    return gap.join(map(lambda x: repr(x), arr))

def assignments(element, gap=', '):
    return gap.join(map(lambda x: f"{x} = {repr(element[x])}", element))

class database:
    def __init__(self):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command = 'CREATE TABLE IF NOT EXISTS users (\
                                                id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                                                type VARCHAR(255) NOT NULL,\
                                                session VARCHAR(255) NOT NULL,\
                                                phase INT NOT NULL)'
                cursor.execute(command)

                command = 'CREATE TABLE IF NOT EXISTS real_users (\
                                                vk_id INT PRIMARY KEY,\
                                                user_id INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'    
                cursor.execute(command)

                command = 'CREATE TABLE IF NOT EXISTS debug_users (\
                                                name VARCHAR(255) PRIMARY KEY,\
                                                user_id INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'    
                cursor.execute(command)

                command = 'CREATE TABLE IF NOT EXISTS debug_messages (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                debug_user_name VARCHAR(255),\
                                                type VARCHAR(255),\
                                                text VARCHAR(255),\
                                                date DATETIME,\
                                                FOREIGN KEY (debug_user_name) REFERENCES debug_users (name) ON DELETE CASCADE)'    
                cursor.execute(command)

                command = 'CREATE TABLE IF NOT EXISTS list (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                user_id INT,\
                                                type VARCHAR(255),\
                                                num INT,\
                                                text VARCHAR(255),\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
                cursor.execute(command)

                command = 'CREATE TABLE IF NOT EXISTS account (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                user_id INT,\
                                                name VARCHAR(255),\
                                                age INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'
                cursor.execute(command)

                command = 'CREATE TABLE IF NOT EXISTS storage (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                type VARCHAR(255),\
                                                num INT,\
                                                text VARCHAR(255))'
                cursor.execute(command)

                command = 'CREATE TABLE IF NOT EXISTS mailing (\
                                                id INT PRIMARY KEY AUTO_INCREMENT,\
                                                user_id INT,\
                                                storage_id INT,\
                                                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,\
                                                FOREIGN KEY (storage_id) REFERENCES storage (id) ON DELETE CASCADE)'
                cursor.execute(command)
            connection.commit()

    
    def get_connection(self):
        return pymysql.connect(
            host=bot_settings.DB_HOST,
            user=bot_settings.DB_USER,
            password=bot_settings.DB_PASSWORD,
            database=bot_settings.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor)

    def add_one(self, table_name, element={}):
        id = -1
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                command = f"INSERT IGNORE INTO { table_name } ({ parameters(list(element.keys())) }) VALUES ({ arguments(list(element.values())) })"
                cursor.execute(command)
                id = cursor.lastrowid
            connection.commit()
        return id

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
        return None

    def is_one(self, table_name, element={}):
        return self.get_one(table_name, element) != None
    
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

 
db = database()