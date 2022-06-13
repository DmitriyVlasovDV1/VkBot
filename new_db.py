from main import db


##########
# Columns
##########

# all users (debug or not)
# id: self id | type: ???(debug or not) | session: current session
# phase: current phase in current session
class Users(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    type = db.Column(db.String(255), nullable=False)
    session = db.Column(db.String(255), nullable=False)
    phase = db.Column(db.Integer, nullable=False)

# vk users
# vk_id: vk id (and self id) | user_id: common user id
class RealUsers(db.Model):
    vk_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# debug users
# name: usersname (unique!) | user_id: common user id
class DebugUsers(db.Model):
    name = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# id: self id | debug_user_name: debug user name | type: bot / user |
# text: content text | date: sending date
class DebugMessages(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    debug_user_name = db.Column(db.String(255), db.ForeignKey('debug_users.name'))
    type = db.Column(db.String(255))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime)


# list with tmp values for session questionnaire
# id: self id | user_id: id of vk user | type ('num' or 'text') |
# text: content text | link for user (debug or not)
class List(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(255))
    num = db.Column(db.Integer)
    text = db.Column(db.Text)

# user accout data
# id: self id | user_id: id of vk user |
# name: owners name | age: owners age
class Account(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(255))
    age = db.Column(db.Integer)

# storage for data (texts or numbers)
# id: self id | type: 'num' or 'text' |
# text: content text
class Storage(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    type = db.Column(db.String(255))
    num = db.Column(db.Integer)
    text = db.Column(db.Text)

# mailings (group of messages for mailing)
# id: self id |  num: number in mailing list |
# name: name of mailing | is_active: sending msgs or not
class Mailings(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    num = db.Column(db.Integer)
    name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)

# messages for mailing
# id: self id | mailing_id: id for mailing | is_active: will be sended or not |
# name: name of msg | text: text content | time: sending time
class MailingMessages(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    mailing_id = db.Column(db.Integer, db.ForeignKey('mailings.id'))
    is_active = db.Column(db.Boolean)
    name = db.Column(db.String(255))
    text = db.Column(db.Text)
    time = db.Column(db.DateTime)


# double link for users and thier mailings
# id: self id | user_id: id of vk user | mailing_id: id of mailing
class MailingAndUser(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    mailing_id = db.Column(db.Integer, db.ForeignKey('mailings.id'))


#########
# Utils
#########

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d

####################
# Database wrapper
####################


class DBWrapper():
    def __init__(self, db):
        self.db = db

    # add one 'element' record in table
    def add_one(self, table, value):
        try:
            element = table(**value)
            self.db.session.add(element)
            self.db.session.commit()
            return element.id
        except:
            self.db.session.rollback()
            return -1

    # get all records in 'table' table with 'template' template
    def get_all(self, table, template={}):
        try:
            res = self.db.session.query(table).filter_by(**template).all()
            res = [row2dict(x) for x in res]
            return res
        except:
            return []

    # get one record in 'table' table with 'template' template
    def get_one(self, table, template={}):
        try:
            res = self.db.session.query(table).filter_by(**template).first()
            if res != None:
                res = row2dict(res)
            return res
        except:
            return None

    # check is any 'template' record in 'table' table
    def is_one(self, table, template={}):
        return self.get_one(table, template) is not None

    # change 'value' values in all records in 'table' table with 'template' template
    def update_all(self, table, value, template={}):
        if len(value) == 0:
            return

        try:
            self.db.session.query(table).filter_by(**template).update(value)
        except:
            pass

    # delete all records in 'table' table with 'element' template
    def delete_all(self, table, template={}):
        try:
            self.db.session.query(table).filter_by(**template).delete(synchronize_session=False)
            self.db.session.commit()
        except Exception as e:
            print(e)
            self.db.session.rollback()
            pass


'''
# fill 'field_name' field with numbers  0..n in 'element' template records
def numerate_all(self, table_name, field_name='num', element={}):
    with self.connection as connection:
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
'''